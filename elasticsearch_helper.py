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
            "number_of_replicas": 0,
            "analysis": {
				"analyzer": {
            		"lower_keyword": {
		                "type": "custom",
		                "tokenizer": "keyword",
		                "filter": "lowercase",
           			 }
				}
			}
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "title": {
                        "type": "text"
                    },
                    "title_suggest": {
                    	"type": "completion",
		                "analyzer": "lower_keyword"
                    },
                    "description": {
                        "type": "text"
                    },
                    "description_suggest": {
                    	"type": "completion",
		                "analyzer": "lower_keyword"
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

def es_search(index_name, suggest_dictionary):
	query_dictionary = {'suggest' : suggest_dictionary}
	suggestions = es_object.search(
	    index=index_name,
	    doc_type='members',
	    body=query_dictionary
	)
	options = suggestions.get('suggest', {}).get('entity-suggest', [{}])[0].get('options', [])
	final_suggestions = [{'name': option.get('text'),
						  'id': option.get('_source', {}).get('id')} for option in options]
	return final_suggestions

def query_title(index_name, title):
	suggest_dictionary  = {'entity-suggest':
         {
             'text':title,
             'completion':{
                 'field':'title_suggest',
             }
         }
    }
	return es_search(index_name, suggest_dictionary)

def query_description(index_name, description):
	suggest_dictionary  = {'entity-suggest':
         {
             'text':description,
             'completion':{
                 'field':'description_suggest',
             }
         }
    }
	return es_search(index_name, suggest_dictionary)
