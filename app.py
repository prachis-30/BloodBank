from flask import Flask, render_template, request, redirect
import sqlite3

try:
    app = Flask(__name__)

    # ---------- DATABASE SETUP ----------
    def init_db():
        conn = sqlite3.connect('donors.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                blood_group TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    init_db()

    # ---------- ROUTES ----------
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/add_donor', methods=['POST'])
    def add_donor():
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        phone = request.form['phone']

        conn = sqlite3.connect('donors.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO donors (name, age, blood_group, phone) VALUES (?, ?, ?, ?)",
            (name, age, blood_group, phone)
        )
        conn.commit()
        conn.close()

        return redirect('/donors')

    @app.route('/donors')
    def donors():
        conn = sqlite3.connect('donors.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donors")
        donor_list = cursor.fetchall()
        conn.close()

        return render_template('donors.html', donors=donor_list)
    
    @app.route('/dashboard')
    def dash():
        return render_template('dashboard.html')

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Error: {e}")
