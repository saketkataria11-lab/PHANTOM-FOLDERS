# Phantom Folders

**Military-grade encrypted file vault with zero-knowledge architecture, plausible deniability, and a futuristic JARVIS-style interface.**

Phantom Folders is a self-hosted encrypted file explorer that stores your files using AES-256-GCM encryption with Scrypt memory-hard key derivation. No files are stored in plaintext — ever. Runs as a native desktop app or a web server accessible from any browser.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🛡️ Security Architecture

| Layer | Technology | Details |
|-------|-----------|---------|
| **Encryption** | AES-256-GCM | Authenticated encryption with zero compression (1:1 bit-exact) |
| **Key Derivation** | Scrypt | Memory-hard KDF (N=16384, r=8, p=1) — GPU/ASIC resistant |
| **Password Storage** | One-way Scrypt Hash | 32-byte key + 32-byte salt — password is NEVER stored |
| **Integrity** | HMAC-SHA256 | Tamper-resistant lockout state and auth verifiers |
| **Plausible Deniability** | Dual-Slot Envelopes | Independent encrypted slots — real and decoy vaults |
| **Fierce Lockout** | Progressive Lockdown | 5 fails → 15 min lock, 10+ fails → 1 hour lock, persists across reboots |
| **Disk Forensics** | Zero Plaintext | No vault names, file names, or metadata exist in plaintext on disk |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (required)
- **Node.js 18+** (only if you want to rebuild the frontend — a pre-built bundle is included)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PhantomFolders.git
cd PhantomFolders

# Install Python dependencies
pip install -r requirements.txt

# Launch (Desktop Mode — opens native window)
python main.py

# Launch (Web Server Mode — access from any browser)
python main.py --server --port 8000
```

### Docker (1-Click Deployment)

```bash
docker compose up -d
# Access at http://localhost:8000
```

---

## 💻 Usage Modes

### 1. Desktop App Mode (Default)
```bash
python main.py
```
Opens a frameless native desktop window with the JARVIS-style encrypted file explorer.

### 2. Web Server Mode (Self-Hosted / Remote Access)
```bash
python main.py --server --host 0.0.0.0 --port 8000
```
Runs as a headless web server. Access from any device on your network at `http://<your-ip>:8000`.

### 3. Docker Container Mode
```bash
docker compose up -d
```
Runs in an isolated container with persistent encrypted storage via Docker volumes.

---

## 📁 Project Structure

```
PhantomFolders/
├── backend/
│   ├── __init__.py          # Package init
│   ├── storage_path.py      # Cross-platform storage path resolution
│   ├── crypto_engine.py     # AES-256-GCM + Scrypt KDF engine
│   ├── auth.py              # Scrypt authentication + fierce lockout
│   ├── web_store.py         # Persistent encrypted object store
│   ├── vault_manager.py     # Dual-slot cryptographic vault manager
│   └── server.py            # FastAPI REST API + static file serving
├── src/                     # React frontend source (JARVIS theme)
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   └── components/
│       ├── LoginScreen.jsx
│       ├── VaultList.jsx
│       ├── FileExplorer.jsx
│       ├── CreateVaultModal.jsx
│       ├── ContextMenu.jsx
│       ├── StatusBar.jsx
│       └── Titlebar.jsx
├── dist/                    # Pre-built production frontend bundle
├── main.py                  # Application entry point (Desktop + Server modes)
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies (frontend dev only)
├── vite.config.mjs          # Vite build configuration
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker Compose deployment
├── launch.bat               # Windows launcher
├── launch.sh                # Linux/macOS launcher
├── test_security_audit.py   # Automated penetration test suite
├── LICENSE                  # MIT License
└── .gitignore
```

---

## 🔐 Features

### Encrypted File Management
- **Import files** via drag-and-drop or file picker — encrypted instantly with AES-256-GCM
- **Double-click to open** — decrypts to ephemeral temp and opens in native system viewer
- **Export / Download** — decrypts 1:1 bit-exact copy (zero compression, zero alteration)
- **Create folders** — full hierarchical directory structure inside each vault

### Vault System
- **Multiple vaults** — each vault has its own independent encryption password
- **Plausible deniability** — optional decoy password shows a separate, fake set of files
- **Lock / Unlock** — purges decrypted data from memory when locked

### Security
- **Zero plaintext on disk** — vault names, file names, and all metadata are encrypted
- **Fierce lockout** — 5 failed attempts triggers 15-minute lockdown, 10+ triggers 1-hour lockdown
- **Tamper-resistant** — lockout state is HMAC-SHA256 signed; rebooting cannot bypass it
- **Session management** — 30-minute auto-expiry with ephemeral UUID tokens

### Cross-Platform
- **Windows, macOS, Linux** — automatic OS-specific storage path resolution
- **Docker** — containerized deployment with persistent volumes
- **Custom storage** — set `PHANTOM_STORAGE_DIR` environment variable to use any path

---

## 🧪 Security Audit

Run the automated Mythos-grade penetration test suite:

```bash
python test_security_audit.py
```

Tests include:
1. **Multi-Format Bit-Exact Integrity** — SHA-256 verification across PDF, PNG, ZIP, DOCX
2. **Persistent Scrypt Auth & Zero Plaintext Inspection** — no passwords on disk
3. **Vault Persistence & Restart Survival** — data survives process restarts
4. **Plausible Deniability Decoy Isolation** — decoy space cannot access real files
5. **Fierce Progressive Lockout & Tamper Resistance** — lockout persists across reboots
6. **Forensic Disk & Path Traversal Injection Audit** — zero plaintext on disk

---

## ⚙️ Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `PHANTOM_STORAGE_DIR` | Custom storage directory path | OS-specific (see below) |
| `PHANTOM_PORT` | Server port | `8001` |
| `PHANTOM_HOST` | Server bind address | `127.0.0.1` |

### Default Storage Locations

| OS | Path |
|----|------|
| Windows | `%LOCALAPPDATA%\.phantom_vault` |
| macOS | `~/Library/Application Support/phantom_vault` |
| Linux | `~/.local/share/phantom_vault` |

---

## 🔧 Development

### Rebuild Frontend
```bash
npm install
npm run build
```

### Run in Development Mode
```bash
# Terminal 1: Start backend
python main.py --server --port 8001

# Terminal 2: Start Vite dev server
npm run dev
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

This software is provided for educational and personal use. The authors are not responsible for any misuse. Always comply with local laws and regulations regarding encryption software.
