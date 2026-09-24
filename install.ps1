# ═══════════════════════════════════════════════════════════════════════════════
# WAR-SQUID-V1 - PowerShell Installation Script
# Author: Ian Carter Kulani
# ═══════════════════════════════════════════════════════════════════════════════

#Requires -RunAsAdministrator

param(
    [string]$InstallDir = "$env:ProgramFiles\WAR-SQUID",
    [switch]$SkipDependencies,
    [switch]$SkipFirewall,
    [switch]$NoShortcut,
    [switch]$Force
)

# Set strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

$VERSION = "1.0.0"
$NAME = "WAR-SQUID-V1"
$PYTHON_MIN_VERSION = "3.8"
$VENV_DIR = "$InstallDir\venv"

# Color functions
function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                              ║" -ForegroundColor Cyan
    Write-Host "║  ██╗    ██╗ █████╗ ██████╗       ███████╗ ██████╗ ██╗   ██╗██╗██████╗        ║" -ForegroundColor Cyan
    Write-Host "║  ██║    ██║██╔══██╗██╔══██╗      ██╔════╝██╔═══██╗██║   ██║██║██╔══██╗       ║" -ForegroundColor Cyan
    Write-Host "║  ██║ █╗ ██║███████║██████╔╝█████╗███████╗██║   ██║██║   ██║██║██║  ██║       ║" -ForegroundColor Cyan
    Write-Host "║  ██║███╗██║██╔══██║██╔══██╗╚════╝╚════██║██║▄▄ ██║██║   ██║██║██║  ██║       ║" -ForegroundColor Cyan
    Write-Host "║  ╚███╔███╔╝██║  ██║██║  ██║      ███████║╚██████╔╝╚██████╔╝██║██████╔╝       ║" -ForegroundColor Cyan
    Write-Host "║   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝      ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═════╝        ║" -ForegroundColor Cyan
    Write-Host "║                                                                              ║" -ForegroundColor Cyan
    Write-Host "║                    WAR-SQUID-V1 - Installation Script                       ║" -ForegroundColor Cyan
    Write-Host "║                         Author: Ian Carter Kulani                            ║" -ForegroundColor Cyan
    Write-Host "║                                                                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[⚠] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "[✗] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALLATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Python {
    Write-Info "Checking Python installation..."
    
    $pythonCmd = $null
    
    # Try python
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    } catch {}
    
    # Try python3
    if (-not $pythonCmd) {
        try {
            $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        } catch {}
    }
    
    # Try py launcher
    if (-not $pythonCmd) {
        try {
            $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
        } catch {}
    }
    
    if (-not $pythonCmd) {
        Write-Error "Python is not installed or not in PATH."
        Write-Host "Please install Python $PYTHON_MIN_VERSION+ from https://python.org" -ForegroundColor Yellow
        return $null
    }
    
    # Get version
    $versionOutput = & $pythonCmd.Source --version 2>&1
    $version = $versionOutput -replace "Python ", ""
    
    Write-Success "Found Python $version"
    
    # Check minimum version
    $versionParts = $version.Split(".")
    $majorVersion = [int]$versionParts[0]
    $minorVersion = [int]$versionParts[1]
    
    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
        Write-Error "Python $PYTHON_MIN_VERSION+ is required. Found $version"
        return $null
    }
    
    return $pythonCmd.Source
}

function Install-PythonDependencies {
    param([string]$PythonPath)
    
    Write-Info "Installing Python dependencies..."
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    & $PythonPath -m pip install --upgrade pip setuptools wheel --quiet
    
    # Install requirements
    $requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
    
    if (Test-Path $requirementsFile) {
        Write-Info "Installing from requirements.txt..."
        & $PythonPath -m pip install -r $requirementsFile
    } else {
        Write-Warning "requirements.txt not found. Installing core packages..."
        & $PythonPath -m pip install requests psutil colorama cryptography flask paramiko scapy
    }
    
    Write-Success "Python dependencies installed"
}

function New-InstallDirectory {
    Write-Info "Creating installation directory..."
    
    if (Test-Path $InstallDir) {
        if ($Force) {
            Write-Warning "Removing existing installation..."
            Remove-Item -Path $InstallDir -Recurse -Force
        } else {
            Write-Warning "Installation directory already exists: $InstallDir"
            $response = Read-Host "Overwrite? (y/N)"
            if ($response -ne "y") {
                Write-Error "Installation cancelled."
                exit 1
            }
            Remove-Item -Path $InstallDir -Recurse -Force
        }
    }
    
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\.war_squid_v1" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\war_squid_reports" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallDir\temp" -Force | Out-Null
    
    Write-Success "Created $InstallDir"
}

