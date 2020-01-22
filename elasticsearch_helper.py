from elasticsearch import Elasticsearch
import os

es_object = None
es_object = Elasticsearch([{'host': os.getenv('ES_HOST'), 'port': os.getenv('ES_PORT')}])

if not es_object.ping():
    raise Exception('Could not connect to ES cluster!')

def create_index(index_name='images'):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "title": {
                        "type": "text"
                    },
                    "description": {
                        "type": "text"
                    },
                    "id": {
                        "type": "integer"
                    },
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        else:
        	print('Index Already Exists!')
    except Exception as ex:
        print(str(ex))

def store_record(index_name, record):
	create_index()
    try:
        outcome = es_object.index(index=index_name, doc_type='members', body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
