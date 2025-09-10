# app/crypto.py
import os, hmac
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DEFAULT_ITER = 200_000
NONCE_LEN = 12
SALT_LEN = 16

def gen_salt(n: int = SALT_LEN) -> bytes:
    return os.urandom(n)

def derive_key(master_password: str, salt: bytes, iterations: int = DEFAULT_ITER) -> bytes:
    pw = master_password.encode("utf-8")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    key = kdf.derive(pw)
    return key  # 32 bytes

def encrypt(key: bytes, plaintext: bytes, aad: bytes | None = None) -> bytes:
    nonce = os.urandom(NONCE_LEN)
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext, aad)
    return nonce + ct  # [12B nonce][cipher+tag]

def decrypt(key: bytes, blob: bytes, aad: bytes | None = None) -> bytes:
    nonce, ct = blob[:NONCE_LEN], blob[NONCE_LEN:]
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, aad)

def make_verifier(key: bytes) -> bytes:
    # 헤더 검증용: 고정 문자열을 AEAD로 암호화해 저장, 해제 시 복호 성공 여부로 키 검증
    return encrypt(key, b"vault-ok")

def check_verifier(key: bytes, verifier_blob: bytes) -> bool:
    try:
        return decrypt(key, verifier_blob) == b"vault-ok"
    except Exception:
        return False

def b64e(b: bytes) -> str:
    return urlsafe_b64encode(b).decode("ascii")

def b64d(s: str) -> bytes:
    return urlsafe_b64decode(s.encode("ascii"))
