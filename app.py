import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "todo_db"),
        user=os.getenv("DB_USER", "todo_user"),
        password=os.getenv("DB_PASSWORD", "todo_password"),
        port=os.getenv("DB_PORT", "5432")
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, task, done FROM todos ORDER BY id DESC;")
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")

    if task:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (task) VALUES (%s);", (task,))
        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for("index"))


@app.route("/done/<int:todo_id>")
def done(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE todos SET done = TRUE WHERE id = %s;", (todo_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s;", (todo_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)