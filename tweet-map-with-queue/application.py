from flask import Flask
from flask import render_template
from flask import request
from flask import Response
from flask.ext.socketio import emit
from flask.ext.socketio import SocketIO
from elasticsearch import Elasticsearch
import threading
import json
# import twitter_stream


elastic = Elasticsearch([{'host':'search-tweet-queue-6bzr27ri5zikrv2haxlsofps6e.us-west-2.es.amazonaws.com', 'port':80}])
# if elastic.indices.exists(index = 'tweet_test') :
    # elastic.indices.delete(index = 'tweet_test')
# mapping = {
# 	'mappings' : {
# 		'tweets' : {
# 			'properties' : {
# 				'create_date' : {
# 					'type' : 'date',
# 					'format' : 'yyyy-MM-dd HH:mm:ss'
# 				},
# 				'coordinates' : {
# 					'type' : 'geo_point'
# 				}
# 			}
# 		}
# 	}
# }
# elastic.indices.create(index = 'tweet_test', ignore = 400, body = mapping)


application = Flask(__name__)
socketio = SocketIO(application)


@application.route('/')
def get_index_page():
	return render_template('index.html')

@application.route('/notification', methods = ['POST'])
def get_notification():
	if request.method == 'POST':
		# print request.values
		# print "---------header-------"
		# print request.headers
		# print request.headers.get("X-Amz-Sns-Message-Type")
		# print "------body---------"
		# print request.data

		json_data = json.loads(request.data)
		if json_data.get("Message", None) != None:
			json_message = json.loads(json_data.get("Message"))
			socketio.emit('response', json_message, namespace = '/test')
			elastic.index(index = 'tweet-queue', doc_type = 'tweets', id = json_message["id"], body = json_message)
			socketio.emit('my_response', {
				'text': json_message["text"], 
				'position': json_message["coordinates"], 
				'emotion': json_message['emotion'], 
				'user': json_message['user']
				}, namespace = '/test')
		# socketio.emit('response', json_data, namespace = '/test')
		response = Response(status = 200)
		return response

@socketio.on('connect', namespace='/test')
def test_connect():
	print 'conntected!'
	# send_thread = Send_Thread()
	# send_thread.start()
@socketio.on('search_emotion', namespace='/test')
def search_emotion(data):
	print data
	result = elastic.search(
		index = 'tweet-queue',
		doc_type = 'tweets',
		body = {
			'query': {
				'match': {
					'emotion': data['data']
				}
			}
		}
	)
	print result
	socketio.emit('search_response', {'data': result['hits']['hits']}, namespace = '/test')
@socketio.on('range_search', namespace='/test')
def search_range(data):
	print data
	result = elastic.search(
		index = 'tweet-queue',
		doc_type='tweets',
		body={
			'query': {
				'bool': {
					'filter': {
						'geo_distance': {
							'distance' : str(data["distance"]) + "km",
							'coordinates': {
								"lat": data["lat"],
								"lon": data["lon"]
							}
						}
					}
				}
			}
		})
	socketio.emit('range_search_response', {'data': result['hits']['hits']}, namespace = '/test')

@socketio.on('search', namespace='/test')
def search_keyword(data):
	print data
	result = elastic.search(
	index = 'tweet-queue',
	doc_type='tweets',
	body={
		'query': {
			'match' : {
				'text' : data['data']
			}
		}
    })
	socketio.emit('search_response', {'data': result['hits']['hits']}, namespace = '/test')

@socketio.on('my event', namespace='/test')
def test_message(message):
	print message

if __name__ == "__main__":
	socketio.run(application)