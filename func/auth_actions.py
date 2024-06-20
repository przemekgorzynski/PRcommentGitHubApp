#auth_actions.py
import jwt
import hashlib
import hmac
import time
import requests

def verify_signature(payload_body: bytes, signature_header: str, webhook_secret: str):
    """Validate incoming webhook"""
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(webhook_secret.encode('utf-8'),msg=payload_body,digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")

def generate_jwt(appid, private_key):
    """Generate JWT token"""
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,  # 10 minutes
        'iss': int(appid)
    }
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token

def get_installation_access_token(jwt_token, repository_owner):
    """Get APP installation token"""
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = 'https://api.github.com/app/installations'
    installation_id = ""
    response = requests.get(url, headers=headers, timeout=10)
    installations = response.json()
    for installation in installations:
        if installation['account']['login'] == repository_owner:
            installation_id = installation['id']

    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    response = requests.post(url, headers=headers, timeout=10)
    response_data = response.json()
    return response_data['token']