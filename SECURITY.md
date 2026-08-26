# Security Policy — Phantom Folders (v1.0.0)

## Threat Model & Security Posture

Phantom Folders is engineered with a **zero-knowledge, post-quantum resilient, defense-in-depth security architecture** designed to withstand state-level forensic analysis, GPU brute-force clusters, offline storage dumps, and side-channel tampering.

---

## 🔒 Cryptographic Specifications

### 1. **Key Derivation Function (KDF)**
* **Algorithm**: Scrypt (RFC 7914)
* **Parameters**: `N = 16384` (CPU/Memory Cost), `r = 8` (Block Size), `p = 1` (Parallelization), `dkLen = 32` (256-bit derived key)
* **Salt**: Cryptographically secure 32-byte (256-bit) CSPRNG random salt per operation.
* **Security Property**: Memory-hard and GPU/ASIC cluster brute-force resistant.

### 2. **Symmetric Authenticated Payload Encryption**
* **Algorithm**: AES-256-GCM (Galois/Counter Mode)
* **Key Length**: 256 bits (32 bytes)
* **Initialization Vector (Nonce)**: 96 bits (12 bytes) CSPRNG random per object
* **Authentication Tag**: 128 bits (16 bytes) GMAC tag ensuring 100% tamper-evident bit integrity.
* **Data Format**: 1:1 bit-exact preservation with **zero compression and zero payload alteration**.

### 3. **Zero Plaintext Storage Guarantee**
* **Vault Names, Folder Trees, and File Metadata**: Stored inside the **Encrypted Master Catalog** (`sys_cat.bin`), encrypted with AES-256-GCM.
* **Storage Blobs**: Stored as high-entropy opaque binary blobs (`.dat`) with random UUID keys (`obj_<hex>`).
* **Forensic Cleanliness**: Zero SQL headers, zero filenames, zero folder names, zero credentials appear anywhere on disk in plaintext.

### 4. **Progressive Fierce Lockout Engine**
* **Integrity Guard**: Lockout state is cryptographically signed using `HMAC-SHA256`.
* **Attempts 1–4**: Real-time remaining attempts warning.
* **5 Failed Attempts**: Immediate **15-MINUTE SYSTEM LOCKDOWN**.
* **10+ Failed Attempts**: Immediate **1-HOUR FIERCE LOCKDOWN**.
* **Anti-Bypass**: Persists across application restarts, process terminations, and host reboots. Any modification to the lockout file triggers an automatic maximum 1-hour lockdown.

### 5. **Plausible Deniability Partitioning**
* **Dual-Slot Envelopes**: Each vault supports a primary slot and an independent decoy slot.
* **Cryptographic Isolation**: Decoy authentication yields a completely segregated file tree with zero cryptographic or physical linkage to the primary confidential vault partition.

### 6. **Data Sanitization (DoD 5220.22-M)**
* Deleted files undergo a **3-pass overwriting sequence** (Pass 1: `0x00`, Pass 2: `0xFF`, Pass 3: CSPRNG random bytes) with forced disk flush before inode unlinking.

---

## 🛡️ Reporting a Vulnerability

If you discover a security vulnerability, please submit a responsible disclosure report via GitHub Security Advisories or contact the maintainers directly. Vulnerabilities will be addressed with emergency patches within 24 hours.
