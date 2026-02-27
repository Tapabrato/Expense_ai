from flask import Flask, request, jsonify, render_template
import joblib
import os

# ---------------------------------
# Initialize Flask App
# ---------------------------------
app = Flask(__name__)

# ---------------------------------
# Load Model & Vectorizer
# ---------------------------------
MODEL_PATH = "model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("model.pkl not found. Please run train.py first.")

if not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError("vectorizer.pkl not found. Please run train.py first.")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print("✅ Model and Vectorizer loaded successfully!")

# ---------------------------------
# Home Route (Frontend)
# ---------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------
# Prediction API
# ---------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        description = data.get("description")

        if not description:
            return jsonify({"error": "Description is required"}), 400

        # Transform input text
        vect = vectorizer.transform([description])

        # Predict category
        prediction = model.predict(vect)[0]

        # Get probability (confidence)
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(vect)[0]
            probability = max(probabilities) * 100
        else:
            probability = 100.0  # fallback if model doesn't support probability

        return jsonify({
            "category": prediction,
            "confidence": round(probability, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------
# Run Server
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)