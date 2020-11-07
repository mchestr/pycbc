from cryptography.fernet import Fernet

from pycbc import json


def encrypt(key: str, data: dict):
    fernet = Fernet(key.encode('utf-8'))
    return fernet.encrypt(json.dumps(data).encode('utf-8')).decode('utf-8')


def decrypt(key: str, data: str, ttl=1800):
    fernet = Fernet(key.encode('utf-8'))
    return json.loads(fernet.decrypt(data.encode('utf-8'), ttl=ttl).decode('utf-8'))
