from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import joblib
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)

# -------------------------------
# DATABASE CONFIG
# -------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------------
# LOAD AI MODEL
# -------------------------------
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# -------------------------------
# DATABASE MODELS
# -------------------------------
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20))
    year = db.Column(db.Integer)
    total_budget = db.Column(db.Float)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))

# Create DB tables
with app.app_context():
    db.drop_all()      # Delete old data
    db.create_all()    # Create fresh tables

# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/")
def home():
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year

    budget = Budget.query.filter_by(month=current_month, year=current_year).first()
    expenses = Expense.query.filter(Expense.date.contains(current_month)).all()

    total_spent = sum(exp.amount for exp in expenses)

    remaining = 0
    total_budget = 0
    if budget:
        total_budget = budget.total_budget
        remaining = total_budget - total_spent

    # Category-wise summary
    category_summary = defaultdict(float)
    for exp in expenses:
        category_summary[exp.category] += exp.amount

    warning = False
    if budget and remaining < (0.2 * total_budget):
        warning = True

    return render_template("index.html",
                           total_budget=total_budget,
                           total_spent=total_spent,
                           remaining=remaining,
                           category_summary=category_summary,
                           warning=warning,
                           current_month=current_month,
                           current_year=current_year)

# -------------------------------
# SET BUDGET
# -------------------------------
@app.route("/set_budget", methods=["POST"])
def set_budget():
    month = datetime.now().strftime("%B")
    year = datetime.now().year
    amount = float(request.form["budget_amount"])

    existing = Budget.query.filter_by(month=month, year=year).first()

    if existing:
        existing.total_budget = amount
    else:
        new_budget = Budget(month=month, year=year, total_budget=amount)
        db.session.add(new_budget)

    db.session.commit()
    return redirect("/")

# -------------------------------
# ADD EXPENSE
# -------------------------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    description = request.form["description"]
    amount = float(request.form["amount"])

    # Predict category
    transformed = vectorizer.transform([description])
    predicted_category = model.predict(transformed)[0]

    date = datetime.now().strftime("%B %d, %Y")

    new_expense = Expense(
        description=description,
        amount=amount,
        category=predicted_category,
        date=date
    )

    db.session.add(new_expense)
    db.session.commit()

    return redirect("/")

# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)