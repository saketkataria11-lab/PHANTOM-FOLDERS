"""
Phantom Folders — Cross-Platform Storage & Hardware Identity Engine
Resolves isolated local cryptographic storage directories and host profiles across:
- Windows (10/11/Server): %LOCALAPPDATA%/.phantom_vault (Hidden+System attrs)
- macOS (Sonoma/Ventura/Monterey): ~/Library/Application Support/phantom_vault (0700 permissions)
- Linux (Ubuntu/Debian/Arch/Fedora/Alpine): ~/.local/share/phantom_vault (0700 permissions)
- Cloud / Docker / NAS: Environment variable $PHANTOM_STORAGE_DIR
"""

import os
import platform
import socket
from pathlib import Path


def get_storage_root() -> Path:
    """Resolve the isolated local cryptographic directory for the current operating system."""
    custom = os.environ.get('PHANTOM_STORAGE_DIR')
    if custom:
        return Path(custom)
    system = platform.system()
    if system == 'Windows':
        base = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
        return base / '.phantom_vault'
    elif system == 'Darwin':
        return Path.home() / 'Library' / 'Application Support' / 'phantom_vault'
    else:
        xdg = os.environ.get('XDG_DATA_HOME', '')
        if xdg:
            return Path(xdg) / 'phantom_vault'
        return Path.home() / '.local' / 'share' / 'phantom_vault'


def safe_set_hidden(path: Path):
    """Apply OS-level protection (Windows Hidden+System attributes or Unix 0700 permissions)."""
    try:
        if platform.system() == 'Windows':
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x02 | 0x04)
        else:
            os.chmod(str(path), 0o700)
    except Exception:
        pass


def safe_clear_hidden(path: Path):
    """Temporarily lift attributes on Windows for atomic file writes."""
    try:
        if platform.system() == 'Windows':
            import ctypes
            if path.exists():
                ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x80)
    except Exception:
        pass


def safe_write_bytes(path: Path, data: bytes):
    """Write binary data safely with attribute protection."""
    safe_clear_hidden(path)
    path.write_bytes(data)
    safe_set_hidden(path)


def get_system_identity() -> dict:
    """Return local host identity and isolated system vault profile."""
    hostname = socket.gethostname()
    system = platform.system()
    release = platform.release()
    arch = platform.machine()
    os_name = "Windows" if system == "Windows" else ("macOS" if system == "Darwin" else "Linux")
    display_name = f"{hostname} ({os_name} {release})"
    return {
        "hostname": hostname,
        "os_type": os_name,
        "os_release": release,
        "architecture": arch,
        "display_name": display_name,
        "storage_root": str(STORAGE_ROOT),
        "is_isolated": True
    }


STORAGE_ROOT = get_storage_root()
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
safe_set_hidden(STORAGE_ROOT)
