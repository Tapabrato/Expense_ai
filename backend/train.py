import pandas as pd
import joblib
import time

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

print("Loading dataset...")

# Load dataset
df = pd.read_csv("dataset.csv")

X = df["description"]
y = df["category"]

print(f"Total records: {len(df)}")

# Convert text into numerical form
print("Vectorizing text...")
vectorizer = TfidfVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, y, test_size=0.2, random_state=42
)

print("Training model...")

model = LogisticRegression(max_iter=200)

# Simulated training progress
for i in range(1, 6):
    print(f"Training progress: {i*20}%")
    time.sleep(0.3)

# Train model
model.fit(X_train, y_train)

print("Model training completed!")

# Evaluate model
y_pred = model.predict(X_test)

train_accuracy = model.score(X_train, y_train)
test_accuracy = accuracy_score(y_test, y_pred)

print("\n📊 MODEL PERFORMANCE")
print(f"Training Accuracy: {train_accuracy * 100:.2f}%")
print(f"Testing Accuracy: {test_accuracy * 100:.2f}%")

# Cross Validation Score
cv_scores = cross_val_score(model, X_vectorized, y, cv=5)
print(f"Cross Validation Accuracy: {cv_scores.mean() * 100:.2f}%")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("\nModel and vectorizer saved successfully!")