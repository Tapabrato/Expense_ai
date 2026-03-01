from flask import Flask, request, jsonify, render_template
import joblib
import os

app = Flask(__name__)

# Load trained model and vectorizer
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Get description safely
        description = data.get("description", "")

        if description.strip() == "":
            return jsonify({
                "category": "No Input",
                "probability": 0
            })

        # Transform input text
        vector = vectorizer.transform([description])

        # Predict category
        prediction = model.predict(vector)[0]

        # Get probabilities
        probabilities = model.predict_proba(vector)[0]

        # Get confidence score
        confidence = round(max(probabilities) * 100, 2)

        return jsonify({
            "category": prediction,
            "probability": confidence
        })

    except Exception as e:
        return jsonify({
            "category": "Error",
            "probability": 0,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)