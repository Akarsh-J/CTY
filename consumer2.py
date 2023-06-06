from kafka import KafkaConsumer
import psycopg2
import threading
from queue import Queue
import json

# Initialize Kafka consumer
consumer = KafkaConsumer("insert", bootstrap_servers="localhost:9092")

# Thread worker function


def process_message(message):
    # Establish PostgreSQL connection
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="cty",
        user="akarshj21",
        password="AkArshj21",
    )

    cursor = connection.cursor()

    try:
        # Convert the message to a query
        msg = message.value.decode("utf-8")
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

    except Exception as e:
        print(f"Error processing message '{message.value.decode('utf-8')}': {str(e)}")
    finally:
        # Close the connection
        connection.close()


# Queue to hold messages
message_queue = Queue()

# Thread worker function


def worker():
    while True:
        message = message_queue.get()
        process_message(message)
        message_queue.task_done()


# Create and start worker threads
num_threads = 4  # Number of consumer threads
for _ in range(num_threads):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

# Process messages
for message in consumer:
    message_queue.put(message)

# Wait for all messages to be processed
message_queue.join()
