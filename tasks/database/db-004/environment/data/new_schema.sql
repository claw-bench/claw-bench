CREATE TABLE users_new (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users_new(id)
);
