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
        database="postgres",
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

        if db == "store_address":
            id = msg["data"]["id"]
            locality = msg["data"]["locality"]
            city = msg["data"]["city"]
            state = msg["data"]["state"]
            user_id = msg["data"]["user_id"]

            query = f"INSERT INTO store_address VALUES ('{id}','{locality}','{city}','{state}','{user_id}')"
            cursor.execute(query)
            connection.commit()

            print(f"Message '{query}' inserted into the database")

        if db == "auth_user":
            id = msg["data"]["id"]
            password = msg["data"]["password"]
            last_login = msg["data"]["last_login"]
            is_superuser = msg["data"]["is_superuser"]
            username = msg["data"]["username"]
            first_name = msg["data"]["first_name"]
            last_name = msg["data"]["last_name"]
            email = msg["data"]["email"]
            is_staff = msg["data"]["is_staff"]
            is_active = msg["data"]["is_active"]
            date_joined = msg["data"]["date_joined"]

            query = f"INSERT INTO auth_user VALUES ('{id}', '{password}', '{last_login}', {is_superuser}, '{username}', '{first_name}', '{last_name}', '{email}', {is_staff}, {is_active}, '{date_joined}')"
            cursor.execute(query)
            connection.commit()

            print(f"Message '{query}' inserted into the database")

        if msg["db"] == "store_cart":
            id = msg["data"]["id"]
            quantity = msg["data"]["quantity"]
            created_at = msg["data"]["created_at"]
            updated_at = msg["data"]["updated_at"]
            product_id = msg["data"]["product_id"]
            user_id = msg["data"]["user_id"]

            query = f"INSERT INTO store_cart VALUES ('{id}', '{quantity}', '{created_at}', '{updated_at}', '{product_id}', '{user_id}')"
            cursor.execute(query)
            connection.commit()

            print(f"Message '{query}' inserted into the database")

        if msg["db"] == "store_product":
            id = msg["data"]["id"]
            title = msg["data"]["title"]
            slug = msg["data"]["slug"]
            short_description = msg["data"]["short_description"]
            detail_description = msg["data"]["detail_description"]
            product_image = msg["data"]["product_image"]
            price = msg["data"]["price"]
            is_active = msg["data"]["is_active"]
            is_featured = msg["data"]["is_featured"]
            created_at = msg["data"]["created_at"]
            updated_at = msg["data"]["updated_at"]
            category_id = msg["data"]["category_id"]
            sku = msg["data"]["sku"]

            query = f"INSERT INTO store_product VALUES ('{id}', '{title}', '{slug}', '{short_description}', '{detail_description}', '{product_image}', {price}, {is_active}, {is_featured}, '{created_at}', '{updated_at}', '{category_id}', '{sku}')"
            cursor.execute(query)
            connection.commit()

            print(f"Message '{query}' inserted into the database")

        if msg["db"] == "store_order":
            id = msg["data"]["id"]
            quantity = msg["data"]["quantity"]
            ordered_date = msg["data"]["ordered_date"]
            status = msg["data"]["status"]
            address_id = msg["data"]["address_id"]
            product_id = msg["data"]["product_id"]
            user_id = msg["data"]["user_id"]

            query = f"INSERT INTO store_order VALUES ('{id}', '{quantity}', '{ordered_date}', '{status}', '{address_id}', '{product_id}', '{user_id}')"
            cursor.execute(query)
            connection.commit()

            print(f"Message '{query}' inserted into the database")

        # print(db, operation)

        # query = (f"INSERT INTO sample VALUES ('{msg[0]}', '{msg[1]}', {msg[2]}, {msg[2]})")

        # Execute the query
        # cursor.execute(query)
        # connection.commit()

        # Print confirmation
        # print(f"Message '{message.value.decode('utf-8')}' inserted into the database")
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
