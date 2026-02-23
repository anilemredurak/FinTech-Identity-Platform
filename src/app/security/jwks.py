from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

from app.core.config import settings


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def get_jwks() -> dict:
    # Load public key and convert to minimal JWK
    with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as f:
        pub = serialization.load_pem_public_key(f.read(), backend=default_backend())

    if not isinstance(pub, rsa.RSAPublicKey):
        raise RuntimeError("Only RSA public keys supported for JWKS")

    numbers = pub.public_numbers()
    e = numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
    n = numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")

    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": settings.JWT_ALGORITHM,
        "kid": hashlib.sha256(n).hexdigest(),
        "n": _b64url(n),
        "e": _b64url(e),
    }
    return {"keys": [jwk]}
