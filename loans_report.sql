-- 1. Add three new library members.
INSERT INTO members (name, email) VALUES ('Alice Smith', 'alice@example.com');
INSERT INTO members (name, email) VALUES ('Bob Jones', 'bob@example.com');
INSERT INTO members (name, email) VALUES ('Carol White', 'carol@example.com');

-- 2. Check the inserts worked.
SELECT * FROM members;

-- 3. Record two loans. A book that is still out has no return date (NULL).
INSERT INTO loans (member_id, book_title, loan_date, return_date)
VALUES (1, 'The Great Gatsby', '2025-04-01', NULL);
INSERT INTO loans (member_id, book_title, loan_date, return_date)
VALUES (2, '1984', '2025-03-15', '2025-03-30');

-- 4. Books currently on loan, with the name of the member who has each one.
SELECT loans.book_title, members.name
FROM loans
JOIN members ON members.id = loans.member_id
WHERE loans.return_date IS NULL;