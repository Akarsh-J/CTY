from kafka import KafkaConsumer
import threading
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from kafka.structs import TopicPartition


# Create a Kafka consumer instance
consumer = KafkaConsumer(
    bootstrap_servers="localhost:9092",
    group_id="group-id",
    enable_auto_commit=False,  # Disable auto commit
    max_poll_records=20,  # Set the maximum number of records to fetch in each poll
)

partition = TopicPartition("insert", 0)
consumer.assign([partition])

num_threads = 4
barrier = threading.Barrier(num_threads + 1)  # +1 for main thread

# thread pool to limit the number of threads being sprout
pool = ThreadPoolExecutor(max_workers=num_threads)

# Store execution status of each offset
# 0 - Queued for execution
# 1 - Succesful
# -1 - Exception
offsets = {}


def process_thread_records(records):
    # wait for all threads to reach the barrier
    barrier.wait()
    for record in records:
        try:
            print(threading.current_thread().name, record.offset)
            # print(record.offset)
            offsets[record.offset] = 1
        except Exception as e:
            print("An error occured: ", str(e))
            offsets[record.offset] = -1


def commit_offsets():
    sorted_keys = sorted(offsets.keys())
    offset_to_commit = -1

    for key in sorted_keys:
        value = offsets[key]
        if value == 1:
            offset_to_commit = key
        elif value == -1:
            break

    consumer.seek(partition, offset_to_commit)
    print("commiting offset: ", offset_to_commit)
    consumer.commit()


# Continuously poll for thread_records in batches
while True:
    # Poll for new thread_records
    batch = consumer.poll(timeout_ms=500)  # Adjust the timeout as needed
    print("New Batch is here\n")
    print("\n\n")

    # threadpool
    futures = []
    if len(batch) == 0:
        continue

    for topic_partition, records in batch.items():
        offsets.clear()

        for record in records:
            offsets[record.offset] = 0

        num_records = len(records)
        min_records_per_thread = num_records // num_threads

        for i in range(num_threads):
            thread_records = []
            index = i

            # to populate thread_records with the appropriate records
            # if records available are 0-19, thread 1 gets 0,4,8,12,16.
            for j in range(min_records_per_thread + 1):
                if index < num_records:
                    thread_records.append(records[index])
                    index += num_threads

            # Submit the thread task to the thread pool
            future = pool.submit(process_thread_records, thread_records)

            futures.append(future)

    print(offsets)
    barrier.wait()

    # wait for all threads to complete its execution
    for future in futures:
        future.result()
    print("\n after join")
    print(offsets)

    commit_offsets()
    a = input()
    # print(batch)

    # Manually commit the offsets once the batch is processed
    # consumer.commit()

# Close the consumer connection
consumer.close()
