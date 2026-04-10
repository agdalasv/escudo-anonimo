from __future__ import annotations
import subprocess
import os
import threading
import http.server
import socketserver
import json
from typing import Callable
import shutil

from .config import cfg

_HOSTS_FILE = "/etc/hosts"
_MARKER_START = "# --- ESCUDO-ANONIMO-BLOCK-START ---"
_MARKER_END = "# --- ESCUDO-ANONIMO-BLOCK-END ---"

_NFT_TABLE = "escudo-bloqueo"

_BLOCKER_PORT = 8888
_BLOCKER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blocker_page")


class _BlockerHandler(http.server.SimpleHTTPRequestHandler):
    blocker_manager = None  # Se asigna desde BlockerManager

    def do_GET(self):
        host_header = self.headers.get("Host", "")
        
        if ":" in host_header:
            host, port_str = host_header.split(":", 1)
            port = int(port_str)
        else:
            host = host_header
            port = 80
        
        if host in ("127.0.0.1", "localhost"):
            pm = self.blocker_manager
            if pm and port != pm._listen_port:
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{pm._listen_port}/")
                self.end_headers()
                return
            host = "localhost"
        
        if self.blocker_manager and host in self.blocker_manager._temp_unlocked:
            import time
            if time.time() < self.blocker_manager._temp_unlocked.get(host, 0):
                unlock_port = self.blocker_manager._listen_port
                if unlock_port != 80:
                    self.send_response(302)
                    self.send_header("Location", f"http://{host}:{unlock_port}")
                    self.end_headers()
                else:
                    self.send_response(302)
                    self.send_header("Location", f"http://{host}")
                    self.end_headers()
                return

        try:
            with open(os.path.join(_BLOCKER_DIR, "blocked.html"), "r") as f:
                html = f.read()
            
            html = html.replace('id="blocked-url"', f'id="blocked-url">{host}')
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html.encode())))
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception:
            pass

    def do_POST(self):
        if self.path == "/unlock":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                password = data.get("password", "")
                site = data.get("site", "")
                
                stored = cfg().get("blocker", "password")
                if not stored or password == stored:
                    if self.blocker_manager and site:
                        import time
                        self.blocker_manager._temp_unlocked[site] = time.time() + self.blocker_manager._unlock_duration
                    
                    port = self.blocker_manager._listen_port if self.blocker_manager else _BLOCKER_PORT
                    redirect_url = f"http://{site}:{port}" if port != 80 else f"http://{site}"
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "redirect": redirect_url}).encode())
                else:
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False}).encode())
            except Exception:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


