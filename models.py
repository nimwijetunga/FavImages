from app import db
from sqlalchemy.dialects.postgresql import JSON, ARRAY
import os
import simplejson as json
import uuid
import image_handler

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    title = db.Column(db.String())
    description = db.Column(db.String())

    def __init__(self, url, title, description='', width='', height=''):
        self.url = url
        self.width = width
        self.height = height
        self.title = title
        self.description = description

    def add_image_to_cache(self):
    	key = 'image:%s' % self.id
    	image_info = {
    		'url': self.url,
    		'width': self.width,
    		'height': self.height,
            'title': self.title,
            'description': self.description
    	}
    	image_handler.images_redis.set(key, json.dumps(image_info))
    	image_handler.images_redis.expire(key, 60*60) # expire after an hour

    def __repr__(self):
        return '<id {}>'.format(self.id)

class User(db.Model):
	__tablename__ = 'users'

	user_id = db.Column(db.String(), primary_key=True)
	password = db.Column(db.String(), nullable=False)
	email = db.Column(db.String())
	images = db.Column(db.String(), default=json.dumps([]))

	def __init__(self, user_id, password, email):
		self.user_id = user_id
		self.password = password
		self.email = email