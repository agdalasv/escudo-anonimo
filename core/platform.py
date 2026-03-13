from __future__ import annotations
import os
import shutil


def is_nixos() -> bool:
    try:
        with open("/etc/os-release") as f:
            return "ID=nixos" in f.read()
    except Exception:
        return os.path.exists("/run/current-system")


def firewall_backend() -> str:
    # Prefer nftables: on NixOS nftables is native; iptables is often a
    # nft shim that can behave unexpectedly with NixOS's own ruleset.
    if shutil.which("nft"):
        return "nftables"
    if shutil.which("iptables"):
        return "iptables"
    raise RuntimeError(
        "Neither nft nor iptables found.\n"
        "Install nftables or iptables and try again."
    )
