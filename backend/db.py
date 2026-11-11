from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("nexa.db")


def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize():
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                symbol TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO products (id, name, category, description, symbol, score)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (1, "Pulse headphones", "Tecnología", "Audio inmersivo para concentrarte.", "◉", 0.96),
                    (2, "Luma desk lamp", "Hogar", "Luz cálida para cada idea.", "◒", 0.91),
                    (3, "Orbit backpack", "Movilidad", "Diseñada para moverte ligero.", "◌", 0.88),
                    (4, "Node keyboard", "Tecnología", "Precisión para crear más rápido.", "⌨", 0.86),
                    (5, "Moss speaker", "Hogar", "Sonido ambiente para tus espacios.", "◍", 0.82),
                    (6, "Loop bottle", "Movilidad", "Hidratación para todos tus trayectos.", "○", 0.79),
                ],
            )


def products(category=None):
    with connection() as conn:
        if category and category != "Todos":
            rows = conn.execute(
                "SELECT * FROM products WHERE category = ? ORDER BY score DESC", (category,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM products ORDER BY score DESC").fetchall()
        return [dict(row) for row in rows]


def save_preference(user_id, product_id):
    with connection() as conn:
        exists = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if exists is None:
            raise ValueError("El producto indicado no existe.")
        conn.execute(
            "INSERT INTO preferences (user_id, product_id) VALUES (?, ?)",
            (user_id, product_id),
        )

