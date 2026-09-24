#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# WAR-SQUID-V1 - Bash Installation Script
# Author: Ian Carter Kulani
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
VERSION="1.0.0"
NAME="WAR-SQUID-V1"
INSTALL_DIR="/opt/war-squid"
VENV_DIR="${INSTALL_DIR}/venv"
SERVICE_NAME="war-squid"
PYTHON_MIN_VERSION="3.8"

# Functions
print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██╗    ██╗ █████╗ ██████╗       ███████╗ ██████╗ ██╗   ██╗██╗██████╗        ║
║  ██║    ██║██╔══██╗██╔══██╗      ██╔════╝██╔═══██╗██║   ██║██║██╔══██╗       ║
║  ██║ █╗ ██║███████║██████╔╝█████╗███████╗██║   ██║██║   ██║██║██║  ██║       ║
║  ██║███╗██║██╔══██║██╔══██╗╚════╝╚════██║██║▄▄ ██║██║   ██║██║██║  ██║       ║
║  ╚███╔███╔╝██║  ██║██║  ██║      ███████║╚██████╔╝╚██████╔╝██║██████╔╝       ║
║   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝      ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═════╝        ║
║                                                                              ║
║                    WAR-SQUID-V1 - Installation Script                       ║
║                         Author: Ian Carter Kulani                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_warning "Not running as root. Some operations may require sudo."
        SUDO="sudo"
    else
        SUDO=""
    fi
}

check_python() {
    log_info "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python is not installed. Please install Python ${PYTHON_MIN_VERSION}+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Found Python ${PYTHON_VERSION}"
    
    # Check version
    if ! $PYTHON_CMD -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python ${PYTHON_MIN_VERSION}+ is required. Found ${PYTHON_VERSION}"
        exit 1
    fi
    
    log_success "Python version is compatible"
}

install_system_deps() {
    log_info "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        $SUDO apt-get update -qq
        $SUDO apt-get install -y -qq \
            python3-pip \
            python3-venv \
            python3-dev \
            build-essential \
            gcc \
            g++ \
            make \
            libffi-dev \
            libssl-dev \
            libxml2-dev \
            libxslt1-dev \
            libjpeg-dev \
            zlib1g-dev \
            git \
            curl \
            wget \
            iputils-ping \
            traceroute \
            dnsutils \
            net-tools \
            nmap \
            netcat-openbsd \
            tcpdump \
            openssh-client \
            whois \
            ca-certificates \
            procps \
            htop
    elif command -v yum &> /dev/null; then
        $SUDO yum install -y \
            python3-pip \
            python3-devel \
            gcc \
            gcc-c++ \
            make \
            libffi-devel \
            openssl-devel \
            libxml2-devel \
            libxslt-devel \
            libjpeg-devel \
            zlib-devel \
            git \
            curl \
            wget \
            iputils \
            traceroute \
            bind-utils \
            net-tools \
            nmap \
            nc \
            tcpdump \
            openssh-clients \
            whois \
            ca-certificates \
            procps-ng \
            htop
    elif command -v pacman &> /dev/null; then
        $SUDO pacman -Sy --noconfirm \
            python-pip \
            base-devel \
            gcc \
            make \
            libffi \
            openssl \
            libxml2 \
            libxslt \
            libjpeg-turbo \
            zlib \
            git \
            curl \
            wget \
            iputils \
            traceroute \
            bind \
            net-tools \
            nmap \
            gnu-netcat \
            tcpdump \
            openssh \
            whois \
            ca-certificates \
            procps-ng \
            htop
    elif command -v apk &> /dev/null; then
        $SUDO apk add --no-cache \
            python3 \
            py3-pip \
            python3-dev \
            build-base \
            gcc \
            g++ \
            make \
            libffi-dev \
            openssl-dev \
            libxml2-dev \
            libxslt-dev \
            jpeg-dev \
            zlib-dev \
            git \
            curl \
            wget \
            iputils \
            traceroute \
            bind-tools \
            net-tools \
            nmap \
            netcat-openbsd \
            tcpdump \
            openssh-client \
            whois \
            ca-certificates \
            procps \
            htop
    else
        log_warning "Unknown package manager. Please install dependencies manually."
    fi
    
    log_success "System dependencies installed"
}

