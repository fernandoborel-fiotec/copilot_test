import sqlite3
import os
import subprocess
import ipaddress
import logging
from flask import Flask, request, make_response
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DUMMY_PASSWORD_HASH = generate_password_hash("invalid-password-for-timing-mitigation")
PING_TIMEOUT_SECONDS = 5


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
        logging.warning("Hash de senha inválido para usuário informado.")
        return False
    return bool(row) and password_matches


@app.route("/ping")
def ping():
    ip = request.args.get("ip", "")
    try:
        validated_ip = str(ipaddress.ip_address(ip))
    except ValueError:
        response = make_response("<pre>Parâmetro 'ip' inválido.</pre>", 400)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    try:
        process = subprocess.run(
            ["ping", "-c", "1", validated_ip],
            capture_output=True,
            text=True,
            timeout=PING_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        response = make_response("<pre>Timeout ao executar ping.</pre>", 504)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    output = escape(process.stdout or process.stderr)
    response = make_response(f"<pre>{output}</pre>")
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


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
        raise RuntimeError("Use um servidor WSGI em produção (e.g., gunicorn).")
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
