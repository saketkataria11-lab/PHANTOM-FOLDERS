# Changelog — Phantom Folders

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-08-26 (Initial Production Release)

### 🚀 Core Features
- **Military-Grade Authenticated Encryption**: AES-256-GCM authenticated payload encryption with 1:1 bit-exact size and hash preservation (zero compression, zero loss).
- **GPU-Resistant Memory-Hard KDF**: Scrypt key derivation (`N=16384, r=8, p=1`, 32-byte key, 32-byte salt).
- **2.0 TB Secure Storage Subsystem**: Built-in capacity tracking engine and telemetry bar displaying real-time cluster utilization, free headroom, and object counts.
- **Encrypted Master Catalog**: Vault names, directory trees, file sizes, and metadata are encrypted with the master key (`sys_cat.bin`), ensuring real names always display upon login while maintaining 100% forensic disk invisibility.
- **Progressive Fierce Lockdown**: HMAC-SHA256 signed tamper-resistant lockout system (5 attempts → 15 min lock, 10+ attempts → 1 hour lock) that survives host reboots and process restarts.
- **Plausible Deniability**: Dual-slot envelope architecture supporting isolated decoy partitions.
- **DoD 5220.22-M 3-Pass Data Sanitization**: Multi-pass bit wiping on file deletion.

### 🌐 Universal Multi-OS & Hosting Architecture
- **Multi-OS Native Support**: Fully verified on **Windows 10/11/Server**, **macOS Sonoma/Ventura**, and **Linux (Ubuntu, Debian, Fedora, Arch, Alpine)**.
- **Desktop Application Mode**: Seamless frameless native desktop window powered by PyWebView with custom window controls and JARVIS dark theme.
- **Universal Headless Web Server Mode**: Self-hosted encrypted cloud vault mode (`python main.py --server --port 8000`) accessible from any browser or mobile device on the network.
- **Docker & Docker Compose**: 1-click multi-stage container deployment with persistent encrypted volumes.
- **Cross-Platform Native File Open**: Double-clicking files decrypts into ephemeral memory viewers and launches native system applications (`os.startfile` on Windows, `open` on macOS, `xdg-open` on Linux).
- **Automated Mythos-Grade Penetration Suite**: 6-part automated security test suite validating bit-exact integrity, zero plaintext on disk, restart survival, decoy isolation, and lockout resilience.
