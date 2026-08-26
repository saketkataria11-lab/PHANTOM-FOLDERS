# Contributing to Phantom Folders

Thank you for your interest in contributing to **Phantom Folders**!

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm` (for frontend changes)
- `git`

### 2. Clone and Install
```bash
git clone https://github.com/YOUR_USERNAME/PhantomFolders.git
cd PhantomFolders

# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies (if editing UI)
npm install
```

### 3. Running in Development
```bash
# Terminal 1: Start FastAPI backend in server mode
python main.py --server --port 8001

# Terminal 2: Start Vite live-reload dev server
npm run dev
```

### 4. Running the Security Test Suite
Before submitting any Pull Request, you **MUST** run the automated penetration test suite:
```bash
python test_security_audit.py
```
All 6 tests must pass 100%.

### 5. Building Frontend for Production
```bash
npm run build
```

---

## 📜 Pull Request Guidelines
- Ensure all Python code adheres to PEP 8 standards.
- Maintain zero plaintext storage guarantees.
- Include unit/penetration tests for any new cryptographic or storage feature.
- Verify cross-platform compatibility across Windows, macOS, and Linux.
