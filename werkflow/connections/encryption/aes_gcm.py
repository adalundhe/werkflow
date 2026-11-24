import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from werkflow.connections.env import Env


class AESGCMFernet:

    def __init__(self, env: Env) -> None:
        self.secret = env.MERCURY_SYNC_AUTH_SECRET
        if not self.secret:
            raise ValueError("MERCURY_SYNC_AUTH_SECRET must be set.")
        raw_secret = (
            self.secret.encode("utf-8")
            if isinstance(self.secret, str)
            else self.secret
        )
        self._key = (
            raw_secret
            if len(raw_secret) == 32
            else hashlib.sha256(raw_secret).digest()
        )

    def encrypt(self, data: bytes) -> bytes:
        nonce = secrets.token_bytes(12)
        return nonce + AESGCM(self._key).encrypt(nonce, data, b"")
    
    def decrypt(self, data: bytes) -> bytes:
        if len(data) < 28:
            raise ValueError("Ciphertext is too short to contain nonce and authentication tag.")
        nonce = data[:12]
        return AESGCM(self._key).decrypt(nonce, data[12:], b"")
    
