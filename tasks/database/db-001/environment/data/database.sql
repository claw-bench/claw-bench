-- Employee database for db-001: Basic SQL Query
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary INTEGER NOT NULL,
    hire_date TEXT NOT NULL
);

INSERT INTO employees (id, name, department, salary, hire_date) VALUES
    (1, 'Alice Chen',   'Engineering', 95000, '2021-03-15'),
    (2, 'Bob Smith',    'Marketing',   72000, '2019-07-01'),
    (3, 'Carol White',  'Engineering', 91000, '2020-11-20'),
    (4, 'Dan Lee',      'Sales',       68000, '2022-01-10'),
    (5, 'Eva Johnson',  'Engineering', 88000, '2018-05-30'),
    (6, 'Frank Liu',    'Engineering', 78000, '2023-02-14'),
    (7, 'Grace Kim',    'Marketing',   85000, '2017-09-09'),
    (8, 'Henry Brown',  'Engineering', 82000, '2021-12-01'),
    (9, 'Ivy Davis',    'Sales',       90000, '2016-04-22'),
    (10, 'Jack Wilson', 'Engineering', 75000, '2022-08-18');
