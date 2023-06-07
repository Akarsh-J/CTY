from kafka import KafkaConsumer
from time import sleep,time
import psycopg2
import json

start_time = time()

consumer = KafkaConsumer(
    'ecom2',
    bootstrap_servers="localhost:9092",
    group_id="HPE-CTY-single-threaded",
    max_poll_records=20,
    enable_auto_commit=False,  # Disable auto commit
    auto_offset_reset="earliest",
)

def process_message(message):
    
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="cty",
        user="akarshj21",
        password="AkArshj21",
    )

    cursor = connection.cursor()
    
    try:
        msg = message.value.decode("utf-8")
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
        
    except Exception as e:
        #print("An error occured: ", str(e))
        print(f"Error processing message '{message.value.decode('utf-8')}': {str(e)}")
        connection.rollback()   #to avoid the error:  current transaction is aborted, commands ignored until end of transaction block
        with open("errors.txt", "a") as file:
            file.write(str({message.offset: str(e)})+"\n")
            
        file.close()
            

i=0
while True:
    messages = consumer.poll(timeout_ms = 2000)
    print(i)
    i+=1
    if not messages:
        
        break
    for topic_partition, records in messages.items():
        for record in records:
            message = record.value
            offset = record.offset
            print(f"{offset}: {message}")
            process_message(record)
            

consumer.close()

end_time = time()

exec_time = end_time - start_time
print("Time taken to execute = ", exec_time)
            