from __future__ import annotations
import subprocess
import shutil
import os
import time
from typing import Callable

from .config import cfg
from .platform import is_nixos

_CONFIG_PATHS = [
    "/etc/i2pd/i2pd.conf",
    "/etc/i2p/i2p.conf",
]
_BAK_SUFFIX  = ".entropy-shield.bak"
_TOR_PROXY   = "ntcpproxy = socks://127.0.0.1:9050\n"
_TOR_MARKER  = "# entropy-shield-tor-proxy"


class I2PManager:
    def __init__(self, log: Callable[[str], None]):
        self._log = log
        self._config: str | None = None
        self._was_active: bool = False
        self._tor_injected: bool = False

    def is_installed(self) -> bool:
        return bool(shutil.which("i2pd") or shutil.which("i2prouter"))

    def configure(self, use_tor: bool = False) -> None:
        self._log("[I2P] Configuring i2pd...")
        self._was_active = self._service_active("i2pd")

        if is_nixos():
            self._log(
                "[I2P] NixOS detected — i2pd config is managed by the NixOS module. "
                "Skipping config file modification."
            )
            return

        self._config = self._find_config()

        if use_tor:
            bak = self._config + _BAK_SUFFIX
            if not os.path.exists(bak):
                shutil.copy2(self._config, bak)

            with open(self._config, "r") as f:
                content = f.read()

            if _TOR_MARKER not in content:
                with open(self._config, "a") as f:
                    f.write(f"\n{_TOR_MARKER}\n{_TOR_PROXY}")
                self._tor_injected = True

        self._log("[I2P] i2pd configured.")

    def start(self) -> None:
        self._log("[I2P] Starting i2pd...")
        r = subprocess.run(["systemctl", "restart", "i2pd"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Failed to start i2pd: {r.stderr.strip()}")
        self._wait_active("i2pd", timeout=15)
        self._log("[I2P] i2pd active. HTTP proxy: 127.0.0.1:4444")

    def stop(self) -> None:
        self._log("[I2P] Stopping i2pd...")

        subprocess.run(["systemctl", "stop", "i2pd"], capture_output=True)

        if is_nixos():
            self._log("[I2P] i2pd stopped.")
            return

        if self._config and self._tor_injected:
            bak = self._config + _BAK_SUFFIX
            if os.path.exists(bak):
                shutil.copy2(bak, self._config)
                os.unlink(bak)
            self._tor_injected = False

        if self._was_active:
            subprocess.run(["systemctl", "start", "i2pd"], capture_output=True)

        self._log("[I2P] i2pd stopped.")

    def _find_config(self) -> str:
        for path in _CONFIG_PATHS:
            if os.path.exists(path):
                return path
        raise RuntimeError("i2pd config not found. Is i2pd installed?")

    def _service_active(self, name: str) -> bool:
        r = subprocess.run(["systemctl", "is-active", name],
                           capture_output=True, text=True)
        return r.stdout.strip() == "active"

    def _wait_active(self, name: str, timeout: int = 15) -> None:
        for _ in range(timeout):
            if self._service_active(name):
                return
            time.sleep(1)
