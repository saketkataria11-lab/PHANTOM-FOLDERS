"""
Phantom Folders — Application Entry Point & Resilient Launcher
Features:
- Dynamic Free Port Allocation (Prevents Port Conflict & 'Can't Reach Page' Errors)
- Synchronous Backend Readiness Handshake
- Native PyWebView Desktop Window with Zero Console Popup
- Automatic Browser Fallback if WebView2 is Unavailable
- Headless Web Server Mode (--server)
"""

import os
import sys

# Prevent pythonw.exe from crashing on print statements when running detached in background
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

import time
import socket
import argparse
import threading
import urllib.request
import urllib.error

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from backend.server import app


def find_available_port(host: str = "127.0.0.1", start_port: int = 8001, max_attempts: int = 50) -> int:
    """Find a free TCP port to prevent bind conflicts."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return start_port


def wait_for_server(url: str, max_retries: int = 60, delay: float = 0.1) -> bool:
    """Poll URL until backend server responds 200 OK."""
    for _ in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PhantomLauncher/1.0'})
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(delay)
    return False


def run_desktop(host: str, port: int):
    """Launch the native desktop window with dynamic port discovery and auto-fallback."""
    allocated_port = find_available_port(host, port)
    target_url = f"http://{host}:{allocated_port}"

    # Start uvicorn server in a background thread
    config = uvicorn.Config(app, host=host, port=allocated_port, log_level="error")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Guaranteed synchronous handshake before opening window
    is_ready = wait_for_server(f"{target_url}/api/ping", max_retries=60, delay=0.1)
    if not is_ready:
        time.sleep(0.5)

    launched_gui = False
    try:
        import webview

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
            target_url,
            width=1280,
            height=800,
            frameless=False,
            easy_drag=False,
            js_api=api
        )

        webview.start(debug=False)
        launched_gui = True
    except Exception:
        launched_gui = False

    # If PyWebView was not available or encountered an issue, open default browser
    if not launched_gui:
        import webbrowser
        webbrowser.open(target_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    server.should_exit = True
    os._exit(0)


def run_server(host: str, port: int):
    """Run as a headless web server."""
    allocated_port = find_available_port(host, port)
    print("================================================")
    print("   PHANTOM FOLDERS - Encrypted File Vault       ")
    print("   Server Mode                                  ")
    print("================================================")
    print(f"   URL: http://{host}:{allocated_port}")
    print("================================================")
    print()
    print("Press Ctrl+C to stop the server.")
    config = uvicorn.Config(app, host=host, port=allocated_port, log_level="info")
    server = uvicorn.Server(config)
    server.run()


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
