@echo off
setlocal
pushd "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 "%~dp0apply_patch.py" %*
goto finished
:use_python
python "%~dp0apply_patch.py" %*
:finished
set "patch_result=%errorlevel%"
if not "%patch_result%"=="0" echo Install Python 3.10 or newer if it is missing, and check the error above.
pause
popd
exit /b %patch_result%
