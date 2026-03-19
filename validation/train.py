import json
import os
import warnings

import joblib
import pandas as pd
from lazypredict.Supervised import LazyClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from features import extract_features, COLUMNS

warnings.filterwarnings("ignore")

LABELS_PATH = os.path.join("datasets", "output", "labels.json")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")
BEST_MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pkl")


def load_dataset():
    if not os.path.exists(LABELS_PATH):
        print(f"labels.json introuvable : {LABELS_PATH} — dataset vide")
        return [], []
    
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

    return X, y


def train():
    X, y = load_dataset()
    
    if not X:
        print("Dataset vide — entraînement ignoré")
        return

    print(f"Total factures PDF : {len(y)}")
    print(f"Legitimes          : {sum(y)}")
    print(f"Falsifiees         : {len(y) - sum(y)}")

    df = pd.DataFrame(X, columns=COLUMNS)

    X_train, X_test, y_train, y_test = train_test_split(
        df, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=COLUMNS)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=COLUMNS)

    joblib.dump(scaler, SCALER_PATH)

    clf = LazyClassifier(verbose=0, ignore_warnings=True, predictions=True)
    models, _ = clf.fit(X_train, X_test, y_train, y_test)

    print("\nClassement des modeles :")
    print(models[["Accuracy", "F1 Score", "Time Taken"]].to_string())

    best_name = models["F1 Score"].idxmax()
    best_score = models.loc[best_name, "F1 Score"]
    print(f"\nMeilleur modele : {best_name} (F1 = {best_score:.3f})")

    joblib.dump(clf.models[best_name], BEST_MODEL_PATH)
    print(f"Modele sauvegarde : {BEST_MODEL_PATH}")


if __name__ == "__main__":
    train()
