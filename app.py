import os
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, Response, flash
import sqlite3
import csv

app = Flask(__name__)
app.secret_key = "abc123"


# --- DATABASE CONNECTION FUNCTION ---
def get_db_connection():
    """Return a connection and ensure the donors table exists."""
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
    return conn


# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_donor', methods=['POST'])
def add_donor():
    name = request.form['name']
    age = request.form['age']
    blood_group = request.form['blood_group']
    phone = request.form['phone']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO donors (name, age, blood_group, phone) VALUES (?, ?, ?, ?)",
        (name, age, blood_group.lower(), phone)
    )
    conn.commit()
    conn.close()

    return redirect('/donors')


@app.route('/donors')
def donors():
    bg = request.args.get('bg')
    search = request.args.get('search')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM donors WHERE 1=1"
    params = []

    if bg:
        query += " AND lower(blood_group) = ?"
        params.append(bg.lower())

    if search:
        query += " AND lower(name) LIKE ?"
        params.append("%" + search.lower() + "%")

    cursor.execute(query, params)
    donor_list = cursor.fetchall()
    conn.close()

    return render_template('donors.html', donors=donor_list)


@app.route('/dashboard')
def dash():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM donors")
    total_donor = cursor.fetchone()[0]

    groups = ['a+', 'a-', 'b+', 'b-', 'o+', 'o-', 'ab+', 'ab-']
    grp_cnt = {}

    for g in groups:
        cursor.execute("SELECT COUNT(*) FROM donors WHERE lower(blood_group) = ?", (g,))
        grp_cnt[g] = cursor.fetchone()[0]

    conn.close()

    labels = groups
    sizes = [grp_cnt[g] for g in groups]

    if sum(sizes) == 0:
        return render_template('dashboard.html',
                               total_donor=total_donor,
                               grp_cnt=grp_cnt,
                               chart_available=False)

    chart_path = os.path.join("static", "piechart.png")
    plt.figure(figsize=(5,5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.savefig(chart_path)
    plt.close()

    return render_template('dashboard.html',
                           total_donor=total_donor,
                           grp_cnt=grp_cnt,
                           chart_available=True,
                           chart="piechart.png")


@app.route('/delete')
def delete():
    donor_id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM donors WHERE id = ?", (donor_id,))
    conn.commit()
    conn.close()
    return redirect('/donors')


@app.route('/update')
def update():
    donor_id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donors WHERE id = ?", (donor_id,))
    donor = cursor.fetchone()
    conn.close()
    return render_template('update_donor.html', donor=donor)


@app.route('/save_update/<int:donor_id>', methods=['POST'])
def save_update(donor_id):
    name = request.form['name']
    age = request.form['age']
    blood_group = request.form['blood_group']
    phone = request.form['phone']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE donors
        SET name = ?, age = ?, blood_group = ?, phone = ?
        WHERE id = ?
    """, (name, age, blood_group.lower(), phone, donor_id))
    conn.commit()
    conn.close()
    return redirect('/donors')


@app.route('/export_csv')
def export_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donors")
    data = cursor.fetchall()
    conn.close()

    csv_content = "ID,Name,Age,Blood Group,Phone\n"
    for row in data:
        phone_text = f'"{row[4]}"'  # ensure phone is text
        csv_content += f"{row[0]},{row[1]},{row[2]},{row[3]},{phone_text}\n"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=donors.csv"}
    )


if __name__ == '__main__':
    app.run(debug=True)
