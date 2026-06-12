-- Schema and seed data for db-002: Multi-Table JOIN with Aggregation

CREATE TABLE customers (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);

CREATE TABLE products (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id  INTEGER REFERENCES products(id),
    amount      REAL NOT NULL
);

INSERT INTO customers (id, name, city) VALUES
    (1, 'Alice Wang',  'New York'),
    (2, 'Bob Smith',   'Chicago'),
    (3, 'Carol Jones', 'New York'),
    (4, 'David Lee',   'San Francisco'),
    (5, 'Eva Garcia',  'Chicago'),
    (6, 'Frank Miller','New York');

INSERT INTO products (id, name, price) VALUES
    (1, 'Widget',  50.00),
    (2, 'Gadget',  120.25),
    (3, 'Gizmo',   75.50);

-- Each customer's orders sum to the expected total_spend.
INSERT INTO orders (id, customer_id, product_id, amount) VALUES
    -- Alice Wang -> 755.50
    (1,  1, 1, 500.00),
    (2,  1, 3, 255.50),
    -- Bob Smith -> 730.25
    (3,  2, 2, 400.00),
    (4,  2, 1, 330.25),
    -- Carol Jones -> 660.00
    (5,  3, 3, 300.00),
    (6,  3, 2, 360.00),
    -- David Lee -> 825.50
    (7,  4, 1, 425.50),
    (8,  4, 2, 400.00),
    -- Eva Garcia -> 870.00
    (9,  5, 2, 470.00),
    (10, 5, 3, 400.00);
    -- Frank Miller has no orders and must not appear in results.
