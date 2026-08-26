"""
Phantom Folders — Military-Grade Stream Crypto Engine
Provides 1:1 Bit-Exact AES-256-GCM Encryption with Scrypt Memory-Hard Key Derivation.
Zero compression, zero alteration, mathematically sound authenticated encryption.
"""

import os
import hashlib
import secrets
from typing import Generator, BinaryIO, Tuple
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt

CHUNK_SIZE = 64 * 1024  # 64 KB streaming buffer

def derive_key(password: str, salt: bytes) -> bytes:
    return scrypt(password.encode('utf-8'), salt, key_len=32, N=16384, r=8, p=1)

def hash_password(password: str, salt: bytes = None) -> Tuple[str, bytes]:
    if salt is None:
        salt = os.urandom(32)
    key = derive_key(password, salt)
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: bytes) -> bool:
    key = derive_key(password, salt)
    return secrets.compare_digest(key.hex(), stored_hash)

def encrypt_bytes(data: bytes, password: str) -> bytes:
    salt = os.urandom(32)
    key = derive_key(password, salt)
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return salt + nonce + tag + ciphertext

def decrypt_bytes(encrypted_payload: bytes, password: str) -> bytes:
    if len(encrypted_payload) < 60:
        raise ValueError("Invalid payload: data too short for GCM authentication headers")
    salt = encrypted_payload[:32]
    nonce = encrypted_payload[32:44]
    tag = encrypted_payload[44:60]
    ciphertext = encrypted_payload[60:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
    return cipher.decrypt_and_verify(ciphertext, tag)
