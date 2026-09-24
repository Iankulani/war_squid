#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  WAR-SQUID-V1 - Requirements Checker                                         ║
║  Author: Ian Carter Kulani                                                   ║
║                                                                              ║
║  This script checks if all required dependencies are installed and           ║
║  reports missing packages with installation instructions.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import subprocess
import importlib
import pkgutil
import json
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"
NAME = "WAR-SQUID-V1"

# Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.WHITE = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.END = ''

# Disable colors on Windows if not supported
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        Colors.disable()

# ═══════════════════════════════════════════════════════════════════════════════
# REQUIRED PACKAGES
# ═══════════════════════════════════════════════════════════════════════════════

REQUIRED_PACKAGES = {
    # Core
    'colorama': '0.4.6',
    'requests': '2.31.0',
    'psutil': '5.9.0',
    'python-dateutil': '2.8.2',
    'pytz': '2023.3',
    'six': '1.16.0',
    'urllib3': '2.0.0',
    
    # Cryptography & Security
    'cryptography': '41.0.0',
    'paramiko': '3.3.0',
    'bcrypt': '4.0.1',
    'passlib': '1.7.4',
    'pyotp': '2.9.0',
    
    # Networking
    'scapy': '2.5.0',
    'dnspython': '2.4.0',
    'netifaces': '0.11.0',
    'netaddr': '0.9.0',
    'whois': '0.9.5',
    
    # Web Framework
    'flask': '2.3.0',
    'flask-socketio': '5.3.0',
    'flask-cors': '4.0.0',
    'flask-limiter': '3.5.0',
    'werkzeug': '2.3.0',
    'jinja2': '3.1.0',
    'gunicorn': '21.2.0',
    'eventlet': '0.33.0',
    
    # Bot Integrations
    'discord.py': '2.3.0',
    'telethon': '1.29.0',
    'slack-sdk': '3.23.0',
    
    # Google APIs
    'google-auth': '2.23.0',
    'google-api-python-client': '2.100.0',
    
    # Web Automation
    'selenium': '4.14.0',
    'beautifulsoup4': '4.12.0',
    'lxml': '4.9.0',
    
    # Data Processing
    'numpy': '1.24.0',
    'pandas': '2.0.0',
    
    # Visualization
    'matplotlib': '3.7.0',
    'seaborn': '0.12.0',
    
    # PDF & Documents
    'reportlab': '4.0.0',
    'pypdf2': '3.0.0',
    'pillow': '10.0.0',
    
    # QR & Barcodes
    'qrcode': '7.4.0',
    
    # URL Shortening
    'pyshorteners': '1.0.1',
    
    # Keylogging & Input
    'pynput': '1.7.6',
    'pyautogui': '0.9.54',
    'pyperclip': '1.8.2',
    
    # Notifications
    'plyer': '2.1.0',
    
    # Scheduling
    'schedule': '1.2.0',
    
    # Data Formats
    'pyyaml': '6.0',
    
    # CLI & Formatting
    'tabulate': '0.9.0',
    'tqdm': '4.66.0',
    'click': '8.1.0',
    'rich': '13.5.0',
    
    # Faker
    'faker': '19.6.0',
    
    # Email
    'email-validator': '2.0.0',
    
    # Database
    'sqlalchemy': '2.0.0',
    
    # Caching
    'redis': '5.0.0',
    'cachetools': '5.3.0',
    
    # Async
    'aiohttp': '3.8.0',
    'aiofiles': '23.2.0',
    
    # Logging
    'loguru': '0.7.0',
    
    # Docker
    'docker': '6.1.0',
    
    # SSH
    'fabric': '3.2.0',
    
    # Misc
    'python-dotenv': '1.0.0',
    'termcolor': '2.3.0',
    'art': '6.0',
    'pyfiglet': '0.8.post1',
}

OPTIONAL_PACKAGES = {
    'webdriver-manager': '4.0.0',
    'plotly': '5.17.0',
    'kaleido': '0.2.1',
    'pdfplumber': '0.10.0',
    'python-docx': '0.8.11',
    'python-barcode': '0.14.0',
    'gputil': '1.4.0',
    'apscheduler': '3.10.0',
    'toml': '0.10.2',
    'xmltodict': '0.13.0',
    'argon2-cffi': '23.1.0',
    'blessed': '1.20.0',
    'halo': '0.0.31',
}

