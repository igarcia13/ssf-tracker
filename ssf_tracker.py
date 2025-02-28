from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Database connection function
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Initialize PostgreSQL database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            ssf_name TEXT NOT NULL,
            student_name TEXT NOT NULL,
            activity TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Initialize DB
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ssf_name = request.form["ssf_name"].strip()
        student_name = request.form["student_name"].strip()
        activity = request.form["activity"].strip()
        date = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activities (ssf_name, student_name, activity, date) VALUES (%s, %s, %s, %s)",
                       (ssf_name, student_name, activity, date))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for("index"))
    
    return render_template("index.html")

@app.route("/summary", methods=["GET", "POST"])
def summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Default to current month if no selection is made
    selected_month = request.form.get("selected_month", datetime.now().strftime("%Y-%m"))
    ssf_name = request.form.get("ssf_name", "").strip()
    
    # Fetch activity summary for selected month and SSF
    cursor.execute("""
        SELECT activity, COUNT(*) as count 
        FROM activities 
        WHERE TO_CHAR(date, 'YYYY-MM') = %s AND ssf_name = %s
        GROUP BY activity
    """, (selected_month, ssf_name))
    activity_summary = cursor.fetchall()
    
    # Fetch detailed student activity list for selected month and SSF
    cursor.execute("""
        SELECT activity, STRING_AGG(student_name, ', ') as students 
        FROM activities 
        WHERE TO_CHAR(date, 'YYYY-MM') = %s AND ssf_name = %s
        GROUP BY activity
    """, (selected_month, ssf_name))
    student_details = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("summary.html", activity_summary=activity_summary, student_details=student_details, selected_month=selected_month, ssf_name=ssf_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


