from __future__ import annotations
from typing import Callable
from .tor      import TorManager
from .dnscrypt import DNSCryptManager
from .i2p      import I2PManager
from .blocker  import BlockerManager
from .firewall import FirewallManager
from .platform import is_nixos


class ConnectionManager:
    def __init__(self, log: Callable[[str], None]):
        self._log = log
        self._tor = TorManager(log)
        self._dns = DNSCryptManager(log)
        self._i2p = I2PManager(log)
        self._blk = BlockerManager(log)
        self._fw  = FirewallManager(log)
        self._layers: dict[str, bool] = {}

    def connect(self, use_tor: bool, use_dnscrypt: bool, use_i2p: bool, use_blocker: bool = False) -> None:
        if not (use_tor or use_dnscrypt or use_i2p or use_blocker):
            raise ValueError("Select at least one privacy layer.")

        # Validate installations before touching anything
        if use_tor and not self._tor.is_installed():
            raise RuntimeError("tor is not installed.")
        if use_dnscrypt and not self._dns.is_installed():
            raise RuntimeError("dnscrypt-proxy is not installed.")
        if use_i2p and not self._i2p.is_installed():
            raise RuntimeError("i2pd is not installed.")

        self._layers = {}

        if use_tor:
            self._tor.configure()
            self._tor.start()
            self._layers["tor"] = True

        if use_dnscrypt:
            self._dns.configure()
            self._dns.start()
            self._layers["dnscrypt"] = True

        if use_i2p:
            self._i2p.configure(use_tor=use_tor)
            self._i2p.start()
            self._layers["i2p"] = True

        # Block websites if enabled
        if use_blocker:
            self._blk.configure()
            self._blk.start()
            self._layers["blocker"] = True

        # NixOS: route system DNS through the correct service.
        # DNSCrypt takes priority over Tor DNS when both are active.
        if is_nixos():
            self._nixos_apply_dns(use_tor, use_dnscrypt)

        self._fw.apply(use_tor, use_dnscrypt, use_i2p)
        self._log("[OK] All selected layers are active.")

    def disconnect(self) -> None:
        # Restore system DNS first (before stopping services)
        if is_nixos():
            self._nixos_restore_dns()

        self._fw.remove()

        self._blk.stop()

        if self._layers.get("i2p"):
            self._i2p.stop()
        if self._layers.get("dnscrypt"):
            self._dns.stop()
        if self._layers.get("tor"):
            self._tor.stop()

        self._layers.clear()
        self._log("[OK] All layers disconnected.")

    # ── NixOS DNS routing ─────────────────────────────────────────

    def _nixos_apply_dns(self, use_tor: bool, use_dnscrypt: bool) -> None:
        """
        Route system DNS via systemd-resolved (resolvectl).

        Priority:
          1. DNSCrypt selected → DNS encrypted through dnscrypt-proxy
          2. Tor only           → DNS through Tor's anonymous DNSPort
        """
        if use_dnscrypt:
            self._log("[DNS] Routing system DNS → dnscrypt-proxy.")
            self._dns.nixos_redirect_dns()
        elif use_tor:
            self._log("[TOR] Routing system DNS → Tor DNSPort.")
            self._tor.nixos_redirect_dns()

    def _nixos_restore_dns(self) -> None:
        """Revert systemd-resolved to system defaults."""
        if self._layers.get("dnscrypt"):
            self._dns.nixos_restore_dns()
        elif self._layers.get("tor"):
            self._tor.nixos_restore_dns()
