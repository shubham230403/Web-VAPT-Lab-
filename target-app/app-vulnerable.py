from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import subprocess
import os

app = Flask(__name__)

DATABASE = "vapt_lab.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            comment TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL
        )
    """)

    # Demo users
    try:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("alice", "alice123", "user")
        )
    except sqlite3.IntegrityError:
        pass

    # Demo products
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ("Laptop", "Security testing laptop", 75000),
            ("Keyboard", "Mechanical keyboard", 3500),
            ("Mouse", "Wireless mouse", 1500),
            ("Monitor", "24 inch monitor", 12000)
        ]

        conn.executemany(
            "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()


# ============================================================
# HTML
# ============================================================

BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Web VAPT Lab</title>
    <style>
        body {
            font-family: Arial;
            margin: 40px;
            background: #f4f4f4;
        }

        .container {
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
        }

        input, textarea, button {
            padding: 10px;
            margin: 5px;
            width: 90%;
        }

        button {
            width: auto;
            cursor: pointer;
        }

        .card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 6px;
        }

        nav a {
            margin-right: 15px;
        }

        .warning {
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
        }
    </style>
</head>

<body>
<div class="container">

<nav>
    <a href="/">Home</a>
    <a href="/login">Login</a>
    <a href="/search">Search</a>
    <a href="/comment">Comments</a>
    <a href="/profile?id=1">Profile</a>
    <a href="/admin">Admin</a>
    <a href="/upload">Upload</a>
    <a href="/ping">Network Diagnostic</a>
    <a href="/file?name=notes.txt">File Viewer</a>
</nav>

<hr>

{{ content|safe }}

</div>
</body>
</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    content = """
    <h1>Web Application VAPT Lab</h1>

    <div class="warning">
        <strong>Authorized Training Environment</strong><br>
        This application is intentionally vulnerable and exists
        only for local security testing and learning.
    </div>

    <h2>Application Modules</h2>

    <ul>
        <li>Authentication</li>
        <li>Search</li>
        <li>User Profiles</li>
        <li>Comments</li>
        <li>Administration</li>
        <li>File Viewer</li>
        <li>Network Diagnostics</li>
        <li>File Upload</li>
    </ul>

    <h2>Potential Security Testing Areas</h2>

    <ul>
        <li>SQL Injection</li>
        <li>Cross-Site Scripting</li>
        <li>Broken Access Control / IDOR</li>
        <li>Command Injection</li>
        <li>Path Traversal</li>
        <li>Unrestricted File Upload</li>
        <li>Authentication weaknesses</li>
        <li>Security Misconfiguration</li>
    </ul>
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db()

        # INTENTIONALLY VULNERABLE TO SQL INJECTION
        query = f"""
            SELECT id, username, role
            FROM users
            WHERE username = '{username}'
            AND password = '{password}'
        """

        try:
            user = conn.execute(query).fetchone()

            if user:
                message = (
                    f"<h3>Login successful</h3>"
                    f"<p>Welcome {user['username']}</p>"
                    f"<p>Role: {user['role']}</p>"
                )
            else:
                message = "<p>Invalid username or password.</p>"

        except Exception as error:
            message = f"<p>Database error: {error}</p>"

        conn.close()

    content = f"""
    <h1>Login</h1>

    {message}

    <form method="POST">

        <input
            type="text"
            name="username"
            placeholder="Username"
        >

        <input
            type="password"
            name="password"
            placeholder="Password"
        >

        <button type="submit">Login</button>

    </form>
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# SEARCH - SQL INJECTION
# ============================================================

@app.route("/search")
def search():

    search_term = request.args.get("q", "")

    conn = get_db()

    # INTENTIONALLY VULNERABLE
    query = f"""
        SELECT id, name, description, price
        FROM products
        WHERE name LIKE '%{search_term}%'
    """

    try:
        products = conn.execute(query).fetchall()
    except Exception as error:
        products = []
        error_message = str(error)
    else:
        error_message = ""

    conn.close()

    results = ""

    for product in products:
        results += f"""
        <div class="card">
            <h3>{product['name']}</h3>
            <p>{product['description']}</p>
            <strong>₹{product['price']}</strong>
        </div>
        """

    content = f"""
    <h1>Product Search</h1>

    <form method="GET">

        <input
            type="text"
            name="q"
            placeholder="Search products"
            value="{search_term}"
        >

        <button type="submit">Search</button>

    </form>

    {error_message}

    {results}
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# PROFILE - IDOR / BROKEN ACCESS CONTROL
# ============================================================

