@echo off
echo Downloading Python installer...
curl -L https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe -o python_installer.exe -k

echo Installing Python...
python_installer.exe /quiet InstallAllUsers=1 PrependPath=1

echo Downloading get-pip.py script...
curl -L https://bootstrap.pypa.io/get-pip.py -o get-pip.py

echo Installing pip...
python get-pip.py

echo Cleaning up...
del python_installer.exe
del get-pip.py

echo installing requirements
pip install --default-timeout=30 -r requirements.txt

echo Done.
pause
