from kafka import KafkaProducer
import json

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


# Send messages to the Kafka topic
def send_message(message):
    producer.send("insert", value=message)
    producer.flush()


# Read messages from the file
with open("queries.txt", "r") as file:
    messages = file.readlines()

# Send each message to Kafka
for message in messages:
    try:
        json_message = json.loads(message)
        print(json_message)
        send_message(json_message)
    except:
        print("Invalid JSON format. Please enter a valid JSON message.")
        continue


# Close the Kafka producer
producer.close()
