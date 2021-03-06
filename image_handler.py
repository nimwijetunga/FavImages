import models
import simplejson as json
from app import db
import elasticsearch_helper as eh
import redis
import util
# import avro_producer as ap
import os

_IMAGES_REDIS_DB_NUM = 0
images_redis = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=_IMAGES_REDIS_DB_NUM)

def create_images_add_to_cache_db_es(image_objs):
	image_ids = []
	for image_obj in image_objs:
		try:
			image = models.Image(**image_obj)
			s3_url = util.upload_to_s3(image.title, image.url)
			image.s3_url = s3_url
			db.session.add(image)
			db.session.commit()
			image.add_image_to_cache()
			eh.store_record('images', {
					'title': image.title,
					'title_suggest': image.title,
					'description': image.description,
					'description_suggest': image.description,
					'id': image.id
				})
			image_ids.append(image.id)
		except Exception as e:
			db.session.rollback()
	return image_ids

def get_image_details(image_id):
	cache_key = 'image:%s' % image_id
	cache_hit = images_redis.get(cache_key)
	if cache_hit:
		print('HIT!')
		obj = json.loads(cache_hit)
		obj['id'] = image_id
		return obj
	# fallback to db search
	image = models.Image.query.get(image_id)
	if not image:
		raise Exception('Cannot Find Image with id: %s' % image_id)
	# add image to cache
	image_obj = {
		'title': image.title,
		'description': image.description,
		'url': image.url,
		'width': image.width,
		'height': image.height
	}
	images_redis.set(cache_key, json.dumps(image_obj))
	return image_obj

def get_favourite_images(user_id):
	user = models.User.query.get(user_id)
	if not user:
		raise Exception('Could not find user with id: %s' % user_id)
	images = user.images or json.dumps([])
	return list(json.loads(images))

def add_favourite_images(user_id, image_ids):
	user = models.User.query.get(user_id)
	if not user:
		raise Exception('Could not find user with id: %s' % user_id)
	image_ids = db.session.query(models.Image.id).filter(models.Image.id.in_(image_ids)).all()
	try:
		images = set(json.loads(user.images))
	except Exception as e:
		images = set([])
	for image_id in image_ids:
		if image_id not in images:
			images.add(image_id[0])
	try:
		user.images = json.dumps(list(images))	
		db.session.add(user)
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		raise Exception('Could not save images for user: %s' % user_id)
	key_dict = {
		'user_id': user_id
    }
	value_dict = {
		'user_id': user_id,
		'password': user.password,
		'images': user.images,
		'email': user.email or ''
	}
	# ap.users_produce_to_kafka(key_dict, value_dict)
