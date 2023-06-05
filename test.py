from kafka import KafkaConsumer
import threading
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from kafka.structs import TopicPartition
import psycopg2
import json


# Create a Kafka consumer instance
consumer = KafkaConsumer(
    bootstrap_servers="localhost:9092",
    group_id="group-id",
    enable_auto_commit=False,  # Disable auto commit
    max_poll_records=20,  # Set the maximum number of records to fetch in each poll
    auto_offset_reset="latest",
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
executed_records_post_error = []


def process_thread_records(records):
    
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="cty",
        user="akarshj21",
        password="AkArshj21",
    )

    cursor = connection.cursor()
    
    # wait for all threads to reach the barrier
    barrier.wait()
    for record in records:
        #Check if the record was executed by the prvious batch
        if record.offset not in executed_records_post_error:
            try:
                msg = record.value.decode("utf-8")
                # msg = msg.strip().split(",")
                msg = json.loads(msg)

                # print(type(msg), msg)

                db = msg["db"]
                operation = msg["operation"]

                if msg["db"] == "Client":
                    (
                        user_id,
                        username,
                        password,
                        first_name,
                        last_name,
                        phone,
                        address_1,
                        address_2,
                    ) = msg["data"].values()

                    query = f"INSERT INTO Client VALUES ('{user_id}', '{username}', '{password}', '{first_name}', '{last_name}', '{phone}', '{address_1}', '{address_2}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "Cart":
                    cart_id, user_id, total_qty, total_cost, created_at, modified_at = msg[
                        "data"
                    ].values()

                    query = f"INSERT INTO Cart VALUES ({cart_id}, '{user_id}', {total_qty}, {total_cost}, '{created_at}', '{modified_at}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "Order_Details":
                    order_id = msg["data"]["order_id"]
                    user_id = msg["data"]["user_id"]
                    total_cost = msg["data"]["total_cost"]
                    items = json.dumps(msg["data"]["items"])
                    payment_id = msg["data"]["Payment_id"]
                    cart_id = msg["data"]["cart_id"]
                    created_at = msg["data"]["Created_at"]
                    modified_at = msg["data"]["Modified_at"]

                    query = f"INSERT INTO Order_Details VALUES ({order_id}, '{user_id}', {total_cost}, '{items}', '{payment_id}', {cart_id}, '{created_at}', '{modified_at}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "Payment_Details":
                    (
                        order_id,
                        transaction_id,
                        amount,
                        provider,
                        status,
                        created_at,
                        payment_id,
                    ) = msg["data"].values()

                    query = f"INSERT INTO Payment_Details VALUES ({order_id}, {transaction_id}, {amount}, '{provider}', '{status}', '{created_at}', '{payment_id}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "user_payment":
                    payment_id, user_id, payment_type, provider, account_no, expiry = msg[
                        "data"
                    ].values()

                    query = f"INSERT INTO user_payment VALUES ('{payment_id}', '{user_id}', '{payment_type}', '{provider}', '{account_no}', '{expiry}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "Product":
                    product_id = msg["data"]["Product_id"]
                    product_name = msg["data"]["Product_name"]
                    description = msg["data"]["description"]
                    category = json.dumps(msg["data"]["Category"])
                    price = msg["data"]["Price"]
                    created_at = msg["data"]["Created_at"]
                    modified_at = msg["data"]["modified_at"]

                    query = f"INSERT INTO Product VALUES ('{product_id}', '{product_name}', '{description}', '{category}', {price}, '{created_at}', '{modified_at}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "Vendor":
                    vendor_id, vendor_name, password, phone, addr, created_at = msg[
                        "data"
                    ].values()

                    query = f"INSERT INTO Vendor VALUES ('{vendor_id}', '{vendor_name}', '{password}', '{phone}', '{addr}', '{created_at}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "product_Vendor":
                    (
                        product_id,
                        vendor_id,
                        item_id,
                        item_name,
                        quantity,
                        discount_price,
                        created_at,
                        modified_at,
                    ) = msg["data"].values()

                    query = f"INSERT INTO product_Vendor VALUES ('{product_id}', '{vendor_id}', '{item_id}', '{item_name}', {quantity}, {discount_price}, '{created_at}', '{modified_at}')"
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")

                if msg["db"] == "Cart_items":
                    cart_id, item_id, quantity = msg["data"].values()

                    query = (
                        f"INSERT INTO Cart_items VALUES ({cart_id}, '{item_id}', {quantity})"
                    )
                    cursor.execute(query)
                    connection.commit()

                    print(f"Message '{query}' inserted into the database")
                
                print(threading.current_thread().name, record.offset)
                # print(record.offset)
                offsets[record.offset] = 1
                
            except Exception as e:
                #print("An error occured: ", str(e))
                print(f"Error processing message '{record.value.decode('utf-8')}': {str(e)}")
                offsets[record.offset] = -1
        
        else:
            print(f"{record.offset} already executed in the previous batch")
    


def commit_offsets():
    sorted_keys = sorted(offsets.keys())
    offset_to_commit = -1
    error_occurred = False

    for key in sorted_keys:
        value = offsets[key]
        if value == 1 and error_occurred == False:
            print(1)
            offset_to_commit = key
        #After an exception has occured if any record has been executed, Then keep track of those records in the list
        elif value == 1 and error_occurred == True:
            print(2)
            executed_records_post_error.append(key)
        elif value == -1:
            print(3)
            error_occurred = True

    if offset_to_commit != -1:
        # move the consumer pointer to the offset that is to be committed
        consumer.seek(partition, offset_to_commit)
        print("commiting offset: ", offset_to_commit)
        consumer.commit()
        # After commiting, seek to make consumer to read from the next
        consumer.seek(partition, offset_to_commit + 1)
    
    else:
        print("Re-executing the same batch since the first record failed")
        consumer.seek(partition,sorted_keys[0])


# Continuously poll for thread_records in batches
while True:
    # Poll for new thread_records
    print("Last offset: ", consumer.position(partition))
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
