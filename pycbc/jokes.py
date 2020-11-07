import requests


def generate():
    resp = requests.get('https://icanhazdadjoke.com/', headers={
        'Accept': 'text/plain',
        'User-Agent': 'https://github.com/mchestr'
    })
    resp.raise_for_status()
    return resp.text