class BlockerManager:
    def __init__(self, log: Callable[[str], None]):
        self._log = log
        self._server = None
        self._server_thread = None
        self._blocked_sites = []
        self._temp_unlocked = {}  # sitename: unlock_expiry_time
        self._unlock_duration = 1800  # 30 minutos
        self._listen_port = _BLOCKER_PORT  # Puerto que escucha el servidor

    def is_installed(self) -> bool:
        return True

    def configure(self) -> None:
        self._log("[BLOCK] Configuring website blocker...")

    def start(self) -> None:
        enabled = cfg().get("blocker", "enabled")
        sites = list(cfg().get("blocker", "sites") or [])

        if not enabled or not sites:
            return

        self._log(f"[BLOCK] Blocking {len(sites)} websites...")

        self._blocked_sites = sites
        self._block_via_hosts(sites)
        self._block_via_firewall(sites)
        self._start_server()

        self._log("[BLOCK] Websites blocked.")

    def stop(self) -> None:
        self._stop_server()
        self._remove_hosts_block()
        self._remove_firewall_block()
        self._flush_dns()
        self._log("[BLOCK] Blocklist removed")

    def _start_server(self) -> None:
        if self._server:
            return
        
        os.chdir(_BLOCKER_DIR)
        
        _BlockerHandler.blocker_manager = self
        
        class _ReuseAddrServer(socketserver.TCPServer):
            allow_reuse_address = True
        
        ports = [_BLOCKER_PORT]
        
        for port in [80, 443]:
            try:
                test_server = _ReuseAddrServer(("", port), _BlockerHandler)
                test_server.server_close()
                ports.append(port)
            except Exception:
                pass
        
        self._server = _ReuseAddrServer(("", ports[0]), _BlockerHandler)
        
        self._listen_port = ports[0]
        
        if len(ports) > 1:
            self._log(f"[BLOCK] Server will also listen on ports: {', '.join(map(str, ports[1:]))}")
        
        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()
        self._log(f"[BLOCK] Server started on port {self._listen_port}")

    def _stop_server(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server = None
            self._server_thread = None
            self._log("[BLOCK] Server stopped")

    def _block_via_hosts(self, sites: list) -> None:
        self._remove_hosts_block()

        try:
            with open(_HOSTS_FILE, "a") as f:
                f.write(f"\n{_MARKER_START}\n")
                for site in sites:
                    site = site.strip()
                    if site:
                        f.write(f"127.0.0.1 {site}\n")
                        f.write(f"127.0.0.1 www.{site}\n")
                f.write(f"{_MARKER_END}\n")
            self._log(f"[BLOCK] Added {len(sites)} sites to /etc/hosts")
        except PermissionError as e:
            self._log(f"[BLOCK] ERROR: No permission to write /etc/hosts: {e}")
        except Exception as e:
            self._log(f"[BLOCK] ERROR writing hosts: {e}")

    def _remove_hosts_block(self) -> None:
        if not os.path.exists(_HOSTS_FILE):
            return
        try:
            with open(_HOSTS_FILE, "r") as f:
                lines = f.readlines()
            with open(_HOSTS_FILE, "w") as f:
                in_block = False
                for line in lines:
                    if _MARKER_START in line:
                        in_block = True
                        continue
                    if _MARKER_END in line:
                        in_block = False
                        continue
                    if not in_block:
                        f.write(line)
        except Exception as e:
            self._log(f"[BLOCK] Error removing hosts block: {e}")

    def _block_via_firewall(self, sites: list) -> None:
        self._remove_firewall_block()

        if not sites:
            return

        if shutil.which("nft"):
            try:
                subprocess.run(
                    ["nft", "add", "table", "ip", _NFT_TABLE],
                    capture_output=True
                )
                subprocess.run(
                    ["nft", "add", "chain", "ip", _NFT_TABLE, "output",
                     "{ policy accept }"],
                    capture_output=True
                )
                for site in sites:
                    site = site.strip()
                    if not site:
                        continue
                    subprocess.run(
                        ["nft", "add", "rule", "ip", _NFT_TABLE, "output",
                         "ip", "daddr", site, "redirect", "to", str(_BLOCKER_PORT)],
                        capture_output=True
                    )
            except Exception as e:
                self._log(f"[BLOCK] nft error: {e}")
        elif shutil.which("iptables"):
            try:
                for site in sites:
                    site = site.strip()
                    if not site:
                        continue
                    subprocess.run(
                        ["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp",
                         "-d", site, "--dport", "80", "-j", "REDIRECT",
                         "--to-port", str(_BLOCKER_PORT)],
                        capture_output=True
                    )
                    subprocess.run(
                        ["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp",
                         "-d", site, "--dport", "443", "-j", "REDIRECT",
                         "--to-port", str(_BLOCKER_PORT)],
                        capture_output=True
                    )
            except Exception as e:
                self._log(f"[BLOCK] iptables error: {e}")

    def _remove_firewall_block(self) -> None:
        if shutil.which("nft"):
            subprocess.run(
                ["nft", "delete", "table", "ip", _NFT_TABLE],
                capture_output=True
            )
        elif shutil.which("iptables"):
            subprocess.run(
                ["iptables", "-F", "OUTPUT"],
                capture_output=True
            )

    def _flush_dns(self) -> None:
        subprocess.run(["systemd-resolve", "--flush-caches"], capture_output=True)
        subprocess.run(["resolvectl", "flush-caches"], capture_output=True)

    def verify_password(self, password: str) -> bool:
        stored = cfg().get("blocker", "password")
        if not stored:
            return True
        return password == stored

    def add_site(self, site: str) -> None:
        sites = list(cfg().get("blocker", "sites") or [])
        if site not in sites:
            sites.append(site)
            cfg().set("blocker", "sites", sites)
            self._log(f"[BLOCK] Added {site} to blocklist.")

    def remove_site(self, site: str) -> None:
        sites = list(cfg().get("blocker", "sites") or [])
        if site in sites:
            sites.remove(site)
            cfg().set("blocker", "sites", sites)
            self._log(f"[BLOCK] Removed {site} from blocklist.")