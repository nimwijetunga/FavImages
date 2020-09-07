from flask import Flask, request, jsonify, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
import simplejson as json
import os
import util
import image_handler
import elasticsearch_helper as eh
# import avro_producer as ap
from util import authenticate_request
from flask_restplus import Api, Resource, fields


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DOCS_ROUTES = Blueprint('swagger', __name__)

class CustomAPI(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

# api = Api(app=app)
api = CustomAPI(app=app, title='FavImages',
                version='1.0')

login_auth = api.namespace('login', description='Authentication API\'s')
images = api.namespace('images', description='Image Saving/Retrieval API\'s')

import models

@property
def specs_url(self):
	'''
	The Swagger specifications absolute url (ie. `swagger.json`)

	:rtype: str
	'''
	url = url_for(self.endpoint('specs'), _external=True)
	if self.app.config.get('SWAGGER_BASEPATH', ''):
	    prefix = url.split('/swagger.json')[0]
	    url = prefix + self.app.config.get('SWAGGER_BASEPATH', '') + '/swagger.json'
	return url

@images.route("/images/search")
class ImagesSearchTitle(Resource):
	@api.doc(params={'title': 'Title to be Searched', 'description': 'Description to be Searched'})
	@authenticate_request
	def get(user_id, self):
		title = request.args.get('title')
		description = request.args.get('description')
		if not title and not description:
			return make_response(jsonify(error='Please provide a title or description'), 400)
		if title and description:
			return make_response(jsonify(error='Please only provide a title OR description'), 400)
		suggestions = []
		if title:
			suggestions = eh.query_title('images', title)
		else:
			suggestions = eh.query_description('images', description) if description else []
		return make_response(jsonify(suggestions=suggestions))

@images.route("/images/details")
class ImagesSearchTitle(Resource):
	@api.doc(params={'image_id': 'Image ID'})
	@authenticate_request
	def get(user_id, self):
		image_id = int(request.args.get('image_id'))
		if not image_id:
			return make_response(jsonify(error='Please provide an image id'), 400)
		image_details = image_handler.get_image_details(image_id)
		return make_response(jsonify(image_details=image_details))

@images.route("/images/favourite")
class ImagesSave(Resource):

	expected = api.schema_model('image_id', {
	    'properties': {
	        'image_id': {
	            'type': 'integer'
	        },
	    },
	    'type': 'object'
	})

	@images.expect(expected)
	@authenticate_request
	def post(user_id, self):
		body = request.get_json() or {}
		image_id = body.get('image_id')
		if not image_id:
			return make_response(jsonify(error='Please provide image ids to save'), 400) 			
		image_handler.add_favourite_images(user_id, [image_id])
		return make_response(jsonify(message='Success'))

	@authenticate_request
	def get(user_id, self):
		return make_response(jsonify(images=image_handler.get_favourite_images(user_id)))

@images.route("/images")
class Images(Resource):
	image_objects = api.schema_model('image_objs', {
	    'properties': {
	        'title': {
	            'type': 'string'
	        },
	        'url': {
	            'type': 'string'
	        },
	        'width': {
	            'type': 'int'
	        },
	        'height': {
	            'type': 'int'
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
		image_key = {
			'id': image_ids[0]
		}
		image_value = {
			'id': image_ids[0],
			'url': image_obj.get('url') or '',
			'title': image_obj.get('title'),
			'description': image_obj.get('description') or '',
			'width': float(image_obj.get('width')) if image_obj.get('width') else 0.0,
			'height': float(image_obj.get('height')) if image_obj.get('height') else 0.0
		}
		# ap.images_produce_to_kafka(image_key, image_value)
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
		# try:
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
		user_key_dict = {
			'user_id': user_id
		}
		user_value_dict = {
			'user_id': user_id,
			'password': password,
			'email': email or '',
			'images': json.dumps([])
		}
		# ap.users_produce_to_kafka(user_key_dict, user_value_dict)
		return util.get_response_with_cookie({'status': 'Success', 'token': auth_token}, 'auth_token', auth_token)
		# except Exception as e:
		# 	db.session.rollback()
		# 	return make_response(jsonify(status='Failed', token=None), 500)

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
			return make_response(jsonify(status='Failed', token=None, error=str(e)), 500)

if __name__ == '__main__':
	print('Starting App!')
	app.run(host='0.0.0.0', port=os.getenv('APP_PORT'))
