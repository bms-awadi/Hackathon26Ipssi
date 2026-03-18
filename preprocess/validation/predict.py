import os

import joblib
import pandas as pd

from features import COLUMNS
from train import SCALER_PATH, BEST_MODEL_PATH


def predict(features):
    if not os.path.exists(BEST_MODEL_PATH) or not os.path.exists(SCALER_PATH):
        return 0

    scaler = joblib.load(SCALER_PATH)
    model = joblib.load(BEST_MODEL_PATH)

    df = pd.DataFrame([features], columns=COLUMNS)
    X_scaled = pd.DataFrame(scaler.transform(df), columns=COLUMNS)

    prediction = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0]

    if prediction == 0:
        return int(proba[0] * 40)
    return 0
