# pr_actions.py
import requests

def set_pr_comment(payload: dict, installation_access_token: str, pr_number: int, pr_comment: str):
    """Generate and put comment into PR"""
    headers = {
    'Authorization': f'token {installation_access_token}',
    'Accept': 'application/vnd.github.v3+json'
    }
    comment_url = payload['pull_request']['_links']['comments']['href']
    response = requests.post(comment_url, headers=headers, json=pr_comment, timeout=10)
    try:
        response.raise_for_status()
        print(f"Successfully set comment in PR number {pr_number}")  # Debugging
    except requests.exceptions.HTTPError as e:
        print(f"Failed to set comment in PR number {pr_number}")
        print(f"Response: {response.text}")
        return {"error": str(e), "response": response.text}
    return response.json()

def set_pr_status(payload: dict, installation_access_token: str, pr_number: int, pr_state: str, pr_description: str, pr_context: str):
    headers = {
    'Authorization': f'token {installation_access_token}',
    'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        "state": pr_state,
        "description": pr_description,
        "context": pr_context
    }
    
    status_url = payload['pull_request']['statuses_url']
    response = requests.post(status_url, headers=headers, json=data, timeout=10)
    try:
        response.raise_for_status()
        print(f"Successfully set PR number {pr_number} status: {pr_state}")  # Debugging
    except requests.exceptions.HTTPError as e:
        print(f"Failed to set PR number status: {e}")
        print(f"Response: {response.text}")
        return {"error": str(e), "response": response.text}
    return response.json()