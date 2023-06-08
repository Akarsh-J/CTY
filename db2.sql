CREATE TABLE IF NOT EXISTS Client(
    User_id char(10) PRIMARY KEY NOT NULL,
    UserName char(50) NOT NULL,
    password char(20) NOT NULL,
    F_Name char(30) NOT NULL,
    L_Name char(30),
    Phone char(10) NOT NULL,
    Addr_1 text,
    Addr_2 text
);

CREATE TABLE IF NOT EXISTS Cart(
    Cart_id int PRIMARY KEY NOT NULL,
    User_ID char(10),
    total_qty int NOT NULL,
    total_cost float(2),
    Created_at timestamp,
    modified_at timestamp,
    FOREIGN KEY(User_ID) REFERENCES client(User_id)
);

CREATE TABLE IF NOT EXISTS Order_Details(
    order_id int PRIMARY KEY,
    user_id char(10) NOT NULL,
    total_cost float(2),
    items JSONB,
    Payment_id char(10) UNIQUE,
    cart_id int NOT NULL,
    Created_at timestamp,
    Modified_at timestamp,
    FOREIGN KEY(user_id) REFERENCES client(User_id),
    FOREIGN KEY(cart_id) REFERENCES cart(Cart_id)
);

CREATE TABLE IF NOT EXISTS payment_details(
    order_id int PRIMARY KEY NOT NULL,
    transaction_id int NOT NULL,
    Amount float(2),
    Provider char(30),
    Status char(10),
    Created_at timestamp,
    payment_id char(10),
    FOREIGN KEY(order_id) REFERENCES Order_Details(order_id),
    FOREIGN KEY(payment_id) REFERENCES Order_Details(payment_id)
);

CREATE TABLE IF NOT EXISTS user_payment(
    Payment_id char(10) PRIMARY KEY NOT NULL,
    User_id char(10) NOT NULL,
    payment_type char(20),
    provider char(30),
    account_no char(18),
    expiry date,
    FOREIGN KEY(Payment_id) REFERENCES Order_Details(payment_id),
    FOREIGN KEY(user_id) REFERENCES client(User_id)
);

CREATE TABLE IF NOT EXISTS Product(
    Product_id char(10) PRIMARY KEY NOT NULL,
    Product_name text NOT NULL,
    description text,
    Category JSONB,
    Price float(2),
    Created_at timestamp,
    modified_at timestamp
);

CREATE TABLE IF NOT EXISTS Vendor(
    Vendor_id char(10) PRIMARY KEY NOT NULL,
    Vendor_name char(50) NOT NULL,
    password char(20),
    Phone char(10),
    Addr text,
    Created_at timestamp);

CREATE TABLE IF NOT EXISTS product_Vendor(
    Product_id char(10) NOT NULL,
    Vendor_id char(10) NOT NULL,
    Item_id char(10) NOT NULL UNIQUE,
    Item_Name text,Quantity int,
    Discount_Price float(2),
    Created_at timestamp,
    modified_at timestamp,
    PRIMARY KEY(Product_id, Vendor_id),
    FOREIGN KEY(Product_id) REFERENCES product(Product_id),
    FOREIGN KEY(Vendor_id) REFERENCES Vendor(Vendor_id)
);

CREATE TABLE IF NOT EXISTS Cart_items(
    cart_id int NOT NULL,
    Item_id char(10) NOT NULL,
    Quantity int,
    FOREIGN KEY(cart_id) REFERENCES cart(Cart_id),
    FOREIGN KEY(Item_id) REFERENCES Product_Vendor(item_id)
);

-------------------------------------------------------------------------------

TRUNCATE Cart CASCADE;
TRUNCATE Client CASCADE;
TRUNCATE Order_Details CASCADE;
TRUNCATE payment_details CASCADE;
TRUNCATE user_payment CASCADE;
TRUNCATE Product CASCADE;
TRUNCATE Vendor CASCADE;
TRUNCATE Product_Vendor CASCADE;
TRUNCATE Cart_items CASCADE;