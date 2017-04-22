import boto3
import json
import threading
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as features
import sys


class Send_Thread(threading.Thread):
	def __init__(self, topic, index, user_name, password):
		threading.Thread.__init__(self)
		self.topic = topic
		self.index = index
		self.user_name = user_name
		self.password = password
	def run(self):
		sqs = boto3.resource('sqs',  region_name = 'us-west-2')
		my_sns = boto3.client('sns',  region_name = 'us-west-2')
		natural_language_understanding = NaturalLanguageUnderstandingV1(
			version='2017-02-27',
			username= user_name,
			password= password)
		while True: 
			message = queue.receive_messages(
				MessageAttributeNames = ['All']	
			)
			if len(message) == 0:
				print "No Message"
			else:
				print "Worker-" + str(self.index) + "------------" + message[0].body
				json_message = json.loads(message[0].body)
				json_message['worker'] = self.index

				max_emo = "neutral"
				try:
					analyze_response = natural_language_understanding.analyze(
						text = json_message['text'],
						features=[features.Emotion()])
					if "emotion" in analyze_response \
					and "document" in analyze_response["emotion"] \
					and "emotion" in analyze_response["emotion"]["document"]: 
						max_val = 0
						emotions = analyze_response["emotion"]["document"]["emotion"]
						for emotion in emotions:
							if emotions[emotion] > max_val:
								max_val = emotions[emotion]
								max_emo = emotion
				except:	
					pass
				print max_emo
				json_message["emotion"] = max_emo
				response = message[0].delete()
				response = my_sns.publish(
					TopicArn = topicArn,
					Message = json.dumps(json_message)
				)
		

if __name__ == "__main__":
	my_sqs = boto3.resource('sqs', region_name = 'us-west-2')
	queue = my_sqs.get_queue_by_name(QueueName='heng-test')
	queue_url = "https://us-west-2.queue.amazonaws.com/765665253410/heng-test"
	topicArn = 'arn:aws:sns:us-west-2:765665253410:http-test-west-2'
	user_name = "72893321-f1bd-4204-a378-1f17a8abbe4f"
	password = "M88M3fBirZ3r"
	for i in range(0, 3):
		send_thread = Send_Thread(topicArn, i, user_name, password)
		send_thread.start()