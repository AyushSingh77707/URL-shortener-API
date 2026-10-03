import secrets
import hashlib
import base64

def generate_pkce_pair():
    code_verifier=secrets.token_urlsafe(64)
    digest=hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge=base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
    return code_verifier,code_challenge

