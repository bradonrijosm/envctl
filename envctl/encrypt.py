"""Encryption support for environment variable profiles."""

import base64
import hashlib
import json
import os
from typing import Dict

from envctl.storage import get_store_path


class EncryptError(Exception):
    pass


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """Simple XOR cipher (repeating key)."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt_vars(variables: Dict[str, str], passphrase: str) -> str:
    """Encrypt a dict of variables to a base64-encoded string."""
    if not passphrase:
        raise EncryptError("Passphrase must not be empty.")
    raw = json.dumps(variables).encode()
    key = _derive_key(passphrase)
    encrypted = _xor_bytes(raw, key)
    return base64.b64encode(encrypted).decode()


def decrypt_vars(token: str, passphrase: str) -> Dict[str, str]:
    """Decrypt a base64-encoded token back to a dict of variables."""
    if not passphrase:
        raise EncryptError("Passphrase must not be empty.")
    try:
        encrypted = base64.b64decode(token.encode())
    except Exception as exc:
        raise EncryptError(f"Invalid encrypted token: {exc}") from exc
    key = _derive_key(passphrase)
    raw = _xor_bytes(encrypted, key)
    try:
        return json.loads(raw.decode())
    except json.JSONDecodeError as exc:
        raise EncryptError("Decryption failed: wrong passphrase or corrupted data.") from exc


def _get_encrypted_path() -> str:
    store = get_store_path()
    return os.path.join(os.path.dirname(store), "encrypted.json")


def _load_encrypted() -> Dict[str, str]:
    path = _get_encrypted_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_encrypted(data: Dict[str, str]) -> None:
    path = _get_encrypted_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def store_encrypted_profile(profile_name: str, variables: Dict[str, str], passphrase: str) -> None:
    """Encrypt and persist a profile's variables under the given name."""
    token = encrypt_vars(variables, passphrase)
    data = _load_encrypted()
    data[profile_name] = token
    _save_encrypted(data)


def load_encrypted_profile(profile_name: str, passphrase: str) -> Dict[str, str]:
    """Load and decrypt a previously stored encrypted profile."""
    data = _load_encrypted()
    if profile_name not in data:
        raise EncryptError(f"No encrypted profile found: '{profile_name}'.")
    return decrypt_vars(data[profile_name], passphrase)


def delete_encrypted_profile(profile_name: str) -> None:
    """Remove an encrypted profile entry."""
    data = _load_encrypted()
    if profile_name not in data:
        raise EncryptError(f"No encrypted profile found: '{profile_name}'.")
    del data[profile_name]
    _save_encrypted(data)


def list_encrypted_profiles():
    """Return names of all stored encrypted profiles."""
    return list(_load_encrypted().keys())
