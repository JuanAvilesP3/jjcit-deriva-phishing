"""
P8 - Deriva conceptual en deteccion de phishing por URL
03b_ablation_experiment.py

Prueba de ablacion pedida por la revision adversarial: is_https,
path_length, num_slashes y url_length dominan la importancia de
features en todos los bloques (Figura 4). Como las URLs legitimas
salen de dominios desnudos de Tranco (sin ruta) y las de phishing
son URLs completas, existe la posibilidad de que esas 4 variables
esten separando por "forma de la URL" (dominio vs URL con ruta) en
vez de por señal real de phishing. Esta prueba reentrena los 3
modelos en el diseño "fija" (bloque 1 -> bloques 2..6) SIN esas 4
columnas y compara el F1 resultante contra el original.

Si el F1 se mantiene cerca de 0.98+, la señal de phishing sobrevive
sin esas 4 variables y la preocupacion del revisor queda descartada.
Si el F1 cae sustancialmente, confirma que gran parte de la
separacion viene de esas 4 variables.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
SEED = 42

DROPPED = ["is_https", "path_length", "num_slashes", "url_length"]


def fit_eval(model_cls_params, X_train, y_train, X_test, y_test):
    model = model_cls_params()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    return f1_score(y_test, pred)


def main():
    df = pd.read_csv(PROC_DIR / "phishing_dataset.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df = df.sort_values("timestamp").reset_index(drop=True)

    feature_cols_full = [c for c in df.columns if c not in ("timestamp", "label")]
    feature_cols_ablated = [c for c in feature_cols_full if c not in DROPPED]
    y_all = df["label"]

    n_blocks = 6
    df["block"] = pd.qcut(df["timestamp"], q=n_blocks, labels=False)

    models = {
        "random_forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, n_jobs=-1),
        "xgboost": lambda: XGBClassifier(n_estimators=200, max_depth=6, random_state=SEED, eval_metric="logloss", verbosity=0),
        "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
    }

    rows = []
    for feature_set_name, feature_cols in [("full_32", feature_cols_full), ("ablated_28_no_url_shape", feature_cols_ablated)]:
        X_all = df[feature_cols].astype(float)
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(scaler.fit_transform(X_all), columns=feature_cols)

        for model_name, model_fn in models.items():
            train_idx = df.index[df.block == 0]
            X_train, y_train = X_scaled.loc[train_idx], y_all.loc[train_idx]
            for k in range(1, n_blocks):
                eval_idx = df.index[df.block == k]
                X_eval, y_eval = X_scaled.loc[eval_idx], y_all.loc[eval_idx]
                f1 = fit_eval(model_fn, X_train, y_train, X_eval, y_eval)
                rows.append(dict(feature_set=feature_set_name, model=model_name, distance=k, f1=f1,
                                  n_train=len(X_train), n_eval=len(X_eval)))
            print(f"[{feature_set_name}][{model_name}] listo")

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / "ablation_url_shape.csv", index=False)

    print("\n=== Resumen: F1 medio por conjunto de features y modelo (diseno fija, distancias 1-5) ===")
    print(out.groupby(["feature_set", "model"])["f1"].agg(["mean", "min", "max"]).round(4))
    print(f"\nCompletado: {len(out)} filas guardadas en {RESULTS_DIR / 'ablation_url_shape.csv'}")


if __name__ == "__main__":
    main()
