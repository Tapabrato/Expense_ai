from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ==============================
# DATABASE MODELS
# ==============================

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

# ==============================
# CATEGORY DETECTION FUNCTION
# ==============================

def detect_category(description):
    description = description.lower()

    food_keywords = ["food", "pizza", "burger", "restaurant", "dinner", "lunch", "groceries","coffee","zomato","swiggy"]
    travel_keywords = ["travel", "bus", "train", "uber", "ola", "flight", "cab"]
    entertainment_keywords = ["movie", "netflix", "game", "concert", "subscription"]
    shopping_keywords = ["shop", "clothes", "amazon", "flipkart", "mall","myntra","ajio","lifestyle"]

    if any(word in description for word in food_keywords):
        return "Food"

    elif any(word in description for word in travel_keywords):
        return "Travel"

    elif any(word in description for word in entertainment_keywords):
        return "Entertainment"

    elif any(word in description for word in shopping_keywords):
        return "Shopping"

    else:
        return "Other"

# ==============================
# ROUTES
# ==============================

# 🔹 Start Page
@app.route('/')
def start():
    return render_template('start.html')


# 🔹 Dashboard Page
@app.route('/dashboard')
def dashboard():
    budgets = Budget.query.all()
    expenses = Expense.query.all()

    total_budget = sum(b.amount for b in budgets)
    total_spent = sum(e.amount for e in expenses)
    remaining = total_budget - total_spent

    # Category Summary for Chart
    category_summary = {}
    for expense in expenses:
        if expense.category in category_summary:
            category_summary[expense.category] += expense.amount
        else:
            category_summary[expense.category] = expense.amount

    warning = remaining <= (0.2 * total_budget) if total_budget > 0 else False

    return render_template(
        'index.html',
        total_budget=total_budget,
        total_spent=total_spent,
        remaining=remaining,
        category_summary=category_summary,
        warning=warning
    )


# 🔹 Set Budget
@app.route('/set_budget', methods=['POST'])
def set_budget():
    amount = float(request.form['budget_amount'])
    new_budget = Budget(amount=amount)
    db.session.add(new_budget)
    db.session.commit()
    return redirect('/dashboard')


# 🔹 Add Expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])

    category = detect_category(description)

    new_expense = Expense(
        description=description,
        amount=amount,
        category=category
    )

    db.session.add(new_expense)
    db.session.commit()

    return redirect('/dashboard')


# ==============================
# CREATE DATABASE
# ==============================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)