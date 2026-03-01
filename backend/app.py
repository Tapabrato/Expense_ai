from flask import Flask, render_template, request, redirect
import joblib
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)

# ==========================
# LOAD ML MODEL (UNCHANGED)
# ==========================
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")


# ==========================
# DATABASE INITIALIZATION
# ==========================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Expense Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    """)

    # Budget Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            monthly_budget REAL
        )
    """)

    conn.commit()
    conn.close()


# ==========================
# EXTRACT AMOUNT FROM TEXT
# ==========================
def extract_amount(text):
    match = re.search(r'\d+', text)
    return float(match.group()) if match else 0


# ==========================
# MONTHLY SUMMARY FUNCTION
# ==========================
def get_month_summary():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    current_month = datetime.now().strftime("%Y-%m")

    # Total spent this month
    cursor.execute("""
        SELECT SUM(amount) FROM expenses
        WHERE strftime('%Y-%m', date) = ?
    """, (current_month,))
    total_spent = cursor.fetchone()[0] or 0

    # Get budget
    cursor.execute("SELECT monthly_budget FROM budget WHERE id=1")
    budget_row = cursor.fetchone()
    budget = budget_row[0] if budget_row else 0

    remaining = budget - total_spent

    conn.close()

    return total_spent, budget, remaining


# ==========================
# HOME ROUTE (AI + BUDGET)
# ==========================
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None

    if request.method == "POST":
        user_text = request.form["text"]

        # ML Prediction (Categorizer System)
        vector = vectorizer.transform([user_text])
        prediction = model.predict(vector)[0]

        # Extract amount
        amount = extract_amount(user_text)
        today = datetime.now().strftime("%Y-%m-%d")

        # Store in database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses (text, amount, category, date)
            VALUES (?, ?, ?, ?)
        """, (user_text, amount, prediction, today))

        conn.commit()
        conn.close()

    # Always calculate monthly summary
    total_spent, budget, remaining = get_month_summary()

    return render_template("index.html",
                           prediction=prediction,
                           total_spent=total_spent,
                           budget=budget,
                           remaining=remaining)


# ==========================
# SET MONTHLY BUDGET ROUTE
# ==========================
@app.route("/set_budget", methods=["POST"])
def set_budget():
    budget = request.form["budget"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM budget")
    cursor.execute("INSERT INTO budget (id, monthly_budget) VALUES (1, ?)", (budget,))

    conn.commit()
    conn.close()

    return redirect("/")


# ==========================
# RUN APPLICATION
# ==========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)