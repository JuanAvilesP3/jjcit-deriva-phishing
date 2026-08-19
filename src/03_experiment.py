"""
P8 - Deriva conceptual en deteccion de phishing por URL
03_experiment.py

Division temporal en n bloques de tamano igual (por numero de
muestras, segun cuantiles de fecha -- ficha tecnica, seccion 5).

Estrategias evaluadas, para cada uno de los 3 modelos:
  - aleatoria:   particion 80/20 aleatoria de todo el dataset (linea
                 base ciega al tiempo; el contraste con esto es "el
                 numero que se cita del articulo").
  - fija:        entrenar solo en el bloque 1, evaluar en cada bloque
                 2..n por separado (mide la degradacion pura).
  - ventana:     entrenar en el bloque k, evaluar en el bloque k+1
                 (reentrenamiento periodico con ventana deslizante).
  - acumulativa: entrenar en los bloques 1..k, evaluar en el bloque
                 k+1 (reentrenamiento que conserva el historial).

Salida: results/tables/degradation_long.csv con F1 por
(modelo, estrategia, bloque(s) de entrenamiento, bloque de evaluacion,
distancia temporal en bloques).
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
SEED = 42


def fit_eval(model_cls_params, X_train, y_train, X_test, y_test):
    model = model_cls_params()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    return f1_score(y_test, pred)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-blocks", type=int, default=6)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROC_DIR / "phishing_dataset.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df = df.sort_values("timestamp").reset_index(drop=True)

    feature_cols = [c for c in df.columns if c not in ("timestamp", "label")]
    X_all = df[feature_cols].astype(float)
    y_all = df["label"]

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_all), columns=feature_cols)

    # Bloques por cuantil de fecha (mismo numero de muestras por bloque)
    df["block"] = pd.qcut(df["timestamp"], q=args.n_blocks, labels=False)
    n_blocks = args.n_blocks

    models = {
        "random_forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, n_jobs=-1),
        "xgboost": lambda: XGBClassifier(n_estimators=200, max_depth=6, random_state=SEED, eval_metric="logloss", verbosity=0),
        "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
    }

    rows = []

    for model_name, model_fn in models.items():
        # --- Linea base aleatoria ---
        X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_all, test_size=0.2, random_state=SEED, stratify=y_all)
        f1 = fit_eval(model_fn, X_tr, y_tr, X_te, y_te)
        rows.append(dict(model=model_name, strategy="aleatoria", train_blocks="80%", eval_block="20% (aleatorio)", distance=np.nan, f1=f1, n_train=len(X_tr), n_eval=len(X_te)))
        print(f"[{model_name}][aleatoria] F1={f1:.4f}")

        # --- Fija: entrenar solo en bloque 0 ---
        train_idx = df.index[df.block == 0]
        X_train, y_train = X_scaled.loc[train_idx], y_all.loc[train_idx]
        for k in range(1, n_blocks):
            eval_idx = df.index[df.block == k]
            X_eval, y_eval = X_scaled.loc[eval_idx], y_all.loc[eval_idx]
            f1 = fit_eval(model_fn, X_train, y_train, X_eval, y_eval)
            rows.append(dict(model=model_name, strategy="fija", train_blocks="0", eval_block=str(k), distance=k, f1=f1, n_train=len(X_train), n_eval=len(X_eval)))
        print(f"[{model_name}][fija] listo")

        # --- Ventana deslizante: entrenar en bloque k, evaluar en k+1 ---
        for k in range(0, n_blocks - 1):
            train_idx = df.index[df.block == k]
            eval_idx = df.index[df.block == k + 1]
            X_train, y_train = X_scaled.loc[train_idx], y_all.loc[train_idx]
            X_eval, y_eval = X_scaled.loc[eval_idx], y_all.loc[eval_idx]
            f1 = fit_eval(model_fn, X_train, y_train, X_eval, y_eval)
            rows.append(dict(model=model_name, strategy="ventana", train_blocks=str(k), eval_block=str(k + 1), distance=1, f1=f1, n_train=len(X_train), n_eval=len(X_eval)))
        print(f"[{model_name}][ventana] listo")

        # --- Acumulativa: entrenar en bloques 0..k, evaluar en k+1 ---
        for k in range(0, n_blocks - 1):
            train_idx = df.index[df.block <= k]
            eval_idx = df.index[df.block == k + 1]
            X_train, y_train = X_scaled.loc[train_idx], y_all.loc[train_idx]
            X_eval, y_eval = X_scaled.loc[eval_idx], y_all.loc[eval_idx]
            f1 = fit_eval(model_fn, X_train, y_train, X_eval, y_eval)
            rows.append(dict(model=model_name, strategy="acumulativa", train_blocks=f"0-{k}", eval_block=str(k + 1), distance=1, f1=f1, n_train=len(X_train), n_eval=len(X_eval)))
        print(f"[{model_name}][acumulativa] listo")

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / "degradation_long.csv", index=False)
    print(f"\nCompletado: {len(out)} filas guardadas en {RESULTS_DIR / 'degradation_long.csv'}")


if __name__ == "__main__":
    main()
