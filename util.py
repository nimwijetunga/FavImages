from flask import jsonify, make_response, request
from functools import wraps
from passlib.hash import sha256_crypt
import os
import jwt
import datetime


def send_json(status_code, body):
	return jsonify(body), status_code

def get_response_with_cookie(body, cookie_key, cookie_value):
	response = make_response(jsonify(body))
	response.set_cookie(cookie_key, value=cookie_value)
	return response

def encrypt_password(password):
	return sha256_crypt.encrypt(password)

def is_valid_password(password, saved_password):
	return sha256_crypt.verify(password, saved_password)

def encode_auth_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        os.getenv('SECRET_KEY'),
        algorithm='HS256'
    )

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, os.getenv('SECRET_KEY'))
        return True, payload['sub']
    except jwt.ExpiredSignatureError:
        return False, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return False, 'Invalid token. Please log in again.'

def authenticate_request(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		cookies = request.cookies or {}
		auth_token = cookies.get('auth_token')
		if not auth_token:
			return send_json(400, {'status': 'Failed', 'msg': 'Not Authenticated'},)
		decoded, resp = decode_auth_token(auth_token)
		if not decoded or not resp:
			return send_json(400, {'status': 'Failed', 'msg': str(resp)})
		user_id = resp
		return f(user_id, *args, **kwargs)
	return wrapper






