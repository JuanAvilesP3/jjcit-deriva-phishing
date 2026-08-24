"""
P8 - Deriva conceptual en deteccion de phishing por URL
03c_bootstrap_strategy_comparison.py

La revision adversarial señalo que el Wilcoxon pareado entre
ventana deslizante y acumulativa (Resultados) solo tiene 3-4 pares
por modelo, asi que su p minimo alcanzable en dos colas es
0.125-0.25: no tiene potencia para rechazar bajo ningun resultado
posible, sea cual sea el efecto real.

En vez de dejarlo como limitacion, esta prueba usa bootstrap sobre
las predicciones individuales (no solo el F1 agregado por bloque)
para comparar ventana vs acumulativa con muchos mas puntos de
datos: para cada bloque de evaluacion, remuestrea las instancias de
test con reemplazo, recalcula F1 de ambas estrategias sobre la
misma remuestra, y acumula la diferencia. Esto usa la variabilidad
real de las predicciones en vez de solo 5 valores de F1 por
estrategia.
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
N_BOOT = 2000


def main():
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(PROC_DIR / "phishing_dataset.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df = df.sort_values("timestamp").reset_index(drop=True)

    feature_cols = [c for c in df.columns if c not in ("timestamp", "label")]
    y_all = df["label"]
    X_all = df[feature_cols].astype(float)
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_all), columns=feature_cols)

    n_blocks = 6
    df["block"] = pd.qcut(df["timestamp"], q=n_blocks, labels=False)

    models = {
        "random_forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, n_jobs=-1),
        "xgboost": lambda: XGBClassifier(n_estimators=200, max_depth=6, random_state=SEED, eval_metric="logloss", verbosity=0),
        "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
    }

    summary_rows = []
    for model_name, model_fn in models.items():
        # Para cada bloque de evaluacion k+1 (k=0..4), entrenar ambas estrategias
        # y guardar las predicciones individuales sobre el MISMO conjunto de test,
        # para poder comparar por bootstrap pareado.
        diffs_pooled = []
        for k in range(0, n_blocks - 1):
            eval_idx = df.index[df.block == k + 1]
            X_eval, y_eval = X_scaled.loc[eval_idx].reset_index(drop=True), y_all.loc[eval_idx].reset_index(drop=True)

            # ventana: entrena solo en bloque k
            train_idx_w = df.index[df.block == k]
            model_w = model_fn()
            model_w.fit(X_scaled.loc[train_idx_w], y_all.loc[train_idx_w])
            pred_w = model_w.predict(X_eval)

            # acumulativa: entrena en bloques 0..k
            train_idx_c = df.index[df.block <= k]
            model_c = model_fn()
            model_c.fit(X_scaled.loc[train_idx_c], y_all.loc[train_idx_c])
            pred_c = model_c.predict(X_eval)

            n = len(y_eval)
            boot_diffs = np.empty(N_BOOT)
            for b in range(N_BOOT):
                idx = rng.integers(0, n, size=n)
                f1_w = f1_score(y_eval.values[idx], pred_w[idx])
                f1_c = f1_score(y_eval.values[idx], pred_c[idx])
                boot_diffs[b] = f1_c - f1_w
            diffs_pooled.append(boot_diffs)
            print(f"[{model_name}] block {k+1}: F1 window={f1_score(y_eval, pred_w):.4f} "
                  f"cumulative={f1_score(y_eval, pred_c):.4f} "
                  f"bootstrap mean diff={boot_diffs.mean():.4f}")

        # Combinar los 5 bloques: promedio de la diferencia bootstrap por replica
        pooled = np.mean(np.vstack(diffs_pooled), axis=0)
        mean_diff = pooled.mean()
        ci_lo, ci_hi = np.percentile(pooled, [2.5, 97.5])
        p_two_sided = 2 * min((pooled <= 0).mean(), (pooled >= 0).mean())
        summary_rows.append(dict(
            model=model_name, mean_diff_cumulative_minus_window=mean_diff,
            ci_lower=ci_lo, ci_upper=ci_hi, p_bootstrap=p_two_sided, n_boot=N_BOOT,
        ))

    out = pd.DataFrame(summary_rows)
    out.to_csv(RESULTS_DIR / "bootstrap_strategy_comparison.csv", index=False)
    print("\n=== Resumen: diferencia F1 (acumulativa - ventana), bootstrap sobre predicciones (2000 replicas x 5 bloques) ===")
    print(out.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
