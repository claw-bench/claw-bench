CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    created_at TEXT NOT NULL
);

INSERT INTO users (id, name, email, address, created_at) VALUES
    (1, 'Alice Chen', 'alice@example.com', '123 Main St, Springfield, IL, 62701', '2021-01-15'),
    (2, 'Bob Martinez', 'bob@example.com', '456 Oak Ave, Chicago, IL, 60601', '2021-02-20'),
    (3, 'Carol White', 'carol@example.com', '789 Pine Rd, Austin, TX, 73301', '2021-03-25'),
    (4, 'David Kim', 'david@example.com', '321 Elm Blvd, Seattle, WA, 98101', '2021-04-30'),
    (5, 'Eva Johnson', 'eva@example.com', '654 Cedar Ln, Denver, CO, 80201', '2021-05-18'),
    (6, 'Frank Liu', 'frank@example.com', '987 Birch Dr, Boston, MA, 02101', '2021-06-12'),
    (7, 'Grace Park', 'grace@example.com', '147 Maple Ct, Portland, OR, 97201', '2021-07-22'),
    (8, 'Henry Brown', 'henry@example.com', '258 Walnut Way, Miami, FL, 33101', '2021-08-09');
