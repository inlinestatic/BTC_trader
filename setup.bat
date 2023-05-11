@echo off

REM Check if Python is already installed
where python > nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed. Skipping installation.
) else (
    echo Downloading Python installer...
    curl -L https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe -o python_installer.exe -k

    echo Installing Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1

    echo Cleaning up...
    del python_installer.exe

    echo Python has been installed successfully!
)

REM Check if MongoDB is already installed
where mongod > nul 2>&1
if %errorlevel% equ 0 (
    echo MongoDB is already installed. Skipping installation.
) else (
    REM Define the MongoDB version
    set MONGODB_VERSION=4.4.5

    REM Define the MongoDB installation directory
    set MONGODB_DIR=C:\mongodb

    REM Create the MongoDB installation directory
    mkdir %MONGODB_DIR%

    REM Download MongoDB (with insecure option)
    curl -o %MONGODB_DIR%\mongodb.zip --insecure https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-4.0.28.zip
	
    REM Extract MongoDB
    tar -xf %MONGODB_DIR%\mongodb.zip -C %MONGODB_DIR%

    REM Rename the extracted directory
    ren %MONGODB_DIR%\mongodb-win32-x86_64-2008plus-ssl-4.0.28 %MONGODB_DIR%\mongodb

    REM Clean up the downloaded zip file
    del %MONGODB_DIR%\mongodb.zip

    REM Add MongoDB to the system PATH
    setx /M PATH "%PATH%;%MONGODB_DIR%\mongodb\bin"

    echo MongoDB %MONGODB_VERSION% has been installed successfully!

    REM Cleanup downloaded and extracted files
    RD /S /Q %MONGODB_DIR%\mongodb
)

echo Done.
pause
