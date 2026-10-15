@echo off
rem ============================================================
rem  Builds the webcam companion (BlinkCompanion.exe) with PyInstaller,
rem  then copies it into the mod's folder so the next game launch uses it.
rem  Double-click this file to run it. Close Outer Wilds first.
rem ============================================================
setlocal

rem Work from the folder this file is in, wherever it's run from.
cd /d "%~dp0"

py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.12 isn't installed, or the "py" launcher can't find it.
    goto :failed
)

rem --- Step 1: the exact Python packages to build with ---
rem The first time, this records the versions installed on this PC, which you know work,
rem into requirements.txt. GitHub installs exactly these when it builds a release.
if not exist requirements.txt (
    echo Recording your Python package versions in requirements.txt...
    py -3.12 -m pip freeze > requirements.txt
    if errorlevel 1 goto :failed
) else (
    echo Making sure the packages in requirements.txt are installed...
    py -3.12 -m pip install --quiet --no-deps -r requirements.txt
    if errorlevel 1 goto :failed
)

rem --- Step 2: build ---
rem --clean starts from scratch. --noconfirm replaces the last build without asking.
echo Building BlinkCompanion (this takes a minute or two)...
py -3.12 -m PyInstaller --noconfirm --clean BlinkCompanion.spec
if errorlevel 1 goto :failed

rem --- Step 3: copy it into the mod's folder ---
set "MOD_FOLDER=%APPDATA%\OuterWildsModManager\OWML\Mods\Zra.QuantumBlink"
if not exist "%MOD_FOLDER%" (
    echo Built dist\BlinkCompanion. The mod's folder wasn't found, so it wasn't copied.
    goto :done
)

rem /MIR makes the copy match exactly, removing files left over from older builds.
robocopy "dist\BlinkCompanion" "%MOD_FOLDER%\BlinkCompanion" /MIR /NFL /NDL /NJH /NJS /NP
rem Robocopy's exit codes 0 to 7 all mean success. 8 or more means something failed.
if errorlevel 8 (
    echo Couldn't copy into the mod's folder. Is Outer Wilds still running?
    goto :failed
)
echo Copied into %MOD_FOLDER%\BlinkCompanion

:done
echo.
echo Done!
pause
exit /b 0

:failed
echo.
echo Something went wrong. See the messages above.
pause
exit /b 1
