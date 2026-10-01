"""Apply the Jailson Edition v99 per-file BSDIFF40 bundle. Python 3.10+, stdlib only."""
import argparse
import bz2
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def signed64(data):
    if len(data) != 8:
        raise ValueError("Truncated BSDIFF40 integer")
    value = int.from_bytes(data, "little")
    return -(value & ((1 << 63) - 1)) if value >> 63 else value


def apply_delta(source, patch, expected_size):
    """Decode the standard sign-magnitude control/difference/extra streams."""
    if patch[:8] != b"BSDIFF40" or len(patch) < 32:
        raise ValueError("Invalid BSDIFF40 patch")
    csize, dsize, size = (signed64(patch[i:i+8]) for i in (8, 16, 24))
    if min(csize, dsize, size) < 0 or size != expected_size or 32+csize+dsize > len(patch):
        raise ValueError("Invalid patch lengths")
    control = bz2.decompress(patch[32:32+csize])
    diff = bz2.decompress(patch[32+csize:32+csize+dsize])
    extra = bz2.decompress(patch[32+csize+dsize:])
    if len(control) % 24:
        raise ValueError("Invalid control stream")
    result = bytearray(size)
    old = new = dp = ep = 0
    for pos in range(0, len(control), 24):
        x, y, seek = (signed64(control[i:i+8]) for i in (pos, pos+8, pos+16))
        if min(x, y) < 0 or new+x+y > size or dp+x > len(diff) or ep+y > len(extra):
            raise ValueError("Invalid patch operation")
        result[new:new+x] = diff[dp:dp+x]
        for i in range(max(0, -old), min(x, len(source)-old)):
            result[new+i] = (result[new+i] + source[old+i]) & 255
        new += x
        old += x
        dp += x
        result[new:new+y] = extra[ep:ep+y]
        new += y
        ep += y
        old += seek
    if new != size or dp != len(diff) or ep != len(extra):
        raise ValueError("Incomplete patch or unused patch data")
    return bytes(result)


def rebuild(original_path, bundle_path):
    with zipfile.ZipFile(bundle_path) as bundle, zipfile.ZipFile(original_path) as original:
        manifest = json.loads(bundle.read("manifest.json"))
        if manifest["format"] != "jailson-per-file-bsdiff40-v1":
            raise ValueError("Unsupported bundle version")
        infos = original.infolist()
        if len({i.filename for i in infos}) != len(infos):
            raise ValueError("Original ZIP contains duplicate paths")
        source = {}
        # Validate every original payload before constructing any output.
        for name, expected in manifest["sources"].items():
            try:
                data = original.read(name)
            except KeyError:
                raise ValueError(f"Original ROM is missing {name}") from None
            if len(data) != expected["size"] or sha(data) != expected["sha256"]:
                raise ValueError(f"Original ROM version mismatch: {name}")
            source[name] = data
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for record in manifest["targets"]:
                data = source[record["source"]] if record["source"] else b""
                if record["patch"]:
                    patch = bundle.read(record["patch"])
                    if sha(patch) != record["patch_sha256"]:
                        raise ValueError(f"Patch checksum mismatch: {record['name']}")
                    data = apply_delta(data, patch, record["size"])
                if len(data) != record["size"] or sha(data) != record["sha256"]:
                    raise ValueError(f"Patched payload mismatch: {record['name']}")
                info = zipfile.ZipInfo(record["name"], tuple(record["zip"]["date_time"]))
                for key in ("compress_type", "create_system", "create_version", "extract_version",
                            "external_attr", "internal_attr"):
                    setattr(info, key, record["zip"][key])
                info.extra = bytes.fromhex(record["zip"]["extra"])
                info.comment = bytes.fromhex(record["zip"]["comment"])
                output.writestr(info, data, compresslevel=9)
            output.comment = bytes.fromhex(manifest["zip_comment"])
        result = buffer.getvalue()
        with zipfile.ZipFile(io.BytesIO(result)) as output:
            if output.testzip() is not None:
                raise ValueError("Output ZIP CRC check failed")
        return result, manifest


def main():
    parser = argparse.ArgumentParser(description="Create Jailson Edition from your original RE4 Zeebo ZIP.")
    parser.add_argument("original", nargs="?", type=Path, default=Path("Resident Evil 4 - Zeebo Edition.zip"))
    parser.add_argument("--patch", type=Path, default=Path(__file__).with_name("Jailson_Edition_v99.re4patch"))
    parser.add_argument("--output", type=Path, default=Path("RE4_Jailson_v99_OCO001.zip"))
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.resolve() == args.original.resolve():
            raise ValueError("Output already exists or points to the original. Choose a new --output path.")
        result, manifest = rebuild(args.original, args.patch)
        with args.output.open("xb") as output:
            output.write(result)
        digest = sha(result)
        print(f"Created: {args.output.resolve()}")
        print(f"Verified all {len(manifest['targets'])} v99 payloads and ZIP CRCs.")
        print(f"SHA256: {digest}")
        if digest == manifest["reference_target_zip_sha256"]:
            print("ZIP is byte-identical to the tested v99 release.")
        else:
            print("ZIP compression bytes differ on this Python/zlib build; all game payloads match v99 exactly.")
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, EOFError) as error:
        print(f"Patch failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
