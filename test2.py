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
    group_id="HPE-CTY",
    enable_auto_commit=False,  # Disable auto commit
    max_poll_records=20,  # Set the maximum number of records to fetch in each poll
    auto_offset_reset="latest",
)

partition = TopicPartition("ecom", 0)
consumer.assign([partition])


NUM_THREADS = 4

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

                if operation=="insert":
                
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


                    elif msg["db"] == "Cart":
                        cart_id, user_id, total_qty, total_cost, created_at, modified_at = msg["data"].values()
                        query = f"INSERT INTO Cart VALUES ({cart_id}, '{user_id}', {total_qty}, {total_cost}, '{created_at}', '{modified_at}')"

                    elif msg["db"] == "Order_Details":
                        order_id, user_id, total_cost, items, payment_id, cart_id, created_at, modified_at= msg["data"].values()
                        items = json.dumps(items)
                        query = f"INSERT INTO Order_Details VALUES ({order_id}, '{user_id}', {total_cost}, '{items}', '{payment_id}', {cart_id}, '{created_at}', '{modified_at}')"

                    elif msg["db"] == "Payment_Details":
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

                    elif msg["db"] == "User_Payment":
                        payment_id, user_id, payment_type, provider, account_no, expiry = msg["data"].values()
                        query = f"INSERT INTO user_payment VALUES ('{payment_id}', '{user_id}', '{payment_type}', '{provider}', '{account_no}', '{expiry}')"

                    elif msg["db"] == "Product":
                        product_id= msg["data"]["Product_id"]
                        product_name = msg["data"]["Product_name"]
                        description = msg["data"]["description"]
                        category = json.dumps(msg["data"]["Category"])
                        price = msg["data"]["Price"]
                        created_at = msg["data"]["Created_at"]
                        modified_at = msg["data"]["modified_at"]

                        query = f"INSERT INTO Product VALUES ('{product_id}', '{product_name}', '{description}', '{category}', {price}, '{created_at}', '{modified_at}')"

                    elif msg["db"] == "Vendor":
                        vendor_id, vendor_name, password, phone, addr, created_at = msg["data"].values()
                        query = f"INSERT INTO Vendor VALUES ('{vendor_id}', '{vendor_name}', '{password}', '{phone}', '{addr}', '{created_at}')"


                    elif msg["db"] == "Product_Vendor":
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

                        query = f"INSERT INTO Product_Vendor VALUES ('{product_id}', '{vendor_id}', '{item_id}', '{item_name}', {quantity}, {discount_price}, '{created_at}', '{modified_at}')"

                    elif msg["db"] == "Cart_Items":
                        cart_id, item_id, quantity = msg["data"].values()

                        query = f"INSERT INTO Cart_Items VALUES ({cart_id}, '{item_id}', {quantity})"


                
                elif operation=="update":
                    if msg["db"] == "Client":
                        val1, val2, val3=msg["data"].values()
                        query=f"UPDATE Client set UserName='{val2}', Password='{val3}' where User_id='{val1}'"
                    elif msg["db"]=="Cart":
                        val1, val2, val3=msg["data"].values()
                        query=f"Update Cart Set total_qty={val2}, total_cost={val3} where Cart_id='{val1}'"
                    elif msg["db"]=="Order_Details":
                        val1, val2, val3=msg["data"].values()
                        val3 = json.dumps(val3)
                        query=f"Update Order_Details Set total_cost={val2}, items='{val3}' where Order_id='{val1}'"
                    elif msg["db"]=="Payment_Details":
                        val1, val2=msg["data"].values()
                        query=f"Update Payment_Details Set Amount={val2} where transaction_id='{val1}'"
                    elif msg["db"]=="User_Payment":
                        val1, val2= msg["data"].values()
                        query=f"Update User_Payment set account_no='{val2}' where Payment_id='{val1}'"
                    elif msg["db"]=="Product":
                        val1, val2=msg["data"].values()
                        query=f"Update Product set description='{val2}' where Product_id='{val1}'"
                    elif msg["db"]=="Vendor":
                        val1, val2= msg["data"].values()
                        query=f"Update Vendor set Vendor_name='{val2}' where Vendor_id='{val1}'"
                    elif msg["db"]=="Product_Vendor":
                        val1, val2, val3, val4= msg["data"].values()
                        query=f"Update Product_Vendor set Discount_Price={val4} where Product_id='{val1}' AND Vendor_id='{val2}' AND Item_id='{val3}'"
                    elif msg["db"]=="Cart_Items":
                        val1, val2, val3= msg["data"].values()
                        query=f"Update Cart_Items set Quantity={val3} where cart_id='{val1}' AND Item_id='{val2}'"


                else:
                    if msg["db"] == "Client":
                        val1,=msg["data"].values()
                        print("val1: ", val1)
                        query=f"Delete from Client where User_id='{val1}'"
                    elif msg["db"]=="Cart":
                        val1,=msg["data"].values()
                        query=f"Delete from Cart where Cart_id='{val1}'"
                    elif msg["db"]=="Order_Details":
                        val1,=msg["data"].values()
                        query=f"Delete from Order_Details where Order_id='{val1}'"
                    elif msg["db"]=="Payment_Details":
                        val1,=msg["data"].values()
                        query=f"Delete from Payment_Details where transaction_id='{val1}'"
                    elif msg["db"]=="User_Payment":
                        val1,= msg["data"].values()
                        query=f"Delete from User_Payment where Payment_id='{val1}'"
                    elif msg["db"]=="Product":
                        val1,=msg["data"].values()
                        query=f"Delete from Product where Product_id='{val1}'"
                    elif msg["db"]=="Vendor":
                        val1,= msg["data"].values()
                        query=f"Delete from Vendor where Vendor_id='{val1}'"
                    elif msg["db"]=="Product_Vendor":
                        val1, val2, val3= msg["data"].values()
                        query=f"Delete from Product_Vendor where Product_id='{val1}' AND Vendor_id='{val2}' AND Item_id='{val3}'"
                    elif msg["db"]=="Cart_Items":
                        val1, val2= msg["data"].values()
                        query=f"Delete from Cart_Items where cart_id='{val1}' AND Item_id='{val2}'"
                
                cursor.execute(query)
                connection.commit()
                print(f"Message '{query}' inserted into the database")
                print(threading.current_thread().name, record.offset)
                # print(record.offset)
                OFFSETS[record.offset] = 1
                #print(OFFSETS)
                if record.offset in executed_records_post_error["error"].keys():
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
                        if record.offset in executed_records_post_error["error"].keys():
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
        # After commiting, seek to make consumer to read from the next offset
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
