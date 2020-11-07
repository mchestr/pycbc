import requests


def generate(config):
    resp = requests.get('https://icanhazdadjoke.com/', headers={
        'Accept': 'text/plain',
        'User-Agent': config.sender_email,
    })
    resp.raise_for_status()
    return resp.text
