from kafka import KafkaProducer
import json
import time
from csv import reader

class MessageProducer:
    broker = ""
    topic = ""
    producer = None

    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.broker,
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                      acks=0,
                                      api_version=(2,5,0),
                                      retries=3
                                      )

    def send_message(self, msg):
        try:
            future = self.producer.send(self.topic, msg)
            self.producer.flush()   # 비우는 작업
            future.get(timeout=60)
            return {'status_code': 200, 'error': None}
        except Exception as e:
            print("error:::::",e)
            return e

# 브로커와 토픽명을 지정한다.
broker = 'localhost:9092'
topic = 'new-topic'
message_producer = MessageProducer(broker, topic)