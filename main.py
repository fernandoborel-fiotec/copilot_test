import sqlite3
import os
import subprocess
import ipaddress
from flask import Flask, request, make_response
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DUMMY_PASSWORD_HASH = generate_password_hash("invalid-password-for-timing-mitigation")


def autenticar_usuario(username, password):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    query = "SELECT password FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    conn.close()
    stored_password_hash = row[0] if row else DUMMY_PASSWORD_HASH
    try:
        password_matches = check_password_hash(stored_password_hash, password)
    except ValueError:
        return False
    return bool(row) and password_matches


@app.route("/ping")
def ping():
    ip = request.args.get("ip", "")
    try:
        validated_ip = str(ipaddress.ip_address(ip))
    except ValueError:
        return "<pre>Parâmetro 'ip' inválido.</pre>", 400

    process = subprocess.run(
        ["ping", "-c", "1", validated_ip],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    output = escape(process.stdout or process.stderr)
    return f"<pre>{output}</pre>"


@app.route("/debug")
def debug():
    return "Endpoint de debug desabilitado.", 403


@app.route("/comente")
def comente():
    comentario = request.args.get("comentario", "")
    response = make_response(f"<h1>Comentário recebido:</h1><p>{escape(comentario)}</p>")
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


if __name__ == "__main__":
    if os.environ.get("APP_ENV", "").lower() == "production":
        raise RuntimeError("Use um servidor WSGI em produção (ex.: gunicorn).")
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
