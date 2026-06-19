@echo off
REM Build Desktop Pet → DesktopPet.exe (Windows)
REM รันไฟล์นี้บน Windows เท่านั้น

cd /d "%~dp0"

pip install pyinstaller --quiet

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name "DesktopPet" ^
  --add-data "sprites;sprites" ^
  --hidden-import "webview.platforms.winforms" ^
  --hidden-import "PIL._tkinter_finder" ^
  desktop_pet.py

echo.
echo Done! EXE is at: dist\DesktopPet\DesktopPet.exe
pause
