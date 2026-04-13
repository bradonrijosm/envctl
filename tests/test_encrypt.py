"""Tests for envctl.encrypt module."""

import os
import pytest

from envctl.encrypt import (
    EncryptError,
    encrypt_vars,
    decrypt_vars,
    store_encrypted_profile,
    load_encrypted_profile,
    delete_encrypted_profile,
    list_encrypted_profiles,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    monkeypatch.setenv("ENVCTL_STORE", str(store_file))
    yield tmp_path


SAMPLE = {"API_KEY": "secret123", "DEBUG": "true"}
PASS = "hunter2"


def test_encrypt_decrypt_roundtrip():
    token = encrypt_vars(SAMPLE, PASS)
    assert isinstance(token, str)
    result = decrypt_vars(token, PASS)
    assert result == SAMPLE


def test_encrypt_empty_passphrase_raises():
    with pytest.raises(EncryptError, match="Passphrase"):
        encrypt_vars(SAMPLE, "")


def test_decrypt_empty_passphrase_raises():
    token = encrypt_vars(SAMPLE, PASS)
    with pytest.raises(EncryptError, match="Passphrase"):
        decrypt_vars(token, "")


def test_decrypt_wrong_passphrase_raises():
    token = encrypt_vars(SAMPLE, PASS)
    with pytest.raises(EncryptError, match="wrong passphrase"):
        decrypt_vars(token, "wrongpass")


def test_decrypt_invalid_token_raises():
    with pytest.raises(EncryptError, match="Invalid encrypted token"):
        decrypt_vars("!!!not-base64!!!", PASS)


def test_store_and_load_encrypted_profile():
    store_encrypted_profile("prod", SAMPLE, PASS)
    result = load_encrypted_profile("prod", PASS)
    assert result == SAMPLE


def test_load_missing_encrypted_profile_raises():
    with pytest.raises(EncryptError, match="No encrypted profile found"):
        load_encrypted_profile("ghost", PASS)


def test_list_encrypted_profiles():
    store_encrypted_profile("alpha", SAMPLE, PASS)
    store_encrypted_profile("beta", {"X": "1"}, PASS)
    names = list_encrypted_profiles()
    assert "alpha" in names
    assert "beta" in names


def test_delete_encrypted_profile():
    store_encrypted_profile("temp", SAMPLE, PASS)
    delete_encrypted_profile("temp")
    assert "temp" not in list_encrypted_profiles()


def test_delete_missing_encrypted_profile_raises():
    with pytest.raises(EncryptError, match="No encrypted profile found"):
        delete_encrypted_profile("nonexistent")


def test_different_passphrases_produce_different_tokens():
    t1 = encrypt_vars(SAMPLE, "pass1")
    t2 = encrypt_vars(SAMPLE, "pass2")
    assert t1 != t2
