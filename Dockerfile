# ═══════════════════════════════════════════════════════════════════════════════
# WAR-SQUID-V1 - Dockerfile
# Author: Ian Carter Kulani
# ═══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Builder ───────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

LABEL maintainer="Ian Carter Kulani"
LABEL description="WAR-SQUID-V1 - Ultimate Cybersecurity Command & Control Platform"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    libpq-dev \
    python3-dev \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
WORKDIR /build
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ───────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="Ian Carter Kulani"
LABEL description="WAR-SQUID-V1 - Ultimate Cybersecurity Command & Control Platform"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    WAR_SQUID_HOME=/app \
    WAR_SQUID_CONFIG=/app/.war_squid_v1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Network tools
    iputils-ping \
    traceroute \
    dnsutils \
    net-tools \
    iproute2 \
    nmap \
    netcat-openbsd \
    tcpdump \
    arping \
    arp-scan \
    whois \
    curl \
    wget \
    openssh-client \
    telnet \
    socat \
    # Security tools
    nikto \
    hydra \
    john \
    hashcat \
    sqlmap \
    # Utilities
    ca-certificates \
    openssl \
    libssl3 \
    libffi8 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    zlib1g \
    procps \
    htop \
    vim \
    nano \
    less \
    file \
    unzip \
    zip \
    tar \
    gzip \
    bzip2 \
    xz-utils \
    # Python runtime
    python3-distutils \
    # Chromium for Selenium
    chromium \
    chromium-driver \
    # Fonts
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Create non-root user
RUN groupadd -r warsquid && useradd -r -g warsquid -d /app -s /bin/bash warsquid

# Copy application files
COPY --chown=warsquid:warsquid . .

# Create necessary directories
RUN mkdir -p /app/.war_squid_v1/{payloads,workspaces,scans,phishing_pages,phishing_templates,captured_credentials,ssh_keys,traffic_logs,nikto_results,web_templates,sessions,spear_phishing,email_templates,dos_logs,agents,c2_logs,modules,network_monitor,keylog_exfil,deployments,domain_hosting,cracking,arp_logs,mac_logs,nat_logs,animation_cache,platform_logs,docker_scans,email_composer,threat_monitor} \
    /app/war_squid_reports/{graphics,pdf_reports,charts} \
    /app/temp \
    && chown -R warsquid:warsquid /app

# Set permissions
RUN chmod +x /app/*.py 2>/dev/null || true \
    && chmod +x /app/*.sh 2>/dev/null || true

# Switch to non-root user
USER warsquid

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose ports
# Web dashboard
EXPOSE 5000
# API
EXPOSE 5001
# Phishing server
EXPOSE 8080
# C2 server
EXPOSE 4444
# Agent communication
EXPOSE 9000

# Default command
CMD ["python", "war_squid.py"]
