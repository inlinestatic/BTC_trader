@echo off

set current_dir=%~dp0
push current_dir

set "json_file="
for %%f in (*.json) do (
    set "json_file=%%~ff"
    goto :found
)
:found

if not defined json_file (
    echo No JSON files found.
    pause
    exit /b
)

echo Found JSON file: %json_file%

set config=%current_dir%\BinanceCredentials.txt
echo Config: %config%
python Binance.py %json_file% %config%
pause