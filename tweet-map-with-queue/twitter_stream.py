#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

from datetime import datetime, timedelta


#Variables that contains the user credentials to access Twitter API 
access_token = "713092162448138240-6ZHbh4KEboncNiKnJstzd0xVnrQgEYT"
access_token_secret = "2V712V0DxIEb9xHQTQJcSq3hwV1F0oIUBxQprsoJDJpOw"
consumer_key = "hpmTucEUFPTHGgClLJzpDiMCC"
consumer_secret = "hDpTYHAtzo4fEoXdTlYudE0O476XilCJRywcXdHFtf3sdI5cG6"


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self, elastic, socketio):
		self.elastic = elastic
		self.socketio = socketio
	def on_data(self, data):
		jsonData = json.loads(data)
		current = datetime.now()
		if (jsonData.get("user") is not None and jsonData["user"]["lang"] == "en" and jsonData.get("coordinates") is not None):

			if (jsonData.get("text") is not None):
				my_data = {
					'text' : jsonData["text"],
					'user' : jsonData["user"]["name"],
					'create_date' : self.current_time(current),
					'coordinates' : jsonData["coordinates"]["coordinates"]
				}
				self.elastic.index(index = 'tweet_test', doc_type = 'tweets', id = jsonData["id"], body = my_data)
				self.socketio.emit('my_response', {'data': jsonData["text"], 'position': jsonData["coordinates"]}, namespace = '/test')
				print "Text: " + jsonData["text"] + "\n"
			#only record the tweets within two days from now
			elastic.delete_by_query(
				index = 'tweet_test',
				doc_type = 'tweets',
				body = {
					'query': {
						'range': {
							'create_date' : {
								'lte' : current_time(current - timedelta(2))
							}
						}
					}
				})
		return True

	def on_error(self, status):
		print status
	def current_time(self, current):
		return current.strftime("%Y-%m-%d %H:%M:%S")

class My_Stream(object):

    def __init__(self, elastic, socketio):
		self.l = StdOutListener(elastic, socketio)
		self.auth = OAuthHandler(consumer_key, consumer_secret)
		self.auth.set_access_token(access_token, access_token_secret)

    def run(self):

		all_characters = []
		for i in range(128):
			all_characters.append(chr(i))
		while True:
			try:
				self.stream = Stream(self.auth, self.l)
				self.stream.filter(track = all_characters)
			except KeyboardInterrupt:
				self.stream.disconnect()
				print 1
				break
			except:
				print 2
				continue