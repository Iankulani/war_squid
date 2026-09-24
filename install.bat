@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM WAR-SQUID-V1 - Windows Batch Installation Script
REM Author: Ian Carter Kulani
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal EnableDelayedExpansion

REM Configuration
set "VERSION=1.0.0"
set "NAME=WAR-SQUID-V1"
set "INSTALL_DIR=%ProgramFiles%\WAR-SQUID"
set "PYTHON_MIN_VERSION=3.8"

REM Colors (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "WHITE=[97m"
set "BOLD=[1m"
set "NC=[0m"

REM Title
title WAR-SQUID-V1 Installation

echo.
echo %CYAN%╔══════════════════════════════════════════════════════════════════════════════╗%NC%
echo %CYAN%║                                                                              ║%NC%
echo %CYAN%║  ██╗    ██╗ █████╗ ██████╗       ███████╗ ██████╗ ██╗   ██╗██╗██████╗        ║%NC%
echo %CYAN%║  ██║    ██║██╔══██╗██╔══██╗      ██╔════╝██╔═══██╗██║   ██║██║██╔══██╗       ║%NC%
echo %CYAN%║  ██║ █╗ ██║███████║██████╔╝█████╗███████╗██║   ██║██║   ██║██║██║  ██║       ║%NC%
echo %CYAN%║  ██║███╗██║██╔══██║██╔══██╗╚════╝╚════██║██║▄▄ ██║██║   ██║██║██║  ██║       ║%NC%
echo %CYAN%║  ╚███╔███╔╝██║  ██║██║  ██║      ███████║╚██████╔╝╚██████╔╝██║██████╔╝       ║%NC%
echo %CYAN%║   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝      ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═════╝        ║%NC%
echo %CYAN%║                                                                              ║%NC%
echo %CYAN%║                    WAR-SQUID-V1 - Installation Script                       ║%NC%
echo %CYAN%║                         Author: Ian Carter Kulani                            ║%NC%
echo %CYAN%║                                                                              ║%NC%
echo %CYAN%╚══════════════════════════════════════════════════════════════════════════════╝%NC%
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo %RED%[✗] This script requires Administrator privileges.%NC%
    echo %YELLOW%    Please right-click and select "Run as Administrator"%NC%
    pause
    exit /b 1
)
echo %GREEN%[✓]%NC% Running with Administrator privileges

REM Check Python
echo %BLUE%[INFO]%NC% Checking Python installation...

where python >nul 2>&1
if %errorLevel% neq 0 (
    where python3 >nul 2>&1
    if %errorLevel% neq 0 (
        echo %RED%[✗] Python is not installed or not in PATH.%NC%
        echo %YELLOW%    Please install Python %PYTHON_MIN_VERSION%+ from https://python.org%NC%
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python3"
) else (
    set "PYTHON_CMD=python"
)

REM Check Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo %GREEN%[✓]%NC% Found Python %PYTHON_VERSION%

REM Check pip
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[⚠]%NC% pip not found. Installing...
    %PYTHON_CMD% -m ensurepip --upgrade
)
echo %GREEN%[✓]%NC% pip is available

REM Create installation directory
echo %BLUE%[INFO]%NC% Creating installation directory...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)
echo %GREEN%[✓]%NC% Created %INSTALL_DIR%

REM Copy application files
echo %BLUE%[INFO]%NC% Copying application files...
xcopy /E /I /Y "%~dp0\*" "%INSTALL_DIR%\" >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[⚠]%NC% Some files may not have been copied
)
echo %GREEN%[✓]%NC% Application files copied

REM Create virtual environment
echo %BLUE%[INFO]%NC% Creating virtual environment...
%PYTHON_CMD% -m venv "%INSTALL_DIR%\venv"
if %errorLevel% neq 0 (
    echo %RED%[✗] Failed to create virtual environment%NC%
    pause
    exit /b 1
)
echo %GREEN%[✓]%NC% Virtual environment created

REM Upgrade pip
echo %BLUE%[INFO]%NC% Upgrading pip...
"%INSTALL_DIR%\venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo %GREEN%[✓]%NC% pip upgraded

REM Install dependencies
echo %BLUE%[INFO]%NC% Installing Python dependencies...
echo %YELLOW%    This may take several minutes...%NC%
"%INSTALL_DIR%\venv\Scripts\pip.exe" install -r "%INSTALL_DIR%\requirements.txt"
if %errorLevel% neq 0 (
    echo %RED%[✗] Failed to install dependencies%NC%
    echo %YELLOW%    Trying with --no-cache-dir...%NC%
    "%INSTALL_DIR%\venv\Scripts\pip.exe" install --no-cache-dir -r "%INSTALL_DIR%\requirements.txt"
)
echo %GREEN%[✓]%NC% Dependencies installed