# ═══════════════════════════════════════════════════════════════════════════════
# CHECKER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class RequirementsChecker:
    """Check if all required packages are installed"""
    
    def __init__(self, verbose: bool = False, fix: bool = False):
        self.verbose = verbose
        self.fix = fix
        self.missing_required: List[Tuple[str, str]] = []
        self.missing_optional: List[Tuple[str, str]] = []
        self.installed: List[Tuple[str, str]] = []
        self.outdated: List[Tuple[str, str, str]] = []
        self.python_version = sys.version_info
        self.pip_available = self._check_pip()
        
    def _check_pip(self) -> bool:
        """Check if pip is available"""
        try:
            import pip
            return True
        except ImportError:
            return False
    
    def _get_installed_version(self, package_name: str) -> Optional[str]:
        """Get installed version of a package"""
        try:
            # Normalize package name
            normalized = package_name.lower().replace('-', '_').replace('.', '_')
            
            # Try importlib.metadata first (Python 3.8+)
            try:
                from importlib.metadata import version, PackageNotFoundError
                try:
                    return version(package_name)
                except PackageNotFoundError:
                    pass
            except ImportError:
                pass
            
            # Fallback to pkg_resources
            try:
                import pkg_resources
                return pkg_resources.get_distribution(package_name).version
            except:
                pass
            
            # Try direct import
            try:
                module = importlib.import_module(normalized)
                if hasattr(module, '__version__'):
                    return module.__version__
                if hasattr(module, 'VERSION'):
                    return module.VERSION
                if hasattr(module, 'version'):
                    return module.version
            except ImportError:
                pass
            
            return None
        except Exception:
            return None
    
    def _parse_version(self, version_str: str) -> Tuple:
        """Parse version string into comparable tuple"""
        try:
            # Remove any non-numeric prefixes
            import re
            version_str = re.sub(r'^[^\d]*', '', version_str)
            parts = version_str.split('.')
            result = []
            for part in parts:
                # Extract numeric part
                match = re.match(r'(\d+)', part)
                if match:
                    result.append(int(match.group(1)))
                else:
                    result.append(0)
            return tuple(result)
        except:
            return (0,)
    
    def _version_compare(self, installed: str, required: str) -> bool:
        """Compare versions, return True if installed >= required"""
        try:
            installed_parts = self._parse_version(installed)
            required_parts = self._parse_version(required)
            
            # Pad shorter version
            max_len = max(len(installed_parts), len(required_parts))
            installed_parts = installed_parts + (0,) * (max_len - len(installed_parts))
            required_parts = required_parts + (0,) * (max_len - len(required_parts))
            
            return installed_parts >= required_parts
        except:
            return True  # Assume OK if can't compare
    
    def check_package(self, package_name: str, required_version: str) -> Tuple[bool, Optional[str]]:
        """Check if a single package is installed and meets version requirement"""
        installed_version = self._get_installed_version(package_name)
        
        if installed_version is None:
            return False, None
        
        if self._version_compare(installed_version, required_version):
            return True, installed_version
        else:
            return False, installed_version
    
    def check_all(self) -> bool:
        """Check all packages"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}  {NAME} v{VERSION} - Requirements Checker{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        # Check Python version
        self._check_python_version()
        
        # Check pip
        if not self.pip_available:
            print(f"{Colors.YELLOW}⚠ pip is not available. Some checks may be limited.{Colors.END}\n")
        
        # Check required packages
        print(f"{Colors.BOLD}{Colors.WHITE}Required Packages:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
        
        for package, version in REQUIRED_PACKAGES.items():
            ok, installed = self.check_package(package, version)
            if ok:
                self.installed.append((package, installed))
                if self.verbose:
                    print(f"  {Colors.GREEN}✓{Colors.END} {package:30} {Colors.GREEN}{installed}{Colors.END}")
            else:
                if installed:
                    self.outdated.append((package, installed, version))
                    print(f"  {Colors.YELLOW}⚠{Colors.END} {package:30} {Colors.YELLOW}{installed} (need {version}){Colors.END}")
                else:
                    self.missing_required.append((package, version))
                    print(f"  {Colors.RED}✗{Colors.END} {package:30} {Colors.RED}MISSING{Colors.END}")
        
        # Check optional packages
        print(f"\n{Colors.BOLD}{Colors.WHITE}Optional Packages:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
        
        for package, version in OPTIONAL_PACKAGES.items():
            ok, installed = self.check_package(package, version)
            if ok:
                if self.verbose:
                    print(f"  {Colors.GREEN}✓{Colors.END} {package:30} {Colors.GREEN}{installed}{Colors.END}")
            else:
                if installed:
                    self.outdated.append((package, installed, version))
                    print(f"  {Colors.YELLOW}⚠{Colors.END} {package:30} {Colors.YELLOW}{installed} (need {version}){Colors.END}")
                else:
                    self.missing_optional.append((package, version))
                    print(f"  {Colors.BLUE}○{Colors.END} {package:30} {Colors.BLUE}not installed (optional){Colors.END}")
        
        # Print summary
        self._print_summary()
        
        # Attempt to fix if requested
        if self.fix and (self.missing_required or self.outdated):
            self._attempt_fix()
        
        return len(self.missing_required) == 0 and len(self.outdated) == 0
    
    def _check_python_version(self):
        """Check Python version"""
        print(f"{Colors.BOLD}{Colors.WHITE}Python Environment:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
        print(f"  Python Version: {platform.python_version()}")
        print(f"  Python Path:    {sys.executable}")
        print(f"  Platform:       {platform.system()} {platform.release()}")
        print(f"  Architecture:   {platform.machine()}")
        
        if self.python_version < (3, 8):
            print(f"  {Colors.RED}✗ Python 3.8+ is required! You have {platform.python_version()}{Colors.END}")
        else:
            print(f"  {Colors.GREEN}✓ Python version is compatible{Colors.END}")
        print()
    
    def _print_summary(self):
        """Print summary of check results"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}  Summary{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        total_required = len(REQUIRED_PACKAGES)
        installed_count = len(self.installed)
        outdated_count = len(self.outdated)
        missing_count = len(self.missing_required)
        
        print(f"  Required packages:  {total_required}")
        print(f"  {Colors.GREEN}Installed:{Colors.END}          {installed_count}")
        print(f"  {Colors.YELLOW}Outdated:{Colors.END}           {outdated_count}")
        print(f"  {Colors.RED}Missing:{Colors.END}            {missing_count}")
        print(f"  {Colors.BLUE}Optional missing:{Colors.END}   {len(self.missing_optional)}")
        
        if missing_count == 0 and outdated_count == 0:
            print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ All required packages are installed and up to date!{Colors.END}")
        else:
            print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠ Some packages need attention.{Colors.END}")
            
            if self.missing_required:
                print(f"\n  {Colors.RED}Missing required packages:{Colors.END}")
                for pkg, ver in self.missing_required:
                    print(f"    - {pkg} (>= {ver})")
            
            if self.outdated:
                print(f"\n  {Colors.YELLOW}Outdated packages:{Colors.END}")
                for pkg, inst, req in self.outdated:
                    print(f"    - {pkg}: {inst} -> {req}")
            
            print(f"\n  {Colors.CYAN}To install missing packages, run:{Colors.END}")
            print(f"    pip install -r requirements.txt")
            print(f"\n  {Colors.CYAN}Or run this script with --fix:{Colors.END}")
            print(f"    python requirements-check.py --fix")
        
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    def _attempt_fix(self):
        """Attempt to install missing packages"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}  Attempting to Fix Missing Packages{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        packages_to_install = []
        for pkg, ver in self.missing_required:
            packages_to_install.append(f"{pkg}>={ver}")
        
        for pkg, inst, req in self.outdated:
            packages_to_install.append(f"{pkg}>={req}")
        
        if not packages_to_install:
            print(f"  {Colors.GREEN}Nothing to fix!{Colors.END}")
            return
        
        print(f"  Installing {len(packages_to_install)} packages...")
        print(f"  Packages: {', '.join(packages_to_install[:5])}{'...' if len(packages_to_install) > 5 else ''}")
        print()
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + packages_to_install
            print(f"  Running: {' '.join(cmd)}\n")
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                print(f"\n  {Colors.GREEN}✓ Installation completed successfully!{Colors.END}")
                print(f"  {Colors.CYAN}Please re-run this script to verify.{Colors.END}")
            else:
                print(f"\n  {Colors.RED}✗ Installation failed with code {result.returncode}{Colors.END}")
        except Exception as e:
            print(f"\n  {Colors.RED}✗ Installation error: {e}{Colors.END}")
    
    def export_report(self, filepath: str = "requirements_report.json"):
        """Export check results to JSON"""
        report = {
            'timestamp': str(__import__('datetime').datetime.now().isoformat()),
            'python_version': platform.python_version(),
            'platform': platform.system(),
            'installed': [{'package': p, 'version': v} for p, v in self.installed],
            'outdated': [{'package': p, 'installed': i, 'required': r} for p, i, r in self.outdated],
            'missing_required': [{'package': p, 'required': r} for p, r in self.missing_required],
            'missing_optional': [{'package': p, 'required': r} for p, r in self.missing_optional],
            'summary': {
                'total_required': len(REQUIRED_PACKAGES),
                'installed': len(self.installed),
                'outdated': len(self.outdated),
                'missing': len(self.missing_required),
                'all_ok': len(self.missing_required) == 0 and len(self.outdated) == 0
            }
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"{Colors.GREEN}✓ Report exported to {filepath}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to export report: {e}{Colors.END}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'{NAME} - Requirements Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python requirements-check.py              # Check all requirements
  python requirements-check.py --verbose    # Show all packages
  python requirements-check.py --fix        # Install missing packages
  python requirements-check.py --report     # Export JSON report
        """
    )
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show all packages including installed ones')
    parser.add_argument('-f', '--fix', action='store_true',
                        help='Attempt to install missing packages')
    parser.add_argument('-r', '--report', action='store_true',
                        help='Export JSON report')
    parser.add_argument('-o', '--output', default='requirements_report.json',
                        help='Output file for report (default: requirements_report.json)')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    checker = RequirementsChecker(verbose=args.verbose, fix=args.fix)
    success = checker.check_all()
    
    if args.report:
        checker.export_report(args.output)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
