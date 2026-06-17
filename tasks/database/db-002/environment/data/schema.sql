CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO customers (id, name, city) VALUES
    (1, 'Alice Wang', 'New York'),
    (2, 'Bob Smith', 'Chicago'),
    (3, 'Carol Jones', 'New York'),
    (4, 'David Lee', 'San Francisco'),
    (5, 'Eva Garcia', 'Chicago'),
    (6, 'Frank Miller', 'Boston');

INSERT INTO products (id, name, price) VALUES
    (1, 'Laptop Stand', 45.00),
    (2, 'Monitor', 220.00),
    (3, 'Keyboard', 75.50),
    (4, 'Office Chair', 300.00);

INSERT INTO orders (id, customer_id, product_id, amount, order_date) VALUES
    (1, 1, 2, 500.00, '2024-01-10'),
    (2, 1, 3, 255.50, '2024-02-12'),
    (3, 2, 4, 430.25, '2024-01-18'),
    (4, 2, 1, 300.00, '2024-03-05'),
    (5, 3, 2, 660.00, '2024-02-01'),
    (6, 4, 4, 500.50, '2024-01-28'),
    (7, 4, 3, 325.00, '2024-03-11'),
    (8, 5, 2, 870.00, '2024-02-20');
