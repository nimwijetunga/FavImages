import models
import simplejson as json
from app import db
from elasticsearch_helper import store_record
import redis
import os

_IMAGES_REDIS_DB_NUM = 0
images_redis = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=_IMAGES_REDIS_DB_NUM)

def create_images_add_to_cache_db_es(image_objs):
	image_ids = []
	for image_obj in image_objs:
		try:
			image = models.Image(**image_obj)
			db.session.add(image)
			db.session.commit()
			image.add_image_to_cache()
			store_record('images', {
					'title': image.title,
					'description': image.description,
					'id': image.id
				})
			image_ids.append(image.id)
		except Exception as e:
			db.session.rollback()
	return image_ids

# def get_existing_images(score):
# 	score_key = 'score:%s' % score
# 	return images_redis.lrange(score_key, 0, -1)

# def fetch_images_from_redis_add_to_db(user, image_uuids):
# 	try:
# 		saved_image_ids = set(user.images or [])
# 		for uuid in image_uuids:
# 			key = 'image:%s' % uuid
# 			image_data = images_redis.get(key)
# 			if not image_data:
# 				raise Exception('Could Not Find Image in Cache')
# 			image_data = json.loads(image_data)
# 			image = models.Image(**image_data)
# 			saved_image = db.session.query(models.Image).filter_by(url=image.url,
# 																   width=image.width,
# 																   height=image.height,
# 																   score=image.score).first()
# 			if saved_image:
# 				saved_image_ids.add(saved_image.id)
# 				continue
# 			db.session.add(image)
# 			db.session.flush()
# 			saved_image_ids.add(image.id)
# 		saved_image_ids = list(saved_image_ids)
# 		user.images = saved_image_ids
# 		db.session.add(user)
# 		db.session.commit()
# 	except Exception as e:
# 		db.session.rollback()
# 		raise Exception(str(e))







