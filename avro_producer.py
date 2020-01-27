from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import time
import simplejson as json
import os


user_value_schema = {
   "namespace": "users.kafka",
   "name": "value",
   "type": "record",
   "fields" : [
     {"name" : "user_id", "type" : "string"},
     {"name" : "password", "type" : "string"},
     {"name" : "email", "type" : "string"},
     {"name":  "images", "type" : "string"}
   ]
}


user_key_schema = {
   "namespace": "users.kafka",
   "name": "key",
   "type": "record",
   "fields" : [
     {"name" : "user_id", "type" : "string"}
   ]
}

images_value_schema = {
   "namespace": "images.kafka",
   "name": "value",
   "type": "record",
   "fields" : [
     {"name" : "id", "type" : "int"},
     {"name" : "url", "type" : "string"},
     {"name" : "title", "type" : "string"},
     {"name" : "description", "type" : "string"},
     {"name": "width", "type" : "float"},
     {"name": "height", "type" : "float"}
   ]
}


images_key_schema = {
   "namespace": "images.kafka",
   "name": "key",
   "type": "record",
   "fields" : [
     {"name" : "id", "type" : "int"}
   ]
}



def users_produce_to_kafka(key, value):
  value_schema = avro.loads(json.dumps(user_value_schema))
  key_schema = avro.loads(json.dumps(user_key_schema))
  avroProducer = AvroProducer({
    'bootstrap.servers': '%s:%s' % (os.getenv('KAFKA_HOST'), os.getenv('KAFKA_PORT')),
    'schema.registry.url': 'http://%s:%s' % (os.getenv('SCHEMA_HOST'), os.getenv('SCHEMA_PORT'))
    }, default_key_schema=key_schema, default_value_schema=value_schema)
  avroProducer.produce(topic='users_topic', value=value, key=key)
  avroProducer.flush()

def images_produce_to_kafka(key, value):
  value_schema = avro.loads(json.dumps(images_value_schema))
  key_schema = avro.loads(json.dumps(images_key_schema))
  avroProducer = AvroProducer({
    'bootstrap.servers': '%s:%s' % (os.getenv('KAFKA_HOST'), os.getenv('KAFKA_PORT')),
    'schema.registry.url': 'http://%s:%s' % (os.getenv('SCHEMA_HOST'), os.getenv('SCHEMA_PORT'))
    }, default_key_schema=key_schema, default_value_schema=value_schema)
  avroProducer.produce(topic='images_topic', value=value, key=key)
  avroProducer.flush()
