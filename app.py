from flask import Flask, render_template, request
import pg8000
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

app = Flask(__name__)

def get_conn():
    return pg8000.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        ssl_context=True
    )

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_conn()
    cursor = conn.cursor()

    if request.method == "POST":
        producto = request.form.get("producto")
        precio = request.form.get("precio")

        try:
            cursor.execute(
                "UPDATE productos SET precio=%s WHERE nombre=%s",
                (precio, producto)
            )
            conn.commit()
        except Exception as e:
            print("Error al actualizar:", e)
            conn.rollback()

    cursor.execute("SELECT nombre, precio FROM productos")
    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", productos=productos)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # requerido por Render
    app.run(host="0.0.0.0", port=port)
