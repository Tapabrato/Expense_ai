from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    description = data["description"]
    
    vect = vectorizer.transform([description])
    prediction = model.predict(vect)[0]
    
    return jsonify({"category": prediction})

if __name__ == "__main__":
    app.run(debug=True)