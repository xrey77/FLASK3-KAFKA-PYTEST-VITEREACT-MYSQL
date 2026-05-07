import json
import threading
from confluent_kafka import Producer, Consumer, KafkaError # type: ignore
from confluent_kafka.admin import AdminClient, NewTopic # type: ignore

class KafkaConsumerService:
    print("consumer service started....")
    def __init__(self, app):
        self.app = app
        self.shutdown_event = threading.Event()
        self.conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'flask-group-v6',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }

    def init_topic(self):
        admin_client = AdminClient({'bootstrap.servers': self.conf['bootstrap.servers']})
        topic = [NewTopic("central-topic", num_partitions=3, replication_factor=1)]
        try:
            admin_client.create_topics(topic)
        except Exception as e:
            self.app.logger.info(f"Topic exists or creation failed: {e}")

    def process_message(self, message_str):
        with self.app.app_context(): # Essential for DB operations
            try:
                data = json.loads(message_str)
                print(f"Processing user: {data.get('user_id')}")
#             # with app.app_context():
#             #     db.session.add(User(...))
#             #     db.session.commit()
                print(f"Successfully processed {data.get('user_id')}")
            except json.JSONDecodeError:
                print("Failed to decode JSON")                
            # except Exception as e:
            #     print(f"Error: {e}")

    # def start(self):
    def start(self, *args, **kwargs):        
        self.init_topic()
        consumer = Consumer(self.conf)
        consumer.subscribe(['central-topic'])

        try:
            while not self.shutdown_event.is_set():
                msg = consumer.poll(1.0)
                if msg is None: continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                self.process_message(msg.value().decode('utf-8'))
                consumer.commit(asynchronous=True) # Add this to mark the message as processed                
                # 2. MANUALLY COMMIT (The "Confirmation")
                try:
                    consumer.commit(asynchronous=False)
                    print("Offset committed successfully.")
                except Exception as e:
                    print(f"Failed to commit offset: {e}")
        finally:
            consumer.close()

    def stop(self):
        self.shutdown_event.set()





class KafkaProducerService:
    def __init__(self, servers='localhost:9092'):
        self.producer = Producer({'bootstrap.servers': servers})    
    # def __init__(self, app=None):
    #     self.producer = None
    #     if app is not None:
    #         self.init_app(app)

    def init_app(self, app):
        conf = {
            'bootstrap.servers': app.config.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'client.id': app.config.get('KAFKA_CLIENT_ID', 'flask-producer'),
            'enable.idempotence': True,  # Ensures exactly-once delivery
            'acks': 'all',               # Highest durability
            'queue.buffering.max.messages': 1000000
        }
        self.producer = Producer(conf)
        
        # Register for cleanup on app shutdown
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.flush()

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['kafka_producer'] = self

    def send_message(self, topic, data):
        self.producer.produce(
            topic, 
            json.dumps(data).encode('utf-8'),
            callback=self._delivery_report
        )
        self.producer.flush() # Ensures the message is sent

    def _delivery_report(self, err, msg):
        if err is not None:
            # In production, use app.logger instead of print
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce(self, topic, value, key=None):
        if self.producer is None:
            raise RuntimeError("KafkaProducerService not initialized.")
            
        # Ensure value is serialized to bytes
        payload = json.dumps(value).encode('utf-8')
        
        self.producer.produce(
            topic, 
            key=key, 
            value=payload, 
            callback=self._delivery_report
        )
        # Serve delivery callbacks
        self.producer.poll(0)

    def flush(self, timeout=10):
        if self.producer:
            # Force send any buffered messages before exit
            self.producer.flush(timeout)



# class KafkaProducerService:
#     def __init__(self, app=None):
#         # self.producer = Producer({'bootstrap.servers': 'localhost:9092'})
#         # app.extensions['kafka_producer'] = self.producer        
#         self.producer = None
#         if app is not None:
#             self.init_app(app)

#     def init_app(self, app):
#         conf = {
#             'bootstrap.servers': app.config.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
#             'client.id': app.config.get('KAFKA_CLIENT_ID', 'flask-producer'),
#             'group.id': 'flask-group-v6', # Updated group ID
#             'auto.offset.reset': 'earliest',
#             'enable.auto.commit': False,
#             'queue.buffering.max.messages': 1000000,
#             'acks': 'all'
#         }
#         self.producer = Producer(conf)
        
#         if not hasattr(app, 'extensions'):
#             app.extensions = {}
#         app.extensions['kafka_producer'] = self

#     def _delivery_report(self, err, msg):
#         if err is not None:
#             print(f"Message delivery failed: {err}")
#         else:
#             print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

#     def produce(self, topic, value, key=None):
#         if self.producer is None:
#             raise RuntimeError("KafkaProducerService not initialized.")
            
#         self.producer.produce(
#             topic, 
#             key=key, 
#             value=json.dumps(value).encode('utf-8'), 
#             callback=self._delivery_report
#         )
#         self.producer.poll(0)

#     def flush(self, timeout=10):
#         if self.producer:
#             self.producer.flush(timeout)
