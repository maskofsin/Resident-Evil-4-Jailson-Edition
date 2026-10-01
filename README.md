# Resident Evil 4 - Jailson Edition

![Resident Evil 4 - Jailson Edition](https://raw.githubusercontent.com/maskofsin/Resident-Evil-4-Jailson-Edition/main/re4je.png)

A fan-made texture and audio mod for **Resident Evil 4 on Zeebo**, featuring Jailson Mendes, Paulo Guina and Pai de Família references.

**This project distributes a patch only. You must supply your own original game ZIP. No original ROM or complete modified game is included.**

## Download and apply

Download **[RE4_Jailson_Edition_v99_patch.zip](https://github.com/maskofsin/Resident-Evil-4-Jailson-Edition/releases/download/v99-patch/RE4_Jailson_Edition_v99_patch.zip)** from the [release page](https://github.com/maskofsin/Resident-Evil-4-Jailson-Edition/releases/tag/v99-patch) and extract it into a new folder.

You need **Python 3.10 or newer** with its standard library. No pip packages, emulator or internet connection are needed to apply the patch.

On Windows, put your original `Resident Evil 4 - Zeebo Edition.zip` beside `Apply_Patch.cmd`, then double-click the CMD. Alternatively, drag your original ZIP onto the CMD.

From a terminal in the extracted patch folder:

```powershell
py -3 apply_patch.py "C:\path\to\Resident Evil 4 - Zeebo Edition.zip"
```

On Linux/macOS:

```sh
python3 apply_patch.py "/path/to/Resident Evil 4 - Zeebo Edition.zip"
```

The result is `RE4_Jailson_v99_OCO001.zip` in the current folder. Open that ZIP with your Zeebx emulator. The original is kept intact. An existing output is never overwritten; use `--output "another-name.zip"` if necessary.

Keep `apply_patch.py` and `Jailson_Edition_v99.re4patch` together. The repository's ZIP download is the source repository; use the release asset above for the ready-to-apply package.

## Required original

Supported source: the **unmodified Zeebo edition**, containing `mif/276675.mif` and the 16 original files under `mod/276675/`, directly at the ZIP root. Android, iOS, PC, console editions and previously modified Zeebo builds are incompatible.

Reference original ZIP SHA-256:

```text
dd740a2a7df280c10e2db717eb5852d2025bc95cb3c60a167181e972298cb01e
```

Recompressed copies work if all 17 required internal files are identical. Each original file is checked by size and SHA-256 before output is created; their expected hashes are in the patch bundle's `manifest.json`. A mismatch stops the operation. Extra files, such as an existing save, are ignored and are not transferred to the new package.

## Included in v99

- Jailson's player face and repaired head texture; Paulo Guina enemy textures.
- Jailson's face on Ashley, retaining her blonde hair.
- Custom voices at normal playback speed, including four random variations for each of events 1 and 10, selected by the game itself. A later event can interrupt a voice.
- Jailson title screen and large game icon.
- Jailson faces in 26 story/ending images. Rear views without a visible face retain their original appearance.
- Separate identity: **OCO001**, package folder **900001**, BREW ClassID **0x4F434F31**.

The package retains the bundled v99 save payload. Existing external saves/profiles are not migrated; the new identity may use separate storage.

## Patch and verification

`Jailson_Edition_v99.re4patch` is a ZIP container with a manifest and **BSDIFF40 binary deltas for uncompressed internal files**. Sixteen files are changed or added, and two unchanged files are copied from your original. It is not a standalone ROM and cannot be applied directly with a single-file ROM patcher. The included Python applicator handles the paths, checksums and ZIP rebuilding.

The patch was generated with [bsdiff4](https://github.com/ilanschnell/bsdiff4). The included applicator uses only Python's standard library; bsdiff4 is not a user dependency.

Applying the released patch to the reference original produced the exact previously tested v99 ZIP:

```text
1fc6a61e22259768e98192efc31482daafe3e60b24554b873006b4bf272a80a7
```

All 18 reconstructed game files and ZIP CRCs are verified. Tests also covered a recompressed/reordered original, rejection of an altered ROM and corrupt delta, preservation of an existing output, and 24 comparisons against the independent bsdiff4 applicator. Different Python/zlib builds may produce different ZIP compression bytes; the applicator always requires every game payload to match v99 exactly.

The v99 game passed opening and initial-combat checks in the unchanged official Zeebx 0.4.1 emulator. All edited story images were inspected. A complete playthrough of every chapter and physical Zeebo hardware testing remain pending.

The downloadable archive contains only the patch, applicator, Windows launcher, instructions and checksums. The repository also retains the previously published project artwork.
