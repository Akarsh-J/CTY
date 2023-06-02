from kafka import KafkaConsumer

# Create a Kafka consumer instance
consumer = KafkaConsumer(
    "insert",
    bootstrap_servers="localhost:9092",
    group_id="group-id",
    enable_auto_commit=False,  # Disable auto commit
    max_poll_records=20,  # Set the maximum number of records to fetch in each poll
)

# Continuously poll for messages in batches
while True:
    # Poll for new messages
    batch = consumer.poll(timeout_ms=500)  # Adjust the timeout as needed

    # distribute the messages from the batch to 4 threads and execute them concurrently
    # Perform error handling and commiting of offset accordingly
    # -----------------------
    # -----------------------
    # -----------------------
    for topic_partition, records in batch.items():
        for record in records:
            print(record.value.decode("utf-8"))
        print("Next batch\n\n")
    # print(batch)

    # Manually commit the offsets once the batch is processed
    # consumer.commit()

# Close the consumer connection
consumer.close()
