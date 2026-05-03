# ⚙️ Technical Installation & Deployment Guide

This document provides a highly detailed, step-by-step procedure for deploying the **Hardened Polyglot Assessment Platform (HPAP)** on a Linux production environment.

---

## 1. System Requirements
*   **Operating System**: RHEL 9 (Recommended), CentOS Stream 9, or Ubuntu 22.04 LTS.
*   **Permissions**: Full `root` or `sudo` access is mandatory for user and directory management.
*   **Compilers**: `gcc` and `g++` (v11+ recommended).
*   **Interpreters**: `python3` (v3.9+).
*   **Memory**: Minimum 4GB (8GB recommended for Llama 3 local inference).

---

## 2. Environment Preparation

### 2.1 Update System & Install Toolchain
On RHEL/CentOS systems:
```bash
sudo dnf update -y
sudo dnf install -y gcc gcc-c++ python3 python3-pip net-tools
```

### 2.2 Global Directory Initialization
HPAP uses the `/srv` hierarchy for persistent data and `/home` for student workspaces.
```bash
# Create root architecture
sudo mkdir -p /srv/assessment_system/{core,assessments,system_logs}
sudo mkdir -p /srv/assessment_system/core/runtime

# Apply initial permissions
sudo chown -R root:root /srv/assessment_system
sudo chmod 755 /srv/assessment_system
```

---

## 3. Security Infrastructure Setup

### 3.1 Provisioning the Sandbox User
The `sandbox_user` is a restricted system account used only for code execution.
```bash
# Create the user with no shell and no home directory
sudo useradd -r -s /usr/sbin/nologin sandbox_user

# Secure the runtime directory
# 711 allows the backend to enter but prevents the sandbox user from listing other temp folders
sudo chmod 711 /srv/assessment_system/core/runtime
```

### 3.2 Sudoers Configuration
The Flask backend (running as root) must be able to switch to `sandbox_user` without a password prompt.
```bash
# Add this line to /etc/sudoers or create /etc/sudoers.d/assessment
root ALL=(sandbox_user) NOPASSWD: ALL
```

---

## 4. AI Engine Deployment (Ollama)

### 4.1 Installation
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 4.2 Start Service & Pull Model
```bash
# Start the Ollama background service
ollama serve > /srv/assessment_system/system_logs/ollama.out 2>&1 &

# Download the Llama 3 model (approx 4.7GB)
ollama pull llama3
```

---

## 5. Application Deployment

### 5.1 Python Dependencies
```bash
sudo pip3 install flask requests
```

### 5.2 Deploy Core Components
1.  **Universal Grader**: Move `universal_grader.py` to `/srv/assessment_system/core/`.
2.  **Stateless Backend**: Deploy `backend_server.py` to your preferred application folder.
3.  **CLI Deployment**:
    ```bash
    cp synchro.py /usr/local/bin/synchro
    chmod +x /usr/local/bin/synchro
    ```

### 5.3 High-Persistence Startup
Launch the backend using `nohup` to ensure it survives terminal detachment.
```bash
nohup python3 backend_server.py > /srv/assessment_system/system_logs/flask.out 2>&1 & disown
```

---

## 6. Verification Checklist
*   [ ] Port 5005 is LISTENING (`netstat -tulnp | grep 5005`).
*   [ ] `sandbox_user` exists (`id sandbox_user`).
*   [ ] Ollama API is reachable (`curl http://localhost:11434/api/tags`).
*   [ ] Admin Panel is accessible at `http://<YOUR_IP>:5005/admin`.

---

## 🛡️ Security Note
This installation assumes the server is a dedicated node. Do not grant students `sudo` access, or the `sandbox_user` isolation can be bypassed.