create_directories() {
    log_info "Creating installation directories..."
    
    $SUDO mkdir -p "${INSTALL_DIR}"
    $SUDO mkdir -p "${INSTALL_DIR}/.war_squid_v1"
    $SUDO mkdir -p "${INSTALL_DIR}/war_squid_reports"
    $SUDO mkdir -p "${INSTALL_DIR}/temp"
    $SUDO mkdir -p /var/log/war-squid
    $SUDO mkdir -p /etc/war-squid
    
    log_success "Directories created"
}

install_application() {
    log_info "Installing ${NAME} application..."
    
    # Copy application files
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    $SUDO cp -r "${SCRIPT_DIR}"/* "${INSTALL_DIR}/"
    
    # Create virtual environment
    $SUDO $PYTHON_CMD -m venv "${VENV_DIR}"
    
    # Install Python dependencies
    $SUDO "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
    
    if [[ -f "${INSTALL_DIR}/requirements.txt" ]]; then
        $SUDO "${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"
    fi
    
    # Set permissions
    $SUDO chmod +x "${INSTALL_DIR}"/*.py 2>/dev/null || true
    $SUDO chmod +x "${INSTALL_DIR}"/*.sh 2>/dev/null || true
    
    log_success "Application installed to ${INSTALL_DIR}"
}

create_config() {
    log_info "Creating configuration..."
    
    CONFIG_FILE="/etc/war-squid/war-squid.conf"
    
    $SUDO cat > "${CONFIG_FILE}" << EOF
# WAR-SQUID-V1 Configuration
# Generated by install.sh on $(date)

# Application Settings
WAR_SQUID_HOME="${INSTALL_DIR}"
WAR_SQUID_CONFIG="${INSTALL_DIR}/.war_squid_v1"
WAR_SQUID_LOG="${INSTALL_DIR}/.war_squid_v1/war_squid.log"

# Web Dashboard
WEB_HOST="0.0.0.0"
WEB_PORT="5000"

# API
API_HOST="0.0.0.0"
API_PORT="5001"

# Phishing Server
PHISHING_PORT="8080"

# C2 Server
C2_PORT="4444"

# Agent Communication
AGENT_PORT="9000"

# Logging
LOG_LEVEL="INFO"
EOF
    
    log_success "Configuration created at ${CONFIG_FILE}"
}

create_service() {
    log_info "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    $SUDO cat > "${SERVICE_FILE}" << EOF
[Unit]
Description=WAR-SQUID-V1 - Cybersecurity Command & Control Platform
Documentation=https://github.com/ian-carter-kulani/war-squid
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=${INSTALL_DIR}"
EnvironmentFile=-/etc/war-squid/war-squid.conf
ExecStart=${VENV_DIR}/bin/python ${INSTALL_DIR}/war_squid.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/war-squid/war-squid.log
StandardError=append:/var/log/war-squid/war-squid-error.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

# Capabilities for network operations
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF
    
    $SUDO systemctl daemon-reload
    $SUDO systemctl enable "${SERVICE_NAME}"
    
    log_success "Systemd service created and enabled"
}

create_cli_wrapper() {
    log_info "Creating CLI wrapper..."
    
    WRAPPER="/usr/local/bin/war-squid"
    
    $SUDO cat > "${WRAPPER}" << EOF
#!/bin/bash
# WAR-SQUID-V1 CLI Wrapper

INSTALL_DIR="${INSTALL_DIR}"
VENV_DIR="${VENV_DIR}"

# Check if virtual environment exists
if [[ ! -d "\${VENV_DIR}" ]]; then
    echo "Error: Virtual environment not found at \${VENV_DIR}"
    exit 1
fi

# Run the application
exec "\${VENV_DIR}/bin/python" "\${INSTALL_DIR}/war_squid.py" "\$@"
EOF
    
    $SUDO chmod +x "${WRAPPER}"
    
    log_success "CLI wrapper created at ${WRAPPER}"
}

create_uninstaller() {
    log_info "Creating uninstaller..."
    
    UNINSTALLER="${INSTALL_DIR}/uninstall.sh"
    
    $SUDO cat > "${UNINSTALLER}" << 'EOF'
#!/bin/bash
# WAR-SQUID-V1 Uninstaller

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Uninstalling WAR-SQUID-V1...${NC}"

# Stop service
if systemctl is-active --quiet war-squid 2>/dev/null; then
    systemctl stop war-squid
    echo "Service stopped"
fi

# Disable service
if systemctl is-enabled --quiet war-squid 2>/dev/null; then
    systemctl disable war-squid
    echo "Service disabled"
fi

# Remove service file
if [[ -f /etc/systemd/system/war-squid.service ]]; then
    rm -f /etc/systemd/system/war-squid.service
    systemctl daemon-reload
    echo "Service file removed"
fi

# Remove CLI wrapper
if [[ -f /usr/local/bin/war-squid ]]; then
    rm -f /usr/local/bin/war-squid
    echo "CLI wrapper removed"
fi

# Remove configuration
if [[ -d /etc/war-squid ]]; then
    rm -rf /etc/war-squid
    echo "Configuration removed"
fi

# Remove logs
if [[ -d /var/log/war-squid ]]; then
    rm -rf /var/log/war-squid
    echo "Logs removed"
fi

# Ask about data
read -p "Remove all WAR-SQUID data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ -d /opt/war-squid ]]; then
        rm -rf /opt/war-squid
        echo "Application data removed"
    fi
fi

echo -e "${GREEN}WAR-SQUID-V1 has been uninstalled.${NC}"
EOF
    
    $SUDO chmod +x "${UNINSTALLER}"
    
    log_success "Uninstaller created at ${UNINSTALLER}"
}

print_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Installation Complete!                            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}Installation Details:${NC}"
    echo -e "  ${CYAN}Install Directory:${NC}  ${INSTALL_DIR}"
    echo -e "  ${CYAN}Virtual Environment:${NC} ${VENV_DIR}"
    echo -e "  ${CYAN}Configuration:${NC}      /etc/war-squid/war-squid.conf"
    echo -e "  ${CYAN}Logs:${NC}               /var/log/war-squid/"
    echo -e "  ${CYAN}Service:${NC}            ${SERVICE_NAME}.service"
    echo ""
    echo -e "${WHITE}Usage:${NC}"
    echo -e "  ${GREEN}Start service:${NC}      sudo systemctl start ${SERVICE_NAME}"
    echo -e "  ${GREEN}Stop service:${NC}       sudo systemctl stop ${SERVICE_NAME}"
    echo -e "  ${GREEN}Restart service:${NC}    sudo systemctl restart ${SERVICE_NAME}"
    echo -e "  ${GREEN}Check status:${NC}       sudo systemctl status ${SERVICE_NAME}"
    echo -e "  ${GREEN}View logs:${NC}          sudo journalctl -u ${SERVICE_NAME} -f"
    echo -e "  ${GREEN}Run CLI:${NC}            war-squid --help"
    echo ""
    echo -e "${WHITE}Web Dashboard:${NC}"
    echo -e "  ${CYAN}URL:${NC}                http://localhost:5000"
    echo -e "  ${CYAN}Default Username:${NC}   admin"
    echo -e "  ${CYAN}Default Password:${NC}   war_squid_2024"
    echo ""
    echo -e "${YELLOW}⚠  IMPORTANT: Change the default password immediately!${NC}"
    echo ""
    echo -e "${WHITE}Uninstall:${NC}"
    echo -e "  ${RED}sudo ${INSTALL_DIR}/uninstall.sh${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    print_banner
    
    check_root
    check_python
    install_system_deps
    create_directories
    install_application
    create_config
    create_service
    create_cli_wrapper
    create_uninstaller
    
    print_summary
    
    # Ask to start service
    read -p "Start WAR-SQUID service now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        $SUDO systemctl start "${SERVICE_NAME}"
        sleep 2
        if $SUDO systemctl is-active --quiet "${SERVICE_NAME}"; then
            log_success "WAR-SQUID service started successfully"
        else
            log_error "Failed to start WAR-SQUID service. Check logs with: journalctl -u ${SERVICE_NAME} -f"
        fi
    fi
}

main "$@"
