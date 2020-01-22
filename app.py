from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import util
import image_handler
from util import authenticate_request
from flask_restplus import Api, Resource, fields


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app=app)

login_auth = api.namespace('login', description='Authentication API\'s')
images = api.namespace('images', description='Image Saving/Retrieval API\'s')

import models

@images.route("/images")
class Images(Resource):
	@api.doc(params={'text': 'Text to be sentiment analyzed'})
	@authenticate_request
	def get(user_id, self):
		image_ids = image_handler.create_image_and_add_to_cache('test_url', 100, 300, 1)
		return jsonify({'status': 'Success', 'image_ids': image_ids})

	image_objects = api.schema_model('image_objs', {
	    'properties': {
	        'title': {
	            'type': 'string'
	        },
	        'url': {
	            'type': 'string'
	        },
	        'width': {
	            'type': 'float'
	        },
	        'height': {
	            'type': 'float'
	        },
	        'description': {
	        	'type': 'string'
	        }
	    },
	    'type': 'object'
	})

	@images.expect(image_objects)
	@authenticate_request
	def post(user_id, self):
		image_obj = request.get_json() or {}
		if not image_obj:
			return make_response(jsonify(status='Failed'), 400)
		image_ids = image_handler.create_images_add_to_cache_db_es([image_obj])
		return make_response(jsonify(image_ids=image_ids))

@login_auth.route("/signup")
class SignUp(Resource):
	signup_request = login_auth.model("Insert_user_data", {
    	'username': fields.String(required=False),
    	'password': fields.String(required=True),
    	'email': fields.String(required=True)
    })
	@login_auth.expect(signup_request)
	def post(self):
		try:
			body = request.get_json()
			if not body:
				return make_response(jsonify(status='Failed', token=None), 400)
			user_id = body.get('username')
			password = body.get('password')
			email = body.get('email')
			if not user_id or not password:
				return make_response(jsonify(status='Failed', token=None), 400)
			user_exists = bool(db.session.query(models.User).filter_by(user_id=user_id).first())
			if user_exists:
				return make_response(jsonify(status='Failed', token=None, msg='User Already Exists!'), 400)
			password = util.encrypt_password(password)
			auth_token = util.encode_auth_token(user_id)
			user = models.User(user_id=user_id, password=password, email=email)
			db.session.add(user)
			db.session.commit()
			return util.get_response_with_cookie({'status': 'Success', 'token': auth_token}, 'auth_token', auth_token)
		except Exception as e:
			db.session.rollback()
			return make_response(jsonify(status='Failed', token=None), 500)

@login_auth.route('/login')
class Login(Resource):
	login_request = login_auth.model("Insert_user_data", {
		'username': fields.String(required=False),
		'password': fields.String(required=True),
	})
	@login_auth.expect(login_request)
	def post(self):
		try:
			body = request.get_json()
			if not body:
				return make_response(jsonify(status='Failed', token=None), 400)
			user_id = body.get('username')
			password = body.get('password')
			if not user_id or not password:
				return make_response(jsonify(status='Failed', token=None), 400)
			user = db.session.query(models.User).filter_by(user_id=user_id).first()
			if not user:
				return make_response(jsonify(status='Failed', token=None, msg='User Does not Exist'), 400)
			if not util.is_valid_password(password, user.password):
				return make_response(jsonify(status='Failed', token=None, msg='Invalid Password'), 400)
			auth_token = util.encode_auth_token(user_id)
			return util.get_response_with_cookie({'status': 'Success', 'token': auth_token}, 'auth_token', auth_token)
		except Exception as e:
			return make_response(jsonify(status='Failed', token=None), 500)

if __name__ == '__main__':
	print('Starting App!')
	app.run(host='0.0.0.0', port=8080)
