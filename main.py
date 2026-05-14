import sqlite3
import os
import subprocess
from flask import Flask, request, make_response
app = Flask(__name__)
def autenticar_usuario(username, password):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result is not None


@app.route("/ping")
def ping():
    ip = request.args.get("ip", "")
    output = subprocess.getoutput(f"ping -c 1 {ip}")
    return f"<pre>{output}</pre>"


@app.route("/debug")
def debug():
    return f"SECRET_KEY={os.environ.get('SECRET_KEY')}"


@app.route("/comente")
def comente():
    comentario = request.args.get("comentario", "")
    return f"<h1>Comentário recebido:</h1><p>{comentario}</p>"


if __name__ == '__main__':
    app.run(debug=True)
