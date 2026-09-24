#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  WAR-SQUID-V1 - Health Check Module                                          ║
║  Author: Ian Carter Kulani                                                   ║
║                                                                              ║
║  Comprehensive health check system for monitoring all aspects of the         ║
║  WAR-SQUID-V1 platform including system resources, services, database,       ║
║  network, and security components.                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import socket
import platform
import subprocess
import datetime
import sqlite3
import shutil
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"
NAME = "WAR-SQUID-V1"

# Import config
CONFIG_DIR = ".war_squid_v1"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DATABASE_FILE = os.path.join(CONFIG_DIR, "war_squid.db")
LOG_FILE = os.path.join(CONFIG_DIR, "war_squid.log")

# Health thresholds
THRESHOLDS = {
    'cpu_warning': 70.0,
    'cpu_critical': 90.0,
    'memory_warning': 70.0,
    'memory_critical': 90.0,
    'disk_warning': 70.0,
    'disk_critical': 90.0,
    'load_warning': 5.0,
    'load_critical': 10.0,
    'response_time_warning': 1.0,  # seconds
    'response_time_critical': 5.0,
}

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

# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: str  # 'healthy', 'warning', 'critical', 'unknown'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    duration: float = 0.0

@dataclass
class SystemHealth:
    """Overall system health"""
    status: str
    checks: List[HealthCheckResult]
    timestamp: str
    version: str
    hostname: str
    platform: str
    uptime: float

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class HealthCheck:
    """Comprehensive health check system"""
    
    def __init__(self, verbose: bool = False, json_output: bool = False):
        self.verbose = verbose
        self.json_output = json_output
        self.results: List[HealthCheckResult] = []
        self.start_time = time.time()
        self.hostname = socket.gethostname()
        self.system = platform.system()
        self.python_version = platform.python_version()
        
    def _add_result(self, name: str, status: str, message: str, 
                    details: Dict = None, duration: float = 0.0):
        """Add a health check result"""
        result = HealthCheckResult(
            name=name,
            status=status,
            message=message,
            details=details or {},
            duration=duration
        )
        self.results.append(result)
        
        if not self.json_output:
            self._print_result(result)
        
        return result
    
    def _print_result(self, result: HealthCheckResult):
        """Print a single result"""
        status_colors = {
            'healthy': Colors.GREEN,
            'warning': Colors.YELLOW,
            'critical': Colors.RED,
            'unknown': Colors.BLUE,
        }
        
        status_icons = {
            'healthy': '✓',
            'warning': '⚠',
            'critical': '✗',
            'unknown': '?',
        }
        
        color = status_colors.get(result.status, Colors.WHITE)
        icon = status_icons.get(result.status, '?')
        
        print(f"  {color}{icon}{Colors.END} {result.name:35} {color}{result.status.upper():10}{Colors.END} {result.message}")
        
        if self.verbose and result.details:
            for key, value in result.details.items():
                print(f"      {Colors.CYAN}{key}:{Colors.END} {value}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_python_version(self) -> HealthCheckResult:
        """Check Python version compatibility"""
        start = time.time()
        
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        
        if version_info >= (3, 8):
            status = 'healthy'
            message = f"Python {version_str}"
        elif version_info >= (3, 6):
            status = 'warning'
            message = f"Python {version_str} (3.8+ recommended)"
        else:
            status = 'critical'
            message = f"Python {version_str} (3.8+ required)"
        
        return self._add_result(
            "Python Version",
            status,
            message,
            {
                'version': version_str,
                'executable': sys.executable,
                'implementation': platform.python_implementation(),
            },
            time.time() - start
        )
    
    def check_cpu(self) -> HealthCheckResult:
        """Check CPU usage"""
        start = time.time()
        
        try:
            # Get CPU usage over a short interval
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            if cpu_percent >= THRESHOLDS['cpu_critical']:
                status = 'critical'
                message = f"CPU usage critical: {cpu_percent:.1f}%"
            elif cpu_percent >= THRESHOLDS['cpu_warning']:
                status = 'warning'
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = 'healthy'
                message = f"CPU usage: {cpu_percent:.1f}%"
            
            details = {
                'usage_percent': cpu_percent,
                'cores': cpu_count,
                'physical_cores': psutil.cpu_count(logical=False),
            }
            
            if cpu_freq:
                details['frequency_mhz'] = f"{cpu_freq.current:.0f}"
                details['max_frequency_mhz'] = f"{cpu_freq.max:.0f}"
            
            # Per-core usage
            per_cpu = psutil.cpu_percent(percpu=True)
            details['per_core_usage'] = [f"{c:.1f}%" for c in per_cpu]
            
            return self._add_result("CPU", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("CPU", 'unknown', f"Failed to check CPU: {e}", {}, time.time() - start)
    
    def check_memory(self) -> HealthCheckResult:
        """Check memory usage"""
        start = time.time()
        
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            if mem.percent >= THRESHOLDS['memory_critical']:
                status = 'critical'
                message = f"Memory usage critical: {mem.percent:.1f}%"
            elif mem.percent >= THRESHOLDS['memory_warning']:
                status = 'warning'
                message = f"Memory usage high: {mem.percent:.1f}%"
            else:
                status = 'healthy'
                message = f"Memory usage: {mem.percent:.1f}%"
            
            details = {
                'total_gb': f"{mem.total / (1024**3):.2f}",
                'available_gb': f"{mem.available / (1024**3):.2f}",
                'used_gb': f"{mem.used / (1024**3):.2f}",
                'percent': mem.percent,
                'swap_total_gb': f"{swap.total / (1024**3):.2f}",
                'swap_used_gb': f"{swap.used / (1024**3):.2f}",
                'swap_percent': swap.percent,
            }
            
            return self._add_result("Memory", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Memory", 'unknown', f"Failed to check memory: {e}", {}, time.time() - start)
    
    def check_disk(self) -> HealthCheckResult:
        """Check disk usage"""
        start = time.time()
        
        try:
            # Check main disk
            if self.system == 'Windows':
                disk = psutil.disk_usage('C:\\')
                disk_path = 'C:\\'
            else:
                disk = psutil.disk_usage('/')
                disk_path = '/'
            
            if disk.percent >= THRESHOLDS['disk_critical']:
                status = 'critical'
                message = f"Disk usage critical: {disk.percent:.1f}%"
            elif disk.percent >= THRESHOLDS['disk_warning']:
                status = 'warning'
                message = f"Disk usage high: {disk.percent:.1f}%"
            else:
                status = 'healthy'
                message = f"Disk usage: {disk.percent:.1f}%"
            
            details = {
                'path': disk_path,
                'total_gb': f"{disk.total / (1024**3):.2f}",
                'used_gb': f"{disk.used / (1024**3):.2f}",
                'free_gb': f"{disk.free / (1024**3):.2f}",
                'percent': disk.percent,
            }
            
            # Check all partitions
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'percent': usage.percent,
                        'free_gb': f"{usage.free / (1024**3):.2f}",
                    })
                except:
                    pass
            
            details['partitions'] = partitions
            
            return self._add_result("Disk", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Disk", 'unknown', f"Failed to check disk: {e}", {}, time.time() - start)
    
    def check_load_average(self) -> HealthCheckResult:
        """Check system load average"""
        start = time.time()
        
        try:
            if hasattr(os, 'getloadavg'):
                load1, load5, load15 = os.getloadavg()
                cpu_count = psutil.cpu_count()
                
                # Normalize load by CPU count
                normalized_load = load1 / cpu_count if cpu_count > 0 else load1
                
                if normalized_load >= 2.0:
                    status = 'critical'
                    message = f"Load average critical: {load1:.2f}"
                elif normalized_load >= 1.0:
                    status = 'warning'
                    message = f"Load average high: {load1:.2f}"
                else:
                    status = 'healthy'
                    message = f"Load average: {load1:.2f}"
                
                details = {
                    'load_1min': load1,
                    'load_5min': load5,
                    'load_15min': load15,
                    'cpu_count': cpu_count,
                    'normalized': f"{normalized_load:.2f}",
                }
            else:
                status = 'healthy'
                message = "Load average not available on this platform"
                details = {}
            
            return self._add_result("Load Average", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Load Average", 'unknown', f"Failed to check load: {e}", {}, time.time() - start)
    
    def check_uptime(self) -> HealthCheckResult:
        """Check system uptime"""
        start = time.time()
        
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_days = uptime_seconds / 86400
            uptime_hours = uptime_seconds / 3600
            
            if uptime_days < 1:
                status = 'healthy'
                message = f"Uptime: {uptime_hours:.1f} hours"
            elif uptime_days < 30:
                status = 'healthy'
                message = f"Uptime: {uptime_days:.1f} days"
            else:
                status = 'warning'
                message = f"Uptime: {uptime_days:.1f} days (consider reboot)"
            
            details = {
                'boot_time': datetime.datetime.fromtimestamp(boot_time).isoformat(),
                'uptime_seconds': f"{uptime_seconds:.0f}",
                'uptime_hours': f"{uptime_hours:.2f}",
                'uptime_days': f"{uptime_days:.2f}",
            }
            
            return self._add_result("System Uptime", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("System Uptime", 'unknown', f"Failed to check uptime: {e}", {}, time.time() - start)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # APPLICATION CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_config(self) -> HealthCheckResult:
        """Check configuration file"""
        start = time.time()
        
        try:
            config_path = Path(CONFIG_FILE)
            
            if not config_path.exists():
                return self._add_result(
                    "Configuration",
                    'warning',
                    "Config file not found (will be created on first run)",
                    {'path': str(config_path)},
                    time.time() - start
                )
            
            # Try to load config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required keys
            required_keys = ['version']
            missing_keys = [k for k in required_keys if k not in config]
            
            if missing_keys:
                status = 'warning'
                message = f"Missing config keys: {', '.join(missing_keys)}"
            else:
                status = 'healthy'
                message = f"Configuration valid (v{config.get('version', 'unknown')})"
            
            details = {
                'path': str(config_path),
                'size_bytes': config_path.stat().st_size,
                'keys': list(config.keys()),
            }
            
            return self._add_result("Configuration", status, message, details, time.time() - start)
        except json.JSONDecodeError as e:
            return self._add_result("Configuration", 'critical', f"Invalid JSON: {e}", {}, time.time() - start)
        except Exception as e:
            return self._add_result("Configuration", 'unknown', f"Failed to check config: {e}", {}, time.time() - start)
    
    def check_database(self) -> HealthCheckResult:
        """Check database connectivity"""
        start = time.time()
        
        try:
            db_path = Path(DATABASE_FILE)
            
            if not db_path.exists():
                return self._add_result(
                    "Database",
                    'warning',
                    "Database not found (will be created on first run)",
                    {'path': str(db_path)},
                    time.time() - start
                )
            
            # Try to connect
            conn = sqlite3.connect(str(db_path), timeout=5)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get database size
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            conn.close()
            
            if integrity != "ok":
                status = 'critical'
                message = f"Database integrity check failed: {integrity}"
            else:
                status = 'healthy'
                message = f"Database OK ({len(tables)} tables, {size_mb:.2f} MB)"
            
            details = {
                'path': str(db_path),
                'size_mb': f"{size_mb:.2f}",
                'tables': len(tables),
                'table_names': tables[:20],  # First 20 tables
                'integrity': integrity,
            }
            
            return self._add_result("Database", status, message, details, time.time() - start)
        except sqlite3.Error as e:
            return self._add_result("Database", 'critical', f"Database error: {e}", {}, time.time() - start)
        except Exception as e:
            return self._add_result("Database", 'unknown', f"Failed to check database: {e}", {}, time.time() - start)
    
    def check_logs(self) -> HealthCheckResult:
        """Check log files"""
        start = time.time()
        
        try:
            log_path = Path(LOG_FILE)
            
            if not log_path.exists():
                return self._add_result(
                    "Log File",
                    'healthy',
                    "Log file not found (will be created on first run)",
                    {'path': str(log_path)},
                    time.time() - start
                )
            
            size_bytes = log_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # Check last modification
            mtime = datetime.datetime.fromtimestamp(log_path.stat().st_mtime)
            age_hours = (datetime.datetime.now() - mtime).total_seconds() / 3600
            
            if size_mb > 100:
                status = 'warning'
                message = f"Log file large: {size_mb:.2f} MB (consider rotation)"
            elif age_hours > 24:
                status = 'warning'
                message = f"Log file not updated in {age_hours:.1f} hours"
            else:
                status = 'healthy'
                message = f"Log file OK ({size_mb:.2f} MB)"
            
            details = {
                'path': str(log_path),
                'size_mb': f"{size_mb:.2f}",
                'last_modified': mtime.isoformat(),
                'age_hours': f"{age_hours:.1f}",
            }
            
            return self._add_result("Log File", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Log File", 'unknown', f"Failed to check logs: {e}", {}, time.time() - start)
    
    def check_directories(self) -> HealthCheckResult:
        """Check required directories"""
        start = time.time()
        
        try:
            required_dirs = [
                CONFIG_DIR,
                os.path.join(CONFIG_DIR, "payloads"),
                os.path.join(CONFIG_DIR, "workspaces"),
                os.path.join(CONFIG_DIR, "scans"),
                "war_squid_reports",
                "temp",
            ]
            
            missing = []
            existing = []
            
            for d in required_dirs:
                path = Path(d)
                if path.exists() and path.is_dir():
                    existing.append(d)
                else:
                    missing.append(d)
            
            if missing:
                status = 'warning'
                message = f"Missing {len(missing)} directories"
            else:
                status = 'healthy'
                message = f"All {len(existing)} directories exist"
            
            details = {
                'existing': existing,
                'missing': missing,
                'total_required': len(required_dirs),
            }
            
            return self._add_result("Directories", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Directories", 'unknown', f"Failed to check directories: {e}", {}, time.time() - start)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NETWORK CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_network_interfaces(self) -> HealthCheckResult:
        """Check network interfaces"""
        start = time.time()
        
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            active_interfaces = []
            for name, addrs in interfaces.items():
                if name in stats and stats[name].isup:
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            active_interfaces.append({
                                'name': name,
                                'ip': addr.address,
                                'netmask': addr.netmask,
                            })
            
            if active_interfaces:
                status = 'healthy'
                message = f"{len(active_interfaces)} active interface(s)"
            else:
                status = 'critical'
                message = "No active network interfaces"
            
            details = {
                'interfaces': active_interfaces,
                'total_interfaces': len(interfaces),
            }
            
            return self._add_result("Network Interfaces", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Network Interfaces", 'unknown', f"Failed to check network: {e}", {}, time.time() - start)
    
    def check_ports(self) -> HealthCheckResult:
        """Check if application ports are available or in use"""
        start = time.time()
        
        try:
            ports_to_check = {
                5000: "Web Dashboard",
                5001: "API",
                8080: "Phishing Server",
                4444: "C2 Server",
                9000: "Agent Communication",
            }
            
            port_status = {}
            for port, name in ports_to_check.items():
                # Check if port is in use
                in_use = False
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex(('127.0.0.1', port))
                    in_use = (result == 0)
                    sock.close()
                except:
                    pass
                
                port_status[port] = {
                    'name': name,
                    'in_use': in_use,
                }
            
            in_use_count = sum(1 for p in port_status.values() if p['in_use'])
            
            if in_use_count > 0:
                status = 'healthy'
                message = f"{in_use_count} port(s) in use"
            else:
                status = 'healthy'
                message = "All ports available"
            
            details = {
                'ports': port_status,
            }
            
            return self._add_result("Network Ports", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Network Ports", 'unknown', f"Failed to check ports: {e}", {}, time.time() - start)
    
    def check_internet_connectivity(self) -> HealthCheckResult:
        """Check internet connectivity"""
        start = time.time()
        
        try:
            # Try to connect to well-known DNS servers
            test_hosts = [
                ('8.8.8.8', 53),      # Google DNS
                ('1.1.1.1', 53),      # Cloudflare DNS
                ('208.67.222.222', 53),  # OpenDNS
            ]
            
            reachable = []
            for host, port in test_hosts:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        reachable.append(host)
                    sock.close()
                except:
                    pass
            
            if reachable:
                status = 'healthy'
                message = f"Internet reachable ({len(reachable)}/{len(test_hosts)} hosts)"
            else:
                status = 'warning'
                message = "No internet connectivity detected"
            
            details = {
                'reachable_hosts': reachable,
                'tested_hosts': [h for h, _ in test_hosts],
            }
            
            return self._add_result("Internet Connectivity", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Internet Connectivity", 'unknown', f"Failed to check connectivity: {e}", {}, time.time() - start)
    
    def check_dns(self) -> HealthCheckResult:
        """Check DNS resolution"""
        start = time.time()
        
        try:
            test_domains = ['google.com', 'cloudflare.com', 'github.com']
            resolved = []
            failed = []
            
            for domain in test_domains:
                try:
                    ip = socket.gethostbyname(domain)
                    resolved.append({'domain': domain, 'ip': ip})
                except:
                    failed.append(domain)
            
            if len(resolved) == len(test_domains):
                status = 'healthy'
                message = f"DNS resolution OK ({len(resolved)}/{len(test_domains)})"
            elif resolved:
                status = 'warning'
                message = f"Partial DNS resolution ({len(resolved)}/{len(test_domains)})"
            else:
                status = 'critical'
                message = "DNS resolution failed"
            
            details = {
                'resolved': resolved,
                'failed': failed,
            }
            
            return self._add_result("DNS Resolution", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("DNS Resolution", 'unknown', f"Failed to check DNS: {e}", {}, time.time() - start)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DEPENDENCY CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_dependencies(self) -> HealthCheckResult:
        """Check Python dependencies"""
        start = time.time()
        
        try:
            required_packages = {
                'requests': 'requests',
                'psutil': 'psutil',
                'colorama': 'colorama',
                'cryptography': 'cryptography',
                'flask': 'flask',
                'paramiko': 'paramiko',
                'scapy': 'scapy',
                'dnspython': 'dns',
                'beautifulsoup4': 'bs4',
                'selenium': 'selenium',
            }
            
            installed = []
            missing = []
            
            for package, import_name in required_packages.items():
                try:
                    __import__(import_name)
                    installed.append(package)
                except ImportError:
                    missing.append(package)
            
            if not missing:
                status = 'healthy'
                message = f"All {len(required_packages)} core dependencies installed"
            elif len(missing) <= 2:
                status = 'warning'
                message = f"Missing {len(missing)} dependencies: {', '.join(missing)}"
            else:
                status = 'critical'
                message = f"Missing {len(missing)} dependencies"
            
            details = {
                'installed': installed,
                'missing': missing,
                'total': len(required_packages),
            }
            
            return self._add_result("Dependencies", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Dependencies", 'unknown', f"Failed to check dependencies: {e}", {}, time.time() - start)
    
    def check_external_tools(self) -> HealthCheckResult:
        """Check external tools availability"""
        start = time.time()
        
        try:
            tools = {
                'nmap': 'nmap',
                'nikto': 'nikto',
                'hydra': 'hydra',
                'john': 'john',
                'hashcat': 'hashcat',
                'sqlmap': 'sqlmap',
                'tcpdump': 'tcpdump',
                'openssl': 'openssl',
                'ssh': 'ssh',
                'curl': 'curl',
                'wget': 'wget',
                'ping': 'ping',
                'traceroute': 'traceroute',
            }
            
            available = []
            missing = []
            
            for tool, command in tools.items():
                if shutil.which(command):
                    available.append(tool)
                else:
                    missing.append(tool)
            
            if not missing:
                status = 'healthy'
                message = f"All {len(tools)} external tools available"
            elif len(available) >= 5:
                status = 'warning'
                message = f"{len(available)}/{len(tools)} tools available"
            else:
                status = 'warning'
                message = f"Only {len(available)}/{len(tools)} tools available"
            
            details = {
                'available': available,
                'missing': missing,
                'total': len(tools),
            }
            
            return self._add_result("External Tools", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("External Tools", 'unknown', f"Failed to check tools: {e}", {}, time.time() - start)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECURITY CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_permissions(self) -> HealthCheckResult:
        """Check file permissions"""
        start = time.time()
        
        try:
            issues = []
            checked = []
            
            # Check config directory permissions
            config_path = Path(CONFIG_DIR)
            if config_path.exists():
                checked.append(str(config_path))
                # Check if world-readable (potential security issue)
                if self.system != 'Windows':
                    mode = config_path.stat().st_mode
                    if mode & 0o004:  # World readable
                        issues.append(f"{config_path} is world-readable")
            
            # Check database permissions
            db_path = Path(DATABASE_FILE)
            if db_path.exists():
                checked.append(str(db_path))
                if self.system != 'Windows':
                    mode = db_path.stat().st_mode
                    if mode & 0o004:  # World readable
                        issues.append(f"{db_path} is world-readable")
            
            if issues:
                status = 'warning'
                message = f"{len(issues)} permission issue(s)"
            else:
                status = 'healthy'
                message = "File permissions OK"
            
            details = {
                'checked': checked,
                'issues': issues,
            }
            
            return self._add_result("File Permissions", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("File Permissions", 'unknown', f"Failed to check permissions: {e}", {}, time.time() - start)
    
    def check_running_processes(self) -> HealthCheckResult:
        """Check for running WAR-SQUID processes"""
        start = time.time()
        
        try:
            war_squid_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    cmdline = proc.info.get('cmdline') or []
                    cmdline_str = ' '.join(cmdline) if cmdline else ''
                    
                    if 'war_squid' in cmdline_str.lower() or 'war-squid' in cmdline_str.lower():
                        war_squid_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if war_squid_processes:
                status = 'healthy'
                message = f"{len(war_squid_processes)} WAR-SQUID process(es) running"
            else:
                status = 'healthy'
                message = "No WAR-SQUID processes running"
            
            details = {
                'processes': war_squid_processes,
                'count': len(war_squid_processes),
            }
            
            return self._add_result("Running Processes", status, message, details, time.time() - start)
        except Exception as e:
            return self._add_result("Running Processes", 'unknown', f"Failed to check processes: {e}", {}, time.time() - start)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN HEALTH CHECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    def run_all_checks(self) -> SystemHealth:
        """Run all health checks"""
        if not self.json_output:
            print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.WHITE}  {NAME} v{VERSION} - Health Check{Colors.END}")
            print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
            
            print(f"{Colors.BOLD}System Information:{Colors.END}")
            print(f"  Hostname:     {self.hostname}")
            print(f"  Platform:     {self.system} {platform.release()}")
            print(f"  Python:       {self.python_version}")
            print(f"  Time:         {datetime.datetime.now().isoformat()}")
            print()
            
            print(f"{Colors.BOLD}System Checks:{Colors.END}")
        
        # System checks
        self.check_python_version()
        self.check_cpu()
        self.check_memory()
        self.check_disk()
        self.check_load_average()
        self.check_uptime()
        
        if not self.json_output:
            print(f"\n{Colors.BOLD}Application Checks:{Colors.END}")
        
        # Application checks
        self.check_config()
        self.check_database()
        self.check_logs()
        self.check_directories()
        
        if not self.json_output:
            print(f"\n{Colors.BOLD}Network Checks:{Colors.END}")
        
        # Network checks
        self.check_network_interfaces()
        self.check_ports()
        self.check_internet_connectivity()
        self.check_dns()
        
        if not self.json_output:
            print(f"\n{Colors.BOLD}Dependency Checks:{Colors.END}")
        
        # Dependency checks
        self.check_dependencies()
        self.check_external_tools()
        
        if not self.json_output:
            print(f"\n{Colors.BOLD}Security Checks:{Colors.END}")
        
        # Security checks
        self.check_permissions()
        self.check_running_processes()
        
        # Determine overall status
        statuses = [r.status for r in self.results]
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        # Create system health summary
        health = SystemHealth(
            status=overall_status,
            checks=self.results,
            timestamp=datetime.datetime.now().isoformat(),
            version=VERSION,
            hostname=self.hostname,
            platform=f"{self.system} {platform.release()}",
            uptime=time.time() - self.start_time
        )
        
        if not self.json_output:
            self._print_summary(health)
        
        return health
    
    def _print_summary(self, health: SystemHealth):
        """Print health check summary"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}  Summary{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        healthy = sum(1 for r in health.checks if r.status == 'healthy')
        warning = sum(1 for r in health.checks if r.status == 'warning')
        critical = sum(1 for r in health.checks if r.status == 'critical')
        unknown = sum(1 for r in health.checks if r.status == 'unknown')
        
        print(f"  Total checks:  {len(health.checks)}")
        print(f"  {Colors.GREEN}Healthy:{Colors.END}        {healthy}")
        print(f"  {Colors.YELLOW}Warning:{Colors.END}        {warning}")
        print(f"  {Colors.RED}Critical:{Colors.END}       {critical}")
        print(f"  {Colors.BLUE}Unknown:{Colors.END}        {unknown}")
        print(f"  Duration:      {health.uptime:.2f}s")
        print()
        
        # Overall status
        status_colors = {
            'healthy': Colors.GREEN,
            'warning': Colors.YELLOW,
            'critical': Colors.RED,
        }
        
        color = status_colors.get(health.status, Colors.WHITE)
        print(f"  Overall Status: {color}{Colors.BOLD}{health.status.upper()}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    def to_json(self) -> str:
        """Convert results to JSON"""
        health = SystemHealth(
            status='unknown',
            checks=self.results,
            timestamp=datetime.datetime.now().isoformat(),
            version=VERSION,
            hostname=self.hostname,
            platform=f"{self.system} {platform.release()}",
            uptime=time.time() - self.start_time
        )
        
        # Determine status
        statuses = [r.status for r in self.results]
        if 'critical' in statuses:
            health.status = 'critical'
        elif 'warning' in statuses:
            health.status = 'warning'
        else:
            health.status = 'healthy'
        
        return json.dumps(asdict(health), indent=2, default=str)
    
    def export_report(self, filepath: str = "health_report.json"):
        """Export health report to file"""
        try:
            with open(filepath, 'w') as f:
                f.write(self.to_json())
            print(f"{Colors.GREEN}✓ Health report exported to {filepath}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to export report: {e}{Colors.END}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'{NAME} - Health Check',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python health.py                  # Run all health checks
  python health.py --verbose        # Show detailed output
  python health.py --json           # Output as JSON
  python health.py --export         # Export report to file
  python health.py --watch          # Continuous monitoring
        """
    )
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed output')
    parser.add_argument('-j', '--json', action='store_true',
                        help='Output as JSON')
    parser.add_argument('-e', '--export', action='store_true',
                        help='Export report to file')
    parser.add_argument('-o', '--output', default='health_report.json',
                        help='Output file for report')
    parser.add_argument('-w', '--watch', type=int, metavar='SECONDS',
                        help='Continuous monitoring interval')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    if args.watch:
        # Continuous monitoring
        try:
            while True:
                os.system('clear' if os.name != 'nt' else 'cls')
                hc = HealthCheck(verbose=args.verbose, json_output=args.json)
                health = hc.run_all_checks()
                
                if args.json:
                    print(hc.to_json())
                
                print(f"\n{Colors.CYAN}Next check in {args.watch} seconds... (Ctrl+C to stop){Colors.END}")
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoring stopped.{Colors.END}")
    else:
        # Single check
        hc = HealthCheck(verbose=args.verbose, json_output=args.json)
        health = hc.run_all_checks()
        
        if args.json:
            print(hc.to_json())
        
        if args.export:
            hc.export_report(args.output)
        
        # Exit code based on status
        if health.status == 'healthy':
            sys.exit(0)
        elif health.status == 'warning':
            sys.exit(1)
        else:
            sys.exit(2)


if __name__ == '__main__':
    main()
