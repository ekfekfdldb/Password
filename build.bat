@echo off
REM 가상환경에서 실행 가정: python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name MyVault app/main.py --paths .
echo Build done. See .\dist\MyVault.exe