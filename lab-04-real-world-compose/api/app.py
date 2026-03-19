"""
Task Manager API — A simple Flask application backed by PostgreSQL.

This is the backend service for Lab 04. It provides a REST API for
managing tasks (create and list). It connects to PostgreSQL using
the psycopg2 library and reads all database configuration from
environment variables.

Endpoints:
    GET  /api/tasks   — List all tasks
    POST /api/tasks   — Create a new task (JSON body: {"title": "..."})
    GET  /api/health  — Health check (verifies database connectivity)
"""

import os
import time
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Database configuration — all values come from environment variables.
# These are set in the .env file and passed to the container via
# docker-compose.yml's "env_file" directive.
# ---------------------------------------------------------------------------
DB_HOST = os.environ.get("POSTGRES_HOST", "db")        # Service name in Compose
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "taskmanager")
DB_USER = os.environ.get("POSTGRES_USER", "admin")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "secretpassword")


def get_db_connection():
    """
    Open a new connection to the PostgreSQL database.

    We use the service name "db" as the hostname because Docker Compose
    creates a shared network where each service is reachable by its name.
    """
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )


def init_db():
    """
    Create the 'tasks' table if it doesn't already exist.

    This runs once at application startup. In a production app you'd use
    a proper migration tool, but for this lab simple CREATE IF NOT EXISTS
    does the job.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id    SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done  BOOLEAN DEFAULT FALSE
            );
        """)
        conn.commit()
        cur.close()
    finally:
        conn.close()


def wait_for_db(max_retries=10, delay=2):
    """
    Wait for the PostgreSQL database to become available.

    Even though docker-compose.yml has "depends_on: db", that only waits
    for the container to START — it doesn't wait for PostgreSQL to be
    READY to accept connections. This retry loop handles that gap.
    """
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_db_connection()
            conn.close()
            print(f"✅ Database is ready (attempt {attempt}/{max_retries})")
            return
        except psycopg2.OperationalError:
            print(f"⏳ Waiting for database... (attempt {attempt}/{max_retries})")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after multiple retries.")


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    """
    GET /api/tasks — Return all tasks as a JSON array.

    Example response:
        [
            {"id": 1, "title": "Buy groceries", "done": false},
            {"id": 2, "title": "Walk the dog", "done": false}
        ]
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id;")
        rows = cur.fetchall()
        cur.close()

        tasks = [
            {"id": row[0], "title": row[1], "done": row[2]}
            for row in rows
        ]
        return jsonify(tasks)
    finally:
        conn.close()


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """
    POST /api/tasks — Create a new task.

    Expects a JSON body with a "title" field:
        {"title": "Buy groceries"}

    Returns the created task with its assigned ID:
        {"id": 1, "title": "Buy groceries", "done": false}
    """
    data = request.get_json()

    # Validate input
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "A 'title' field is required."}), 400

    title = data["title"].strip()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done;",
            (title,),
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()

        task = {"id": row[0], "title": row[1], "done": row[2]}
        return jsonify(task), 201
    finally:
        conn.close()


@app.route("/api/health", methods=["GET"])
def health():
    """
    GET /api/health — Simple health check.

    Verifies that the API can connect to PostgreSQL and returns
    the connection status. Used by monitoring tools and by you
    during this lab to confirm everything is wired up correctly.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except psycopg2.OperationalError:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 503


# ---------------------------------------------------------------------------
# Application startup
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Wait for PostgreSQL to be ready, then create the table
    wait_for_db()
    init_db()
    print("🚀 Task Manager API is running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)