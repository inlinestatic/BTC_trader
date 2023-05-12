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
    set MONGODB_VERSION=4.0.28

    REM Define the MongoDB installation directory
    set MONGODB_DIR=C:\mongodb

    REM Create the MongoDB installation directory
    mkdir %MONGODB_DIR%
    mkdir %MONGODB_DIR%\data
    REM Download MongoDB (with insecure option)
    curl -o %MONGODB_DIR%\mongodb.zip --insecure https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-4.0.28.zip
	
    REM Extract MongoDB
    tar -xf %MONGODB_DIR%\mongodb.zip -C %MONGODB_DIR%

    REM Rename the extracted directory
    xcopy %MONGODB_DIR%\mongodb-win32-x86_64-2008plus-ssl-4.0.28\mongodb  %MONGODB_DIR%\mongodb /E /I 

    REM Clean up the downloaded zip file
    del %MONGODB_DIR%\mongodb.zip
    rmdir /s /q %MONGODB_DIR%\mongodb-win32-x86_64-2008plus-ssl-4.0.28
	
	REM Define the variable value
	set NEW_PATH=%MONGODB_DIR%\mongodb\bin
	
	REM Add the variable to the PATH in the registry
	reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "%PATH%;%NEW_PATH%" /f

    echo MongoDB %MONGODB_VERSION% has been installed successfully!

    REM Configure MongoDB as a service
    echo Configuring MongoDB as a service...
    %MONGODB_DIR%\bin\mongod.exe --install --serviceName "MongoDB" --serviceDisplayName "MongoDB" --serviceDescription "MongoDB Server" --dbpath "C:\mongodb\data" --logpath "C:\mongodb\mongo.log"
    echo MongoDB service has been configured successfully!

    REM Start the MongoDB service
    echo Starting MongoDB service...
    net start MongoDB

    echo MongoDB service has been started!
)

echo Done.
pause