function Copy-ApplicationFiles {
    Write-Info "Copying application files..."
    
    $sourceDir = $PSScriptRoot
    
    Get-ChildItem -Path $sourceDir -Exclude @("install.ps1", "install.bat", "install.sh") | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $InstallDir -Recurse -Force
    }
    
    Write-Success "Application files copied"
}

function New-VirtualEnvironment {
    param([string]$PythonPath)
    
    Write-Info "Creating virtual environment..."
    
    & $PythonPath -m venv $VENV_DIR
    
    if (-not (Test-Path "$VENV_DIR\Scripts\python.exe")) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    
    Write-Success "Virtual environment created"
}

function Install-VenvDependencies {
    Write-Info "Installing dependencies in virtual environment..."
    
    $venvPython = "$VENV_DIR\Scripts\python.exe"
    $venvPip = "$VENV_DIR\Scripts\pip.exe"
    
    # Upgrade pip
    & $venvPython -m pip install --upgrade pip setuptools wheel --quiet
    
    # Install requirements
    $requirementsFile = Join-Path $InstallDir "requirements.txt"
    
    if (Test-Path $requirementsFile) {
        Write-Info "This may take several minutes..."
        & $venvPip install -r $requirementsFile
    }
    
    Write-Success "Dependencies installed in virtual environment"
}

function New-Configuration {
    Write-Info "Creating configuration..."
    
    $configDir = "$InstallDir\.war_squid_v1"
    
    # Create default config
    $config = @{
        version = $VERSION
        install_date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        install_path = $InstallDir
        web = @{
            host = "0.0.0.0"
            port = 5000
        }
        api = @{
            host = "0.0.0.0"
            port = 5001
        }
        phishing = @{
            port = 8080
        }
        c2 = @{
            port = 4444
        }
        logging = @{
            level = "INFO"
        }
    }
    
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path "$configDir\config.json" -Encoding UTF8
    
    Write-Success "Configuration created"
}

function New-CLIWrapper {
    Write-Info "Creating CLI wrapper..."
    
    $wrapperPath = "$InstallDir\war-squid.ps1"
    
    $wrapperContent = @'
# WAR-SQUID-V1 CLI Wrapper
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$InstallDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $InstallDir "venv\Scripts\python.exe"
$MainScript = Join-Path $InstallDir "war_squid.py"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found at $VenvPython"
    exit 1
}

& $VenvPython $MainScript @Arguments
'@
    
    $wrapperContent | Set-Content -Path $wrapperPath -Encoding UTF8
    
    # Create batch wrapper too
    $batchWrapper = @"
@echo off
REM WAR-SQUID-V1 CLI Wrapper
"$VENV_DIR\Scripts\python.exe" "$InstallDir\war_squid.py" %*
"@
    
    $batchWrapper | Set-Content -Path "$InstallDir\war-squid.bat" -Encoding ASCII
    
    Write-Success "CLI wrapper created"
}

function Add-ToPath {
    Write-Info "Adding to system PATH..."
    
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    if ($currentPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$InstallDir", "Machine")
        Write-Success "Added $InstallDir to system PATH"
    } else {
        Write-Info "Already in PATH"
    }
}

function New-DesktopShortcut {
    if ($NoShortcut) {
        return
    }
    
    Write-Info "Creating desktop shortcut..."
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\WAR-SQUID.lnk")
    $Shortcut.TargetPath = "$InstallDir\war-squid.bat"
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.Description = "WAR-SQUID-V1 - Cybersecurity Platform"
    $Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,13"
    $Shortcut.Save()
    
    Write-Success "Desktop shortcut created"
}

function New-FirewallRules {
    if ($SkipFirewall) {
        return
    }
    
    Write-Info "Creating firewall rules..."
    
    $ports = @(
        @{Name="WAR-SQUID Web Dashboard"; Port=5000},
        @{Name="WAR-SQUID API"; Port=5001},
        @{Name="WAR-SQUID Phishing Server"; Port=8080},
        @{Name="WAR-SQUID C2 Server"; Port=4444},
        @{Name="WAR-SQUID Agent Communication"; Port=9000}
    )
    
    foreach ($p in $ports) {
        try {
            New-NetFirewallRule -DisplayName $p.Name -Direction Inbound -Protocol TCP -LocalPort $p.Port -Action Allow -ErrorAction SilentlyContinue | Out-Null
        } catch {
            # Rule may already exist
        }
    }
    
    Write-Success "Firewall rules created"
}

