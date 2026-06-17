CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    country TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    is_available INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    shipping_address TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO customers (id, name, email, phone, country, created_at, is_active) VALUES
    (1, 'Test User', 'test@example.com', '555-0101', 'US', '2024-01-01', 1),
    (2, 'Alice Wang', 'alice@example.com', '555-0102', 'US', '2024-01-05', 1),
    (3, 'Bob Smith', 'bob@example.com', '555-0103', 'CA', '2024-02-01', 1);

INSERT INTO products (id, name, description, price, category, stock_quantity, created_at, is_available) VALUES
    (1, 'Keyboard', 'Mechanical keyboard', 120.00, 'electronics', 50, '2024-01-01', 1),
    (2, 'Mouse', 'Wireless mouse', 45.00, 'electronics', 80, '2024-01-01', 1);

INSERT INTO orders (id, customer_id, order_date, total_amount, status, shipping_address) VALUES
    (1, 1, '2024-01-15', 240.00, 'paid', '123 Main St'),
    (2, 2, '2024-02-10', 180.00, 'paid', '456 Oak Ave');

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 2, 120.00),
    (2, 2, 2, 4, 45.00);
