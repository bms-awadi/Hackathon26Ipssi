import json
import os

import joblib
import pandas as pd

from features import extract_features, COLUMNS
from train import LABELS_PATH, SCALER_PATH, BEST_MODEL_PATH


def evaluate():
    if not os.path.exists(BEST_MODEL_PATH) or not os.path.exists(SCALER_PATH):
        print("Modele introuvable. Lance d'abord train.py.")
        return

    with open(LABELS_PATH, encoding="utf-8") as f:
        labels = json.load(f)

    X, y = [], []
    for doc in labels.values():
        if doc.get("type") != "facture":
            continue
        if doc.get("format") != "pdf":
            continue
        X.append(extract_features(doc))
        y.append(1 if doc.get("legitime", True) else 0)

    scaler = joblib.load(SCALER_PATH)
    model = joblib.load(BEST_MODEL_PATH)

    df = pd.DataFrame(X, columns=COLUMNS)
    X_scaled = pd.DataFrame(scaler.transform(df), columns=COLUMNS)
    predictions = model.predict(X_scaled)

    TP = FP = TN = FN = 0
    for pred, true in zip(predictions, y):
        if true == 1 and pred == 1:
            TP += 1
        elif true == 0 and pred == 1:
            FP += 1
        elif true == 0 and pred == 0:
            TN += 1
        elif true == 1 and pred == 0:
            FN += 1

    total = len(y)
    correct = TP + TN
    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print(f"Total documents    : {total}")
    print(f"Precision globale  : {correct}/{total} ({round(correct/total*100, 1)}%)")
    print(f"Matrice            : TP={TP}  FP={FP}  TN={TN}  FN={FN}")
    print(f"Precision          : {precision:.3f}")
    print(f"Rappel             : {recall:.3f}")
    print(f"F1-score           : {f1:.3f}")


if __name__ == "__main__":
    evaluate()
