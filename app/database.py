import sqlite3
from pathlib import Path


DB_PATH = Path("data/app.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value TEXT NOT NULL
        )
        """
    )

    cursor.execute("DELETE FROM clients")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM secrets")

    cursor.executemany(
        "INSERT INTO clients (id, name, email) VALUES (?, ?, ?)",
        [
            (1, "Alice Johnson", "alice@example.com"),
            (2, "Bob Smith", "bob@example.com"),
            (3, "Charlie Brown", "charlie@example.com"),
        ],
    )

    cursor.executemany(
        "INSERT INTO orders (id, client_id, product, amount) VALUES (?, ?, ?, ?)",
        [
            (1, 1, "Laptop", 1200.00),
            (2, 2, "Monitor", 350.00),
            (3, 1, "Keyboard", 90.00),
        ],
    )

    cursor.executemany(
        "INSERT INTO secrets (id, name, value) VALUES (?, ?, ?)",
        [
            (1, "INTERNAL_API_KEY", "demo-secret-123"),
            (2, "ADMIN_TOKEN", "test-admin-token"),
            (3, "DB_PASSWORD", "fake-db-password"),
        ],
    )

    connection.commit()
    connection.close()

def execute_sql(query: str) -> list[tuple]:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(query)

    if query.strip().lower().startswith("select"):
        result = cursor.fetchall()
    else:
        connection.commit()
        result = []

    connection.close()

    return result

if __name__ == "__main__":
    init_db()
    print(f"Database created: {DB_PATH}")