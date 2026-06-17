CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary INTEGER NOT NULL,
    hire_date TEXT NOT NULL
);

INSERT INTO employees (id, name, department, salary, hire_date) VALUES
    (1, 'Alice Chen', 'Engineering', 95000, '2021-03-15'),
    (2, 'Bob Smith', 'Sales', 72000, '2020-07-01'),
    (3, 'Carol White', 'Engineering', 91000, '2019-11-20'),
    (4, 'David Kim', 'Marketing', 81000, '2022-01-10'),
    (5, 'Eva Johnson', 'Engineering', 88000, '2021-09-05'),
    (6, 'Frank Liu', 'Engineering', 78000, '2023-02-14'),
    (7, 'Grace Park', 'HR', 69000, '2020-04-22'),
    (8, 'Henry Brown', 'Engineering', 85000, '2018-06-30'),
    (9, 'Ivy Davis', 'Finance', 97000, '2017-12-12'),
    (10, 'Jack Wilson', 'Engineering', 75000, '2022-10-03');