REM Create configuration directory
echo %BLUE%[INFO]%NC% Creating configuration...
if not exist "%INSTALL_DIR%\.war_squid_v1" (
    mkdir "%INSTALL_DIR%\.war_squid_v1"
)
if not exist "%INSTALL_DIR%\war_squid_reports" (
    mkdir "%INSTALL_DIR%\war_squid_reports"
)
if not exist "%INSTALL_DIR%\temp" (
    mkdir "%INSTALL_DIR%\temp"
)
echo %GREEN%[✓]%NC% Configuration created

REM Create CLI wrapper
echo %BLUE%[INFO]%NC% Creating CLI wrapper...

set "WRAPPER=%INSTALL_DIR%\war-squid.bat"
(
echo @echo off
echo REM WAR-SQUID-V1 CLI Wrapper
echo.
echo set "INSTALL_DIR=%INSTALL_DIR%"
echo.
echo if not exist "%%INSTALL_DIR%%\venv\Scripts\python.exe" ^(
echo     echo Error: Virtual environment not found
echo     exit /b 1
echo ^)
echo.
echo "%%INSTALL_DIR%%\venv\Scripts\python.exe" "%%INSTALL_DIR%%\war_squid.py" %%*
) > "%WRAPPER%"

echo %GREEN%[✓]%NC% CLI wrapper created

REM Add to PATH
echo %BLUE%[INFO]%NC% Adding to PATH...
setx PATH "%PATH%;%INSTALL_DIR%" /M >nul 2>&1
echo %GREEN%[✓]%NC% Added to system PATH

REM Create uninstaller
echo %BLUE%[INFO]%NC% Creating uninstaller...

set "UNINSTALLER=%INSTALL_DIR%\uninstall.bat"
(
echo @echo off
echo REM WAR-SQUID-V1 Uninstaller
echo.
echo echo Uninstalling WAR-SQUID-V1...
echo.
echo REM Remove from PATH
echo setx PATH "%%PATH:%INSTALL_DIR%;=%%" /M ^>nul 2^>^&1
echo.
echo REM Remove installation directory
echo rmdir /S /Q "%INSTALL_DIR%"
echo.
echo echo WAR-SQUID-V1 has been uninstalled.
echo pause
) > "%UNINSTALLER%"

echo %GREEN%[✓]%NC% Uninstaller created

REM Create desktop shortcut
echo %BLUE%[INFO]%NC% Creating desktop shortcut...

set "SHORTCUT=%USERPROFILE%\Desktop\WAR-SQUID.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%INSTALL_DIR%\war-squid.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'WAR-SQUID-V1'; $s.Save()" >nul 2>&1

echo %GREEN%[✓]%NC% Desktop shortcut created

REM Firewall rules
echo %BLUE%[INFO]%NC% Adding firewall rules...

netsh advfirewall firewall add rule name="WAR-SQUID Web" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
netsh advfirewall firewall add rule name="WAR-SQUID API" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1
netsh advfirewall firewall add rule name="WAR-SQUID Phishing" dir=in action=allow protocol=TCP localport=8080 >nul 2>&1
netsh advfirewall firewall add rule name="WAR-SQUID C2" dir=in action=allow protocol=TCP localport=4444 >nul 2>&1

echo %GREEN%[✓]%NC% Firewall rules added

REM Summary
echo.
echo %GREEN%╔══════════════════════════════════════════════════════════════════════╗%NC%
echo %GREEN%║                    Installation Complete!                            ║%NC%
echo %GREEN%╚══════════════════════════════════════════════════════════════════════╝%NC%
echo.
echo %WHITE%Installation Details:%NC%
echo   %CYAN%Install Directory:%NC%  %INSTALL_DIR%
echo   %CYAN%Virtual Environment:%NC% %INSTALL_DIR%\venv
echo   %CYAN%CLI Wrapper:%NC%        %INSTALL_DIR%\war-squid.bat
echo   %CYAN%Uninstaller:%NC%        %INSTALL_DIR%\uninstall.bat
echo.
echo %WHITE%Usage:%NC%
echo   %GREEN%Run application:%NC%   war-squid
echo   %GREEN%Run with args:%NC%     war-squid --help
echo.
echo %WHITE%Web Dashboard:%NC%
echo   %CYAN%URL:%NC%                http://localhost:5000
echo   %CYAN%Default Username:%NC%   admin
echo   %CYAN%Default Password:%NC%   war_squid_2024
echo.
echo %YELLOW%⚠  IMPORTANT: Change the default password immediately!%NC%
echo.
echo %WHITE%Uninstall:%NC%
echo   %RED%%INSTALL_DIR%\uninstall.bat%NC%
echo.

REM Ask to run
set /p RUN_NOW="Run WAR-SQUID now? (Y/N): "
if /i "%RUN_NOW%"=="Y" (
    start "" "%INSTALL_DIR%\war-squid.bat"
)

pause
endlocal
