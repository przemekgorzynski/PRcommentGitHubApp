#!python3
"""App to put comment in PR"""
import os
import time
import hashlib
import hmac
from fastapi import FastAPI, Request, HTTPException, Header
import requests
import jwt


app = FastAPI()

private_key_file_path = os.getenv('private_key_file_path')
app_id = os.getenv('app_id')
webhook_secret = os.getenv('webhook_secret')

def load_private_key(file_path):
    """Load the private key from a file"""
    with open(file_path, 'r', encoding="utf8") as file:
        private_key= file.read()
    return private_key

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

def generate_pr_comment(payload, installation_access_token):
    """Generate and put comment into PR"""
    headers = {
    'Authorization': f'token {installation_access_token}',
    'Accept': 'application/vnd.github.v3+json'
    }
    comment_url = payload['pull_request']['_links']['comments']['href']
    comment_content = {
        'body': """
## Pull Request Review
### Comment written by GitHub App

### Checklist:
- [ ] Fix bugs
- [ ] Tests have been added/updated
- [ ] Documentation has been updated

Happy Coding! :smile:
        """
    }
    response = requests.post(comment_url, headers=headers, json=comment_content, timeout=10)
    return response.json()

@app.get("/")
async def read_api():
    """Root API endpoint"""
    return {"message": "Main endpoint"}

@app.post("/webhook")
async def handle_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    """Webhook API endpoint"""
    payload = await request.json()  # returns JSON
    payload_body = await request.body() # returns bytes for signature verification
    verify_signature(payload_body, x_hub_signature_256, webhook_secret)  # verify incoming request

    # Run action only when PR is opened or reopened
    if payload['action'] in ['opened', 'reopened']:
        private_key = load_private_key(private_key_file_path)
        repository_owner = payload['repository']['owner']['login']
        jwt_token = generate_jwt(app_id, private_key)
        installation_access_token = get_installation_access_token(jwt_token, repository_owner)
        generate_pr_comment(payload, installation_access_token)
