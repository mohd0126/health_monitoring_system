"""
ml_model.py
-----------
Trains a Decision Tree classifier on a synthetic dataset
representing water quality and health outbreak conditions
in rural Northeast India.

Features used:
  - ph         : water pH level
  - turbidity  : water turbidity (NTU)
  - temp       : water temperature (°C)
  - patients   : number of sick patients reported
  - fever      : fever reported (0/1)
  - diarrhea   : diarrhea reported (0/1)
  - vomiting   : vomiting reported (0/1)

Label:
  - 0 = SAFE
  - 1 = HIGH RISK
"""

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ─────────────────────────────────────────────
# Sample Training Dataset (50 rows)
# Simulating realistic rural NE India conditions
# ─────────────────────────────────────────────

TRAINING_DATA = [
    # ph,   turbidity, temp, patients, fever, diarrhea, vomiting, risk
    [7.2,   3.0,  26,  2,  0, 0, 0,  0],
    [7.0,   2.5,  24,  1,  0, 0, 0,  0],
    [6.8,   4.0,  27,  3,  0, 0, 0,  0],
    [7.5,   5.0,  25,  4,  1, 0, 0,  0],
    [7.1,   6.0,  28,  2,  0, 1, 0,  0],
    [6.5,   7.0,  30,  3,  0, 0, 1,  0],
    [7.3,   8.0,  29,  4,  1, 0, 0,  0],
    [6.9,   9.0,  31,  5,  1, 1, 0,  0],
    [7.6,   10.0, 32,  5,  0, 0, 0,  0],
    [7.0,   10.5, 27,  5,  1, 0, 1,  0],
    # Borderline cases
    [6.2,   11.0, 33,  6,  1, 1, 0,  1],
    [5.8,   12.0, 34,  7,  1, 1, 1,  1],
    [5.5,   14.0, 35,  8,  1, 1, 1,  1],
    [5.0,   16.0, 36,  9,  1, 1, 1,  1],
    [4.8,   18.0, 37,  12, 1, 1, 1,  1],
    [4.5,   20.0, 38,  15, 1, 1, 1,  1],
    [8.5,   13.0, 28,  7,  1, 0, 1,  1],
    [8.8,   15.0, 30,  10, 1, 1, 0,  1],
    [9.0,   17.0, 32,  8,  1, 1, 1,  1],
    [9.2,   22.0, 35,  14, 1, 1, 1,  1],
    # More SAFE cases
    [7.4,   1.5,  24,  1,  0, 0, 0,  0],
    [7.2,   2.0,  25,  2,  0, 0, 0,  0],
    [7.0,   3.5,  26,  1,  0, 0, 0,  0],
    [6.9,   4.5,  27,  3,  0, 0, 0,  0],
    [7.1,   5.5,  28,  4,  0, 0, 0,  0],
    [7.3,   6.5,  29,  2,  0, 0, 0,  0],
    [7.0,   7.5,  30,  3,  1, 0, 0,  0],
    [6.8,   8.5,  31,  4,  0, 1, 0,  0],
    [7.2,   9.5,  25,  5,  0, 0, 1,  0],
    [7.0,   10.0, 27,  4,  0, 0, 0,  0],
    # More HIGH RISK cases
    [6.0,   12.5, 33,  6,  1, 1, 1,  1],
    [5.7,   14.5, 34,  8,  1, 1, 1,  1],
    [5.3,   16.5, 35,  11, 1, 1, 1,  1],
    [4.9,   19.0, 36,  13, 1, 1, 1,  1],
    [9.1,   21.0, 37,  16, 1, 1, 1,  1],
    [8.9,   11.5, 33,  7,  1, 1, 0,  1],
    [8.6,   13.5, 31,  9,  1, 0, 1,  1],
    [6.1,   15.5, 34,  10, 1, 1, 1,  1],
    [5.9,   17.5, 36,  12, 1, 1, 1,  1],
    [5.6,   23.0, 38,  18, 1, 1, 1,  1],
    # Mixed edge cases
    [7.0,   11.5, 30,  4,  1, 0, 0,  0],
    [6.5,   10.5, 29,  6,  0, 1, 0,  1],
    [7.2,   12.0, 28,  3,  0, 0, 1,  0],
    [6.3,   13.0, 31,  7,  1, 1, 0,  1],
    [7.8,   9.0,  27,  5,  0, 0, 0,  0],
    [8.0,   14.0, 32,  6,  1, 0, 1,  1],
    [7.5,   8.0,  26,  5,  1, 1, 0,  0],
    [6.7,   11.0, 30,  8,  1, 1, 1,  1],
    [7.1,   7.0,  25,  3,  0, 0, 0,  0],
    [5.4,   18.5, 37,  14, 1, 1, 1,  1],
]

COLUMNS = ["ph", "turbidity", "temp", "patients", "fever", "diarrhea", "vomiting", "risk"]

# ─────────────────────────────────────────────
# Train the Decision Tree Model
# ─────────────────────────────────────────────

def _train_model():
    df = pd.DataFrame(TRAINING_DATA, columns=COLUMNS)

    X = df.drop("risk", axis=1)
    y = df["risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(f"[ML Model] Decision Tree trained. Accuracy: {accuracy * 100:.1f}%")

    return model


# Train once at import time
_MODEL = _train_model()


# ─────────────────────────────────────────────
# Public Predict Function
# ─────────────────────────────────────────────

def predict_risk_ml(ph, turbidity, temp, patients, fever, diarrhea, vomiting):
    """
    Use the trained Decision Tree to predict risk level.

    Returns:
        "HIGH RISK" or "SAFE"
    """
    features = pd.DataFrame(
        [[ph, turbidity, temp, patients, fever, diarrhea, vomiting]],
        columns=["ph", "turbidity", "temp", "patients", "fever", "diarrhea", "vomiting"]
    )

    prediction = _MODEL.predict(features)[0]
    return "HIGH RISK" if prediction == 1 else "SAFE"
