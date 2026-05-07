import datetime
import os

import jwt

# Get SECRET_KEY — file path provided via env var, default to local key.txt
if 'SECRET_KEY' in os.environ:
    key_file = os.environ['SECRET_KEY']
else:
    key_file = 'key.txt'

with open(key_file, 'r') as file:
    data = file.read().replace('\n', '')
SECRET_KEY_VALUE = data


def encode_auth_token(user_id):
    """
    Generates the Auth Token (HS256-signed JWT).
    :return: encoded JWT string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            SECRET_KEY_VALUE,
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token and verifies its HMAC signature.
    :return: user_id if valid, error string if not
    """
    try:
        # Note: lab code disabled signature verification with verify_signature=False.
        # We enable it here so forged tokens are rejected. Same algorithm (HS256), same secret.
        payload = jwt.decode(auth_token, SECRET_KEY_VALUE, algorithms=["HS256"])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