@app.route("/profile")
def profile():

    user_id = request.args.get("id", "1")

    conn = get_db()

    # INTENTIONALLY NO AUTHORIZATION CHECK
    query = f"""
        SELECT id, username, role
        FROM users
        WHERE id = {user_id}
    """

    try:
        user = conn.execute(query).fetchone()
    except Exception as error:
        user = None
        error_message = str(error)
    else:
        error_message = ""

    conn.close()

    if not user:
        content = "<h2>User not found</h2>"
    else:
        content = f"""
        <h1>User Profile</h1>

        <div class="card">
            <p>User ID: {user['id']}</p>
            <p>Username: {user['username']}</p>
            <p>Role: {user['role']}</p>
        </div>
        """

    content += f"<p>{error_message}</p>"

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# COMMENTS - STORED XSS
# ============================================================

@app.route("/comment", methods=["GET", "POST"])
def comment():

    conn = get_db()

    if request.method == "POST":

        username = request.form.get("username", "anonymous")
        comment_text = request.form.get("comment", "")

        conn.execute(
            "INSERT INTO comments (username, comment) VALUES (?, ?)",
            (username, comment_text)
        )

        conn.commit()

    comments = conn.execute(
        "SELECT username, comment FROM comments ORDER BY id DESC"
    ).fetchall()

    conn.close()

    comment_html = ""

    for comment_item in comments:

        # INTENTIONALLY VULNERABLE TO STORED XSS
        comment_html += f"""
        <div class="card">
            <strong>{comment_item['username']}</strong>
            <p>{comment_item['comment']}</p>
        </div>
        """

    content = f"""
    <h1>Comments</h1>

    <form method="POST">

        <input
            type="text"
            name="username"
            placeholder="Your name"
        >

        <textarea
            name="comment"
            placeholder="Write a comment"
        ></textarea>

        <button type="submit">Post Comment</button>

    </form>

    <h2>Comments</h2>

    {comment_html}
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# ADMIN - BROKEN ACCESS CONTROL
# ============================================================

@app.route("/admin")
def admin():

    # INTENTIONALLY NO AUTHENTICATION / AUTHORIZATION

    content = """
    <h1>Admin Panel</h1>

    <div class="card">
        <h3>Administrative Functions</h3>

        <ul>
            <li>User Management</li>
            <li>System Configuration</li>
            <li>Security Logs</li>
            <li>Application Settings</li>
        </ul>
    </div>
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# FILE VIEWER - PATH TRAVERSAL
# ============================================================

@app.route("/file")
def file_viewer():

    filename = request.args.get("name", "notes.txt")

    # INTENTIONALLY VULNERABLE
    filepath = os.path.join(
        os.path.dirname(__file__),
        filename
    )

    try:

        with open(filepath, "r", encoding="utf-8") as file:
            data = file.read()

        content = f"""
        <h1>File Viewer</h1>

        <pre>{data}</pre>
        """

    except Exception as error:

        content = f"""
        <h1>File Viewer</h1>

        <p>Error: {error}</p>
        """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# COMMAND INJECTION
# ============================================================

@app.route("/ping")
def ping():

    host = request.args.get("host", "127.0.0.1")

    # INTENTIONALLY VULNERABLE
    command = f"ping -n 1 {host}"

    result = subprocess.getoutput(command)

    content = f"""
    <h1>Network Diagnostic</h1>

    <p>Host: {host}</p>

    <pre>{result}</pre>
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# FILE UPLOAD
# ============================================================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    message = ""

    if request.method == "POST":

        uploaded_file = request.files.get("file")

        if uploaded_file:

            filepath = os.path.join(
                UPLOAD_FOLDER,
                uploaded_file.filename
            )

            # INTENTIONALLY NO FILE TYPE VALIDATION
            uploaded_file.save(filepath)

            message = f"""
            <p>
                File uploaded successfully:
                {uploaded_file.filename}
            </p>
            """

    content = f"""
    <h1>File Upload</h1>

    {message}

    <form method="POST" enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
            Upload
        </button>

    </form>
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# INFORMATION DISCLOSURE
# ============================================================

@app.route("/debug")
def debug():

    # INTENTIONALLY DISCLOSES ENVIRONMENT INFORMATION

    content = f"""
    <h1>Debug Information</h1>

    <pre>
Application Path: {os.path.abspath(__file__)}
Current Working Directory: {os.getcwd()}
Python Version: {os.sys.version}
Environment Variables:
{dict(os.environ)}
    </pre>
    """

    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("=" * 70)
    print("Web-VAPT-Lab - Intentionally Vulnerable Application")
    print("=" * 70)
    print("Application: http://127.0.0.1:5005")
    print("Mode: VULNERABLE")
    print("=" * 70)

    app.run(
        host="127.0.0.1",
        port=5005,
        debug=False
    )