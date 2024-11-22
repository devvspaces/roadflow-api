import requests


def get_github_account(access_token: str):
    base_url = 'https://api.github.com'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    account = requests.get(f'{base_url}/user', headers=headers).json()
    emails: list = requests.get(f'{base_url}/user/emails', headers=headers).json()
    primary_email = None
    for email in emails:
        if email['primary']:
            primary_email = email
            break
    return account, primary_email
        