import os
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect
import sqlite3

try:
    app = Flask(__name__)

    # DATABASE
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

    #  ROUTES 
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
        bg = request.args.get('bg')

        conn = sqlite3.connect('donors.db')
        cursor = conn.cursor()

        if bg:
            cursor.execute("SELECT * FROM donors WHERE blood_group = ?", (bg,))
        else:
            cursor.execute("SELECT * FROM donors")

        donor_list = cursor.fetchall()
        conn.close()

        return render_template('donors.html', donors=donor_list)
    
    @app.route('/dashboard')
    def dash():
        conn = sqlite3.connect('donors.db')
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

    # Avoid error when all counts are zero
        if sum(sizes) == 0:
            return render_template('dashboard.html',
                               total_donor=total_donor,
                               grp_cnt=grp_cnt,
                               chart_available=False)

    # Create chart
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import os

        chart_path = os.path.join("static", "piechart.png")

        plt.figure(figsize=(5,5))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Donors by Blood Group")
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

        conn = sqlite3.connect('donors.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM donors WHERE id = ?", (donor_id,))
        conn.commit()
        conn.close()

        return redirect('/donors')


    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Error: {e}")
