from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'hackathon-topic',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening...")

for message in consumer:
    print("Received:", message.value)