function New-Uninstaller {
    Write-Info "Creating uninstaller..."
    
    $uninstallScript = @"
# WAR-SQUID-V1 Uninstaller
#Requires -RunAsAdministrator

Write-Host "Uninstalling WAR-SQUID-V1..." -ForegroundColor Yellow

# Remove from PATH
`$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
`$newPath = (`$currentPath -split ';' | Where-Object { `$_ -ne '$InstallDir' }) -join ';'
[Environment]::SetEnvironmentVariable("Path", `$newPath, "Machine")

# Remove firewall rules
Get-NetFirewallRule -DisplayName "WAR-SQUID*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue

# Remove desktop shortcut
Remove-Item -Path "`$env:USERPROFILE\Desktop\WAR-SQUID.lnk" -Force -ErrorAction SilentlyContinue

# Ask about data
`$response = Read-Host "Remove all WAR-SQUID data? (y/N)"
if (`$response -eq "y") {
    Remove-Item -Path "$InstallDir" -Recurse -Force
    Write-Host "WAR-SQUID-V1 has been completely removed." -ForegroundColor Green
} else {
    Write-Host "Application removed but data preserved at $InstallDir" -ForegroundColor Yellow
}

Read-Host "Press Enter to exit"
"@
    
    $uninstallScript | Set-Content -Path "$InstallDir\uninstall.ps1" -Encoding UTF8
    
    Write-Success "Uninstaller created"
}

function Show-Summary {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    Installation Complete!                            ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation Details:" -ForegroundColor White
    Write-Host "  Install Directory:  " -NoNewline -ForegroundColor Cyan
    Write-Host $InstallDir
    Write-Host "  Virtual Environment: " -NoNewline -ForegroundColor Cyan
    Write-Host $VENV_DIR
    Write-Host "  CLI Wrapper:        " -NoNewline -ForegroundColor Cyan
    Write-Host "$InstallDir\war-squid.bat"
    Write-Host "  Uninstaller:        " -NoNewline -ForegroundColor Cyan
    Write-Host "$InstallDir\uninstall.ps1"
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  Run application:   " -NoNewline -ForegroundColor Green
    Write-Host "war-squid"
    Write-Host "  Run with args:     " -NoNewline -ForegroundColor Green
    Write-Host "war-squid --help"
    Write-Host ""
    Write-Host "Web Dashboard:" -ForegroundColor White
    Write-Host "  URL:                " -NoNewline -ForegroundColor Cyan
    Write-Host "http://localhost:5000"
    Write-Host "  Default Username:   " -NoNewline -ForegroundColor Cyan
    Write-Host "admin"
    Write-Host "  Default Password:   " -NoNewline -ForegroundColor Cyan
    Write-Host "war_squid_2024"
    Write-Host ""
    Write-Host "⚠  IMPORTANT: Change the default password immediately!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Uninstall:" -ForegroundColor White
    Write-Host "  " -NoNewline -ForegroundColor Red
    Write-Host "$InstallDir\uninstall.ps1"
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

function Main {
    Write-Banner
    
    # Check administrator
    if (-not (Test-Administrator)) {
        Write-Error "This script requires Administrator privileges."
        Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
        exit 1
    }
    Write-Success "Running with Administrator privileges"
    
    # Check Python
    $pythonPath = Test-Python
    if (-not $pythonPath) {
        exit 1
    }
    
    # Create installation directory
    New-InstallDirectory
    
    # Copy files
    Copy-ApplicationFiles
    
    # Create virtual environment
    New-VirtualEnvironment -PythonPath $pythonPath
    
    # Install dependencies
    if (-not $SkipDependencies) {
        Install-VenvDependencies
    }
    
    # Create configuration
    New-Configuration
    
    # Create CLI wrapper
    New-CLIWrapper
    
    # Add to PATH
    Add-ToPath
    
    # Create desktop shortcut
    New-DesktopShortcut
    
    # Create firewall rules
    New-FirewallRules
    
    # Create uninstaller
    New-Uninstaller
    
    # Show summary
    Show-Summary
    
    # Ask to run
    $runNow = Read-Host "Run WAR-SQUID now? (Y/N)"
    if ($runNow -eq "Y" -or $runNow -eq "y") {
        Start-Process -FilePath "$InstallDir\war-squid.bat" -WorkingDirectory $InstallDir
    }
}

# Run main
Main
