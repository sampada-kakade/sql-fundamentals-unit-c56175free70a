import os
import sqlite3
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_sql(name):
    # utf-8-sig skips a byte-order mark if an editor added one
    with open(os.path.join(ROOT, name), encoding="utf-8-sig") as f:
        return f.read()


def run_script(conn, text):
    """Run every statement in order, like DBeaver's Execute Script.
    Returns one (column_names, rows) pair per SELECT."""
    results = []
    statement = ""
    for line in text.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            cur = conn.execute(statement)
            if cur.description is not None:
                columns = [d[0] for d in cur.description]
                results.append((columns, cur.fetchall()))
            statement = ""
    code = [l for l in statement.splitlines() if not l.strip().startswith("--")]
    if "".join(code).strip():
        raise AssertionError("unfinished statement (missing ;?): " + statement)
    return results


class LoansReportTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        run_script(self.conn, read_sql("schema.sql"))
        self.selects = run_script(self.conn, read_sql("loans_report.sql"))

    def tearDown(self):
        self.conn.close()

    def test_script_has_two_selects(self):
        self.assertEqual(len(self.selects), 2)

    def test_members_select_shows_all_three_with_every_column(self):
        columns, rows = self.selects[0]
        self.assertEqual(columns, ["id", "name", "email"])
        self.assertEqual(rows, [
            (1, "Alice Smith", "alice@example.com"),
            (2, "Bob Jones", "bob@example.com"),
            (3, "Carol White", "carol@example.com"),
        ])

    def test_loans_were_inserted(self):
        rows = self.conn.execute(
            "SELECT member_id, book_title, loan_date, return_date "
            "FROM loans ORDER BY id").fetchall()
        self.assertEqual(rows, [
            (1, "The Great Gatsby", "2025-04-01", None),
            (2, "1984", "2025-03-15", "2025-03-30"),
        ])

    def test_report_lists_only_unreturned_books_with_member_name(self):
        columns, rows = self.selects[1]
        self.assertEqual(columns, ["book_title", "name"])
        self.assertEqual(rows, [("The Great Gatsby", "Alice Smith")])

    def test_report_picks_up_any_new_unreturned_loan(self):
        self.conn.execute(
            "INSERT INTO loans (member_id, book_title, loan_date) "
            "VALUES (3, 'Dune', '2025-04-10')")
        text = read_sql("loans_report.sql")
        report_sql = text[text.index("-- 4."):]
        _, rows = run_script(self.conn, report_sql)[0]
        self.assertEqual(sorted(rows), [
            ("Dune", "Carol White"),
            ("The Great Gatsby", "Alice Smith"),
        ])

    def test_running_both_scripts_again_gives_same_results(self):
        run_script(self.conn, read_sql("schema.sql"))
        again = run_script(self.conn, read_sql("loans_report.sql"))
        self.assertEqual(again, self.selects)


if __name__ == "__main__":
    unittest.main()

