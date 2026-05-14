import sqlite3
import os
import subprocess
import ipaddress
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


def autenticar_usuario(username, password):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    query = "SELECT 1 FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None


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
    output = process.stdout or process.stderr
    return f"<pre>{output}</pre>"


@app.route("/debug")
def debug():
    return "Endpoint de debug desabilitado.", 403


@app.route("/comente")
def comente():
    comentario = request.args.get("comentario", "")
    return f"<h1>Comentário recebido:</h1><p>{escape(comentario)}</p>"


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
