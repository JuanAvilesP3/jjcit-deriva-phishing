"""
P8 - Deriva conceptual en deteccion de phishing por URL
03d_size_matched_cumulative.py

Robustez (revision adversarial, seguimiento): la Limitaciones del
manuscrito senala que el reentrenamiento acumulativo (bloques 0..k) y
el de ventana deslizante (solo bloque k) difieren tanto en volumen de
datos de entrenamiento como en que tan antiguos son esos datos, y que
no se habia corrido un control que fije el volumen y solo deje variar
la antiguedad. Este script lo agrega: para cada k, entrena en una
submuestra aleatoria estratificada (misma proporcion de clases) de los
bloques 0..k, del MISMO tamanno que un solo bloque (para igualar el
volumen de la ventana deslizante), y evalua en el bloque k+1. Se repite
con varias semillas para promediar el ruido de la submuestra.
"""

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
N_REPEATS = 10


def fit_eval(model_cls_params, X_train, y_train, X_test, y_test):
    model = model_cls_params()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    return f1_score(y_test, pred)


def main(n_blocks=6):
    df = pd.read_csv(PROC_DIR / "phishing_dataset.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df = df.sort_values("timestamp").reset_index(drop=True)

    feature_cols = [c for c in df.columns if c not in ("timestamp", "label")]
    X_all = df[feature_cols].astype(float)
    y_all = df["label"]
    X_scaled = pd.DataFrame(StandardScaler().fit_transform(X_all), columns=feature_cols)
    df["block"] = pd.qcut(df["timestamp"], q=n_blocks, labels=False)

    models = {
        "random_forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, n_jobs=-1),
        "xgboost": lambda: XGBClassifier(n_estimators=200, max_depth=6, random_state=SEED, eval_metric="logloss", verbosity=0),
        "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
    }

    one_block_size = int((df.block == 0).sum())
    rows = []

    for model_name, model_fn in models.items():
        for k in range(0, n_blocks - 1):
            cum_idx = df.index[df.block <= k]
            eval_idx = df.index[df.block == k + 1]
            X_eval, y_eval = X_scaled.loc[eval_idx], y_all.loc[eval_idx]

            f1s = []
            for rep in range(N_REPEATS):
                rng_seed = SEED + rep
                if len(cum_idx) > one_block_size:
                    sub_idx, _ = train_test_split(
                        cum_idx, train_size=one_block_size, random_state=rng_seed,
                        stratify=y_all.loc[cum_idx],
                    )
                else:
                    sub_idx = cum_idx  # k=0: acumulativa ya es del tamanno de un bloque
                X_train, y_train = X_scaled.loc[sub_idx], y_all.loc[sub_idx]
                f1s.append(fit_eval(model_fn, X_train, y_train, X_eval, y_eval))

            rows.append(dict(
                model=model_name, distance=1, eval_block=k + 1,
                f1_mean=np.mean(f1s), f1_std=np.std(f1s), n_repeats=N_REPEATS,
                n_train_matched=min(len(cum_idx), one_block_size), n_train_full_cumulative=len(cum_idx),
            ))
            print(f"[{model_name}][k={k}] tamano-igualado F1={np.mean(f1s):.4f} (+/-{np.std(f1s):.4f})")

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / "acumulativa_tamano_igualado.csv", index=False)

    # --- Comparacion resumida por modelo, promediando sobre los 5 bloques ---
    strat = pd.read_csv(RESULTS_DIR / "degradation_long.csv")
    summary_rows = []
    for model_name in models:
        sliding_f1 = strat[(strat.model == model_name) & (strat.strategy == "ventana")]["f1"].mean()
        cumulative_f1 = strat[(strat.model == model_name) & (strat.strategy == "acumulativa")]["f1"].mean()
        matched_f1 = out[out.model == model_name]["f1_mean"].mean()
        summary_rows.append(dict(
            model=model_name, f1_ventana=sliding_f1, f1_acumulativa=cumulative_f1,
            f1_acumulativa_tamano_igualado=matched_f1,
        ))
    summary = pd.DataFrame(summary_rows)
    print("\n=== Resumen: ventana vs. acumulativa vs. acumulativa con tamano igualado ===")
    print(summary.to_string(index=False))
    summary.to_csv(RESULTS_DIR / "acumulativa_tamano_igualado_resumen.csv", index=False)


if __name__ == "__main__":
    main()
