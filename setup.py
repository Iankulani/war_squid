#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  WAR-SQUID-V1 - Setup Script                                                 ║
║  Author: Ian Carter Kulani                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from setuptools import setup, find_packages, Command

# ═══════════════════════════════════════════════════════════════════════════════
# METADATA
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"
NAME = "war-squid-v1"
AUTHOR = "Ian Carter Kulani"
AUTHOR_EMAIL = "ian.carter.kulani@example.com"
DESCRIPTION = "Ultimate Cybersecurity Command & Control Platform"
LONG_DESCRIPTION = """
WAR-SQUID-V1 is a comprehensive cybersecurity automation platform featuring:

• 300+ Security Commands
• Multi-Platform Bot Integration (Discord, Telegram, Slack, Google Chat, Signal, WhatsApp, Web)
• Blue & White Web Dashboard with Bar & Pie Charts
• All Ping/Traceroute/Nmap/Wget/Curl/SSH Commands
• 100+ Phishing Templates for Social Engineering
• Real Traffic Generation
• Password Cracking Engine
• ARP Spoofing & Network Manipulation
• MAC Address Management
• NAT Information
• Docker Security Scanning
• Email Composition & Sending
• PDF Report Generation
• Keylogger with Exfiltration
• Automated Threat Monitoring
• Agent Mode with Full Control

Author: Ian Carter Kulani
"""
URL = "https://github.com/ian-carter-kulani/war-squid"
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.8"

# ═══════════════════════════════════════════════════════════════════════════════
# READ REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def read_requirements(filename="requirements.txt"):
    """Read requirements from file"""
    requirements = []
    req_file = Path(__file__).parent / filename
    if req_file.exists():
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

def read_file(filename):
    """Read file content"""
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class CleanCommand(Command):
    """Custom clean command to remove build artifacts"""
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Remove build artifacts"""
        dirs_to_remove = [
            'build', 'dist', '*.egg-info', '__pycache__',
            '.pytest_cache', '.mypy_cache', '.tox', 'htmlcov',
            '.coverage', '*.pyc', '*.pyo'
        ]
        
        for pattern in dirs_to_remove:
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"Removed directory: {path}")
                elif path.is_file():
                    path.unlink()
                    print(f"Removed file: {path}")
        
        # Remove nested __pycache__ directories
        for path in Path('.').rglob('__pycache__'):
            shutil.rmtree(path, ignore_errors=True)
            print(f"Removed: {path}")


class InstallDepsCommand(Command):
    """Install all dependencies"""
    description = "Install all project dependencies"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Install dependencies"""
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully!")


class CheckDepsCommand(Command):
    """Check all dependencies"""
    description = "Check if all dependencies are installed"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Check dependencies"""
        print("Checking dependencies...")
        try:
            from requirements_check import RequirementsChecker
            checker = RequirementsChecker(verbose=True)
            success = checker.check_all()
            sys.exit(0 if success else 1)
        except ImportError:
            print("requirements-check.py not found. Running pip check...")
            subprocess.call([sys.executable, '-m', 'pip', 'check'])


class RunTestsCommand(Command):
    """Run test suite"""
    description = "Run all tests"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Run tests"""
        print("Running tests...")
        subprocess.call([sys.executable, '-m', 'pytest', 'tests/', '-v', '--cov=.'])


class CreateDirsCommand(Command):
    """Create all necessary directories"""
    description = "Create all project directories"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Create directories"""
        dirs = [
            '.war_squid_v1',
            '.war_squid_v1/payloads',
            '.war_squid_v1/workspaces',
            '.war_squid_v1/scans',
            '.war_squid_v1/phishing_pages',
            '.war_squid_v1/phishing_templates',
            '.war_squid_v1/captured_credentials',
            '.war_squid_v1/ssh_keys',
            '.war_squid_v1/traffic_logs',
            '.war_squid_v1/nikto_results',
            'war_squid_reports',
            'war_squid_reports/graphics',
            'war_squid_reports/pdf_reports',
            'war_squid_reports/charts',
            'temp',
            'tests',
            'tests/unit',
            'tests/integration',
            'docs',
        ]
        
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
            print(f"Created: {d}")


class DockerBuildCommand(Command):
    """Build Docker image"""
    description = "Build Docker image"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Build Docker image"""
        print("Building Docker image...")
        subprocess.call(['docker', 'build', '-t', 'war-squid-v1:latest', '-f', 'Dockerfile', '.'])
        subprocess.call(['docker', 'build', '-t', 'war-squid-v1:alpine', '-f', 'Dockerfile.alpine', '.'])


class DockerRunCommand(Command):
    """Run Docker container"""
    description = "Run Docker container"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Run Docker container"""
        print("Starting WAR-SQUID Docker container...")
        subprocess.call([
            'docker', 'run', '-d',
            '--name', 'war-squid-v1',
            '-p', '5000:5000',
            '-p', '5001:5001',
            '-p', '8080:8080',
            '-p', '4444:4444',
            '--restart', 'unless-stopped',
            'war-squid-v1:latest'
        ])


class HealthCheckCommand(Command):
    """Run health check"""
    description = "Run system health check"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        """Run health check"""
        print("Running health check...")
        try:
            from health import HealthCheck
            hc = HealthCheck()
            hc.run_all_checks()
        except ImportError:
            print("health.py not found. Running basic checks...")
            import psutil
            print(f"CPU: {psutil.cpu_percent()}%")
            print(f"Memory: {psutil.virtual_memory().percent}%")
            print(f"Disk: {psutil.disk_usage('/').percent}%")


# ═══════════════════════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════════════════════

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    license=LICENSE,
    python_requires=PYTHON_REQUIRES,
    
    # Packages
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    py_modules=[
        'war_squid',
        'requirements_check',
        'health',
    ],
    
    # Include data files
    include_package_data=True,
    package_data={
        '': [
            '*.txt',
            '*.md',
            '*.json',
            '*.yaml',
            '*.yml',
            '*.html',
            '*.css',
            '*.js',
            'Dockerfile',
            'Dockerfile.alpine',
            'docker-compose.yml',
            '.gitlab-ci.yml',
        ],
    },
    
    # Requirements
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
        'full': read_requirements('requirements.txt') + read_requirements('requirements-dev.txt'),
    },
    
    # Entry points
    entry_points={
        'console_scripts': [
            'war-squid=war_squid:main',
            'war-squid-check=requirements_check:main',
            'war-squid-health=health:main',
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    
    # Keywords
    keywords='security cybersecurity pentesting networking automation',
    
    # Custom commands
    cmdclass={
        'clean': CleanCommand,
        'install_deps': InstallDepsCommand,
        'check_deps': CheckDepsCommand,
        'run_tests': RunTestsCommand,
        'create_dirs': CreateDirsCommand,
        'docker_build': DockerBuildCommand,
        'docker_run': DockerRunCommand,
        'health_check': HealthCheckCommand,
    },
    
    # Zip safe
    zip_safe=False,
)
