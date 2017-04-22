import boto3
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime, timedelta

#Variables that contains the user credentials to access Twitter API 
access_token = "713092162448138240-6ZHbh4KEboncNiKnJstzd0xVnrQgEYT"
access_token_secret = "2V712V0DxIEb9xHQTQJcSq3hwV1F0oIUBxQprsoJDJpOw"
consumer_key = "hpmTucEUFPTHGgClLJzpDiMCC"
consumer_secret = "hDpTYHAtzo4fEoXdTlYudE0O476XilCJRywcXdHFtf3sdI5cG6"


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self, sqs_client, queue_url):
		self.client = sqs_client
		self.queue_url = queue_url
	def on_data(self, data):
		jsonData = json.loads(data)
		current = datetime.now()
		if (jsonData.get("user") is not None and jsonData["user"]["lang"] == "en" and jsonData.get("coordinates") is not None):

			if (jsonData.get("text") is not None):
				my_data = {
					'id' : jsonData['id'],
					'text' : jsonData["text"],
					'user' : jsonData["user"]["name"],
					'create_date' : self.current_time(current),
					'coordinates' : jsonData["coordinates"]["coordinates"]
				}

				print "Text: " + jsonData["text"] + "\n"
				response = my_sqs.send_message(
					QueueUrl=queue_url,
					DelaySeconds=10,
					MessageBody=(
						json.dumps(my_data)
					)
				)
		return True

	def on_error(self, status):
		print status
	def current_time(self, current):
		return current.strftime("%Y-%m-%d %H:%M:%S")

class My_Stream(object):

    def __init__(self, sqs_client, queue_url):
		self.l = StdOutListener(sqs_client, queue_url)
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

if __name__ == "__main__":
	my_sqs = boto3.client('sqs', region_name='us-west-2')
	queue_url = "https://us-west-2.queue.amazonaws.com/765665253410/heng-test"

	my_stream = My_Stream(my_sqs, queue_url)
	my_stream.run()

