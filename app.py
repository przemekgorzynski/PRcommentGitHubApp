#!python3
"""App to manage PRs"""
import os
import time
from fastapi import FastAPI, Request, HTTPException, Header
from func.pr_actions import set_pr_comment, set_pr_status
from func.auth_actions import verify_signature, generate_jwt, get_installation_access_token

app = FastAPI()

private_key_file_path = os.getenv('private_key_file_path')
app_id = os.getenv('app_id')
webhook_secret = os.getenv('webhook_secret')

def load_private_key(file_path):
    """Load the private key from a file"""
    with open(file_path, 'r', encoding="utf8") as file:
        private_key= file.read()
    return private_key

###########################################################
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
    if payload['action'] in ['opened', 'reopened', 'synchronize', 'edited']:
        private_key = load_private_key(private_key_file_path)
        repository_owner = payload['repository']['owner']['login']
        jwt_token = generate_jwt(app_id, private_key)
        installation_access_token = get_installation_access_token(jwt_token, repository_owner)
        pr_number = payload['number']
        pr_context = "Shelter Scanner"
        pr_comment = {
        'body': """
## Pull Request Review
Shelter Scanner! :smile:
        """
        }
        set_pr_comment(payload, installation_access_token, pr_number, pr_comment)
        set_pr_status(payload, installation_access_token, pr_number, "pending", "Scanning in progress", pr_context)
        time.sleep(120)
        set_pr_status(payload, installation_access_token, pr_number, "success", "Scanning completed", pr_context)
