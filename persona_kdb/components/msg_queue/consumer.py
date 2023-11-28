from kafka import KafkaConsumer
import time
import json
import sys
import datetime
from models import KafkaMessage

class MessageConsumer:
    broker = ""
    topic = ""
    group_id = ""
    logger = None

    def __init__(self, broker, topic, group_id):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id

    def activate_listener(self):
    	# 처리 시간 등의 결과 확인을 위해 kafka_output.txt 파일에 값을 이어 출력한다.
    	sys.stdout = open('kafka_output.txt','a', encoding='utf-8')
        consumer = KafkaConsumer(
            bootstrap_servers=self.broker,
            group_id=self.group_id,
            consumer_timeout_ms=2000,
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('ascii'))
        )
        consumer.subscribe(self.topic)
        tot_start = time.time()
        start = time.time()
        i = 0

        try:
            with open(self.topic+'.txt', 'a', encoding='utf-8') as file:
                for message in consumer:
                    message = message.value
                    file.write(str(message))
                    i = i + 1
                    
                    data = {
                        'name': topic,
                        'col_a': i,
                        'col_b': message,
                        'create_date': datetime.datetime.now()
                    }
                    KafkaMessage.objects.create(**data)
                    
                    consumer.commit()
                    
                tot_end = time.time()
                tot_elapsed = tot_end - tot_start
                per_time_value = i / tot_elapsed
                
                print("=====================================================")
                print("총 처리 시간: ", tot_elapsed)
                print("총 처리 건수: ", i)
                print("초당 처리 건수: ", per_time_value)
        except KeyboardInterrupt:
            print("Aborted by user...")
            

broker = 'localhost:9092'
topic = 'new-topic'
group_id = 'consumer-1'

consumer1 = MessageConsumer(broker, topic, group_id)
consumer1.activate_listener()

consumer2 = MessageConsumer(broker, topic, group_id)
consumer2.activate_listener()
