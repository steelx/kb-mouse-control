@echo off
echo Cleaning up previous build...
if exist venv rmdir /s /q venv
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist kb-mouse.spec del kb-mouse.spec

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error installing requirements. Exiting.
    exit /b %errorlevel%
)

echo Building with PyInstaller...
pyinstaller --name="KB Mouse Control" ^
            --onefile ^
            --windowed ^
            --icon=app_icon.ico ^
            --add-data "app_icon.ico;." ^
            --version-file=version_info.txt ^
            main.py

if %errorlevel% neq 0 (
    echo Error building with PyInstaller. Exiting.
    exit /b %errorlevel%
)

echo Build successful. Executable should be in the dist folder.

echo Local build test complete.
echo Deactivating virtual environment...
deactivate

echo Done. Check the dist folder for the executable.
