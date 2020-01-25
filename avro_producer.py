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
     {"name": "images", "type" : {"type": "array", "items" : "int"}}
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

def users_produce_to_kafka(key, value):
  value_schema = avro.loads(json.dumps(user_value_schema))
  key_schema = avro.loads(json.dumps(user_key_schema))
  avroProducer = AvroProducer({
    'bootstrap.servers': '%s:%s' % (os.getenv('KAFKA_HOST'), os.getenv('KAFKA_PORT')),
    'schema.registry.url': 'http://%s:%s' % (os.getenv('SCHEMA_HOST'), os.getenv('SCHEMA_PORT'))
    }, default_key_schema=key_schema, default_value_schema=value_schema)
  avroProducer.produce(topic='users_vx', value=value, key=key)
  avroProducer.flush()


# key = {"user_id": "nim"}
# value = {"user_id": "nim", "password": "123", "email":"abc.com", "images": [1,2,3]}
# users_produce_to_kafka(key, value)
