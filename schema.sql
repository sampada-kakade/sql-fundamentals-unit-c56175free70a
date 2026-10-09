DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE loans (
    id          INTEGER PRIMARY KEY,
    member_id   INTEGER NOT NULL REFERENCES members (id),
    book_title  TEXT NOT NULL,
    loan_date   TEXT NOT NULL,
    return_date TEXT
);

