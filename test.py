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

NUM_THREADS = 4
barrier = threading.Barrier(NUM_THREADS + 1)  # +1 for main thread

# thread pool to limit the number of threads being sprout
pool = ThreadPoolExecutor(max_workers=NUM_THREADS)

# Store execution status of each offset
# 0 - Queued for execution
# 1 - Succesful
# -1 - Exception
OFFSETS = {}

#format: {"error":{"offset":{"count":0,"err":str(e)}}, "success":[offset_number]}
executed_records_post_error = {"error":{},"success":[]}
THRESHOLD_FOR_DLQ = 2   #Threshold to enter a record into Dead letter queue


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
        if record.offset not in executed_records_post_error["success"]:
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
                OFFSETS[record.offset] = 1
                executed_records_post_error["error"].pop(record.offset)
                
            except Exception as e:
                #print("An error occured: ", str(e))
                print(f"Error processing message '{record.value.decode('utf-8')}': {str(e)}")
                connection.rollback()   #to avoid the error:  current transaction is aborted, commands ignored until end of transaction block
                if record.offset in executed_records_post_error["error"].keys():
                    if executed_records_post_error["error"][record.offset]["count"] > THRESHOLD_FOR_DLQ:
                        with open("DLQ.txt", "a") as DLQ:
                            DLQ.write(str({record.offset: str(e)})+"\n")
                        print(f"ENTERING THE RECORD {record.offset} TO DLQ as it exceeds threshold")
                        OFFSETS[record.offset] = 1  #Assume the record has succesfully executed
                        executed_records_post_error["error"].pop(record.offset)
                        
                        DLQ.close()
                    else:
                        executed_records_post_error["error"][record.offset]["count"] += 1
                        OFFSETS[record.offset] = -1
                        
                else:
                    executed_records_post_error["error"][record.offset] = {"count":1,"err":str(e)}
                    OFFSETS[record.offset] = -1
        
        else:
            print(f"{record.offset} already executed in the previous batch")
            OFFSETS[record.offset] = 1


def commit_offsets():
    sorted_keys = sorted(OFFSETS.keys())
    offset_to_commit = -1
    error_occurred = False

    for key in sorted_keys:
        value = OFFSETS[key]
        if value == 1 and error_occurred == False:
            offset_to_commit = key
        #After an exception has occured if any record has been executed, Then keep track of those records in the list
        elif value == 1 and error_occurred == True:
            executed_records_post_error["success"].append(key)
        elif value == -1:
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
    #print("Last offset: ", consumer.position(partition))
    #with open("history.txt","r") as file:
    #    json_string = file.read()
    
    #executed_records_post_error = json.loads(json_string)
    batch = consumer.poll(timeout_ms=500)  # Adjust the timeout as needed
    print("New Batch is here\n")
    print("\n\n")

    # threadpool
    futures = []
    if len(batch) == 0:
        continue

    for topic_partition, records in batch.items():
        OFFSETS.clear()

        for record in records:
            OFFSETS[record.offset] = 0

        num_records = len(records)
        min_records_per_thread = num_records // NUM_THREADS

        for i in range(NUM_THREADS):
            thread_records = []
            index = i

            # to populate thread_records with the appropriate records
            # if records available are 0-19, thread 1 gets 0,4,8,12,16.
            for j in range(min_records_per_thread + 1):
                if index < num_records:
                    thread_records.append(records[index])
                    index += NUM_THREADS

            # Submit the thread task to the thread pool
            future = pool.submit(process_thread_records, thread_records)

            futures.append(future)

    print(OFFSETS)
    barrier.wait()

    # wait for all threads to complete its execution
    for future in futures:
        future.result()
    
    print("\n after join")
    print(OFFSETS)
    commit_offsets()
    
    with open("history.txt","w") as file:
        file.write(str(executed_records_post_error))
    
    file.close()

    a = input()
    # print(batch)

    # Manually commit the OFFSETS once the batch is processed
    # consumer.commit()

# Close the consumer connection
consumer.close()
