"""
Phantom Folders — Application Entry Point
Supports two modes:
  1. Desktop Mode (default): Opens a native frameless PyWebView window.
  2. Server Mode (--server): Runs as a headless web server accessible from any browser.

Usage:
  python main.py                          # Desktop app mode
  python main.py --server                 # Web server on 127.0.0.1:8001
  python main.py --server --host 0.0.0.0  # Web server on all interfaces
  python main.py --server --port 8000     # Web server on custom port
"""

import os
import sys
import time
import argparse
import threading
import urllib.request
import urllib.error

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from backend.server import app


def run_backend(host: str = "127.0.0.1", port: int = 8001):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port, log_level="error")


def wait_for_server(url: str, max_retries: int = 30) -> bool:
    """Poll URL until server responds."""
    for _ in range(max_retries):
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return True
        except (urllib.error.URLError, ConnectionResetError, OSError):
            time.sleep(0.2)
    return False


def run_desktop(host: str, port: int):
    """Launch the native desktop window using PyWebView."""
    try:
        import webview
    except ImportError:
        print("[ERROR] PyWebView is not installed. Install it with: pip install pywebview")
        print("[INFO]  Falling back to server mode. Open your browser to:")
        print(f"        http://{host}:{port}")
        run_backend(host, port)
        return

    # Start backend in background thread
    backend_thread = threading.Thread(target=run_backend, args=(host, port), daemon=True)
    backend_thread.start()
    wait_for_server(f"http://{host}:{port}/api/ping")

    class WindowApi:
        def minimize(self):
            if len(webview.windows) > 0:
                webview.windows[0].minimize()

        def maximize(self):
            if len(webview.windows) > 0:
                webview.windows[0].toggle_fullscreen()

        def close(self):
            if len(webview.windows) > 0:
                webview.windows[0].destroy()

    api = WindowApi()
    window = webview.create_window(
        'PHANTOM FOLDERS — Encrypted File Explorer',
        f'http://{host}:{port}',
        width=1280,
        height=800,
        frameless=True,
        transparent=False,
        easy_drag=True,
        js_api=api
    )

    webview.start(debug=False)
    os._exit(0)


def run_server(host: str, port: int):
    """Run as a headless web server."""
    print("================================================")
    print("   PHANTOM FOLDERS - Encrypted File Vault       ")
    print("   Server Mode                                  ")
    print("================================================")
    print(f"   URL: http://{host}:{port}")
    print("================================================")
    print()
    print("Press Ctrl+C to stop the server.")
    run_backend(host, port)


def main():
    parser = argparse.ArgumentParser(description="Phantom Folders — Encrypted File Vault")
    parser.add_argument("--server", action="store_true", help="Run in headless web server mode")
    parser.add_argument("--host", default=os.environ.get("PHANTOM_HOST", "127.0.0.1"), help="Server bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PHANTOM_PORT", "8001")), help="Server port (default: 8001)")
    args = parser.parse_args()

    if args.server:
        run_server(args.host, args.port)
    else:
        run_desktop(args.host, args.port)


if __name__ == "__main__":
    main()
