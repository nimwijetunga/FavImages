from flask import jsonify, make_response, request
from functools import wraps
from passlib.hash import sha256_crypt
import os
import jwt
import datetime
import boto
from boto.s3.key import Key
import urllib2
import StringIO


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

def upload_to_s3(name, image_url):
	conn = boto.connect_s3(os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), host='s3.us-east-1.amazonaws.com')
	bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
	bucket = conn.get_bucket(bucket_name)
	file_object = urllib2.urlopen(image_url)           # 'Like' a file object
	fp = StringIO.StringIO(file_object.read())
	k = Key(bucket)
	ext = file_object.headers.getheader('content-type').split('/')[1]
	key = 'images/%s.%s' % (name, ext)
	k.key = key
	k.set_contents_from_file(fp)
	return "https://%s.s3.amazonaws.com/%s" % (bucket_name, key)

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
