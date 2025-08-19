# app/core/keys.py
import os, sys
from pathlib import Path
import logging

log = logging.getLogger("finabit-mcp")

def _bundle_base() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]

def _resolve(default_rel: tuple[str, ...], env_var: str | None) -> Path:
    if env_var:
        p = os.getenv(env_var)
        if p:
            return Path(p)
    return _bundle_base().joinpath(*default_rel)

PUBLIC_KEY_PATH = _resolve(("keys", "public.pem"), "PUBLIC_KEY_PATH")
if not PUBLIC_KEY_PATH.exists():
    alt = Path(__file__).resolve().parents[1] / "keys" / "public.pem"
    if alt.exists():
        PUBLIC_KEY_PATH = alt
    else:
        raise FileNotFoundError(f"public.pem not found at {PUBLIC_KEY_PATH}")

PUBLIC_KEY = PUBLIC_KEY_PATH.read_bytes()

priv_candidate = os.getenv("PRIVATE_KEY_PATH")
if priv_candidate:
    priv_path = Path(priv_candidate)
else:
    cand = _resolve(("keys", "private.pem"), None)
    priv_path = cand if cand.exists() else (Path(__file__).resolve().parents[1] / "keys" / "private.pem")

PRIVATE_KEY = priv_path.read_bytes() if priv_path and Path(priv_path).exists() else None
if PRIVATE_KEY is None:
    log.info("No private key found; continuing without signing (verification-only).")
