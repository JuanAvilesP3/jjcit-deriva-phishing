"""
P8 - Deriva conceptual en deteccion de phishing por URL
03e_revision_checks.py

Comprobaciones anadidas tras la revision cruzada interna (16/10/2026):

  1. Composicion de clases por bloque: el dataset esta balanceado en total,
     pero no dentro de cada bloque (PhishTank solo publica URLs que siguen
     en linea, asi que el phishing antiguo esta sub-representado). Se
     guarda el conteo por clase y bloque.
  2. Metricas que no dependen de la prevalencia en el diseno "fija":
     tasa de verdaderos positivos, tasa de falsos positivos, exactitud
     balanceada y F1 sobre bloques de evaluacion rebalanceados 50/50
     (submuestreo de la clase mayoritaria, 20 repeticiones).
  3. Inferencia con el bloque como unidad: Spearman entre distancia y la
     media de F1 de los tres modelos por bloque (n = 5).
  4. Sensibilidad con 12 bloques: misma tendencia con mas unidades.
  5. Control de la ablacion: quitar otras cuatro variables importantes que
     no dependen de como se construyo la clase legitima.
  6. Duplicados: la linea base aleatoria repetida tras quitar vectores de
     variables duplicados (evita que un mismo vector caiga en ambos lados).

El escalado se ajusta solo con los datos de entrenamiento de cada
particion. Salida: results/tables/revision_*.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
SEED = 42
URL_SHAPE = ["is_https", "path_length", "num_slashes", "url_length"]
# Variables que tambien dependen de que la URL legitima no tenga ruta: se excluyen del control.
PATH_DERIVED = ["path_num_segments", "has_double_slash_in_path"]

MODELS = {
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, n_jobs=-1),
    "xgboost": lambda: XGBClassifier(n_estimators=200, max_depth=6, random_state=SEED, eval_metric="logloss", verbosity=0),
    "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
}


def fit_predict(name, Xtr, ytr, Xte):
    sc = StandardScaler().fit(Xtr)
    m = MODELS[name]()
    m.fit(sc.transform(Xtr), ytr)
    return m.predict(sc.transform(Xte)), m


def rebalanced_f1(y, pred, rng, reps=20):
    y, pred = np.asarray(y), np.asarray(pred)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    k = min(len(pos), len(neg))
    out = []
    for _ in range(reps):
        idx = np.concatenate([rng.choice(pos, k, replace=False), rng.choice(neg, k, replace=False)])
        out.append(f1_score(y[idx], pred[idx]))
    return float(np.mean(out))


def fixed_design(df, cols, n_blocks):
    df = df.copy()
    df["block"] = pd.qcut(df["timestamp"], q=n_blocks, labels=False)
    rng = np.random.RandomState(SEED)
    rows = []
    tr = df[df.block == 0]
    for name in MODELS:
        _, model = fit_predict(name, tr[cols], tr.label, tr[cols].iloc[:1])
        sc = StandardScaler().fit(tr[cols])
        for k in range(1, n_blocks):
            ev = df[df.block == k]
            pred = model.predict(sc.transform(ev[cols]))
            tpr = recall_score(ev.label, pred)
            tnr = recall_score(ev.label, pred, pos_label=0)
            rows.append(dict(n_blocks=n_blocks, model=name, distance=k, pct_phishing=100 * ev.label.mean(),
                             f1=f1_score(ev.label, pred), f1_rebalanced=rebalanced_f1(ev.label, pred, rng),
                             tpr=tpr, fpr=1 - tnr, balanced_accuracy=(tpr + tnr) / 2))
    return pd.DataFrame(rows)


def main():
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 20)
    df = pd.read_csv(PROC_DIR / "phishing_dataset.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df = df.sort_values("timestamp").reset_index(drop=True)
    cols = [c for c in df.columns if c not in ("timestamp", "label")]

    # 1. Composicion por bloque
    b = df.assign(block=pd.qcut(df["timestamp"], q=6, labels=False))
    comp = b.groupby("block").agg(n=("label", "size"), phishing=("label", "sum"),
                                  start=("timestamp", "min"), end=("timestamp", "max")).reset_index()
    comp["legitimate"] = comp.n - comp.phishing
    comp["pct_phishing"] = (100 * comp.phishing / comp.n).round(1)
    comp.to_csv(RESULTS_DIR / "revision_block_composition.csv", index=False)
    print(comp)

    # 2-4. Metricas independientes de la prevalencia, con 6 y 12 bloques
    res = pd.concat([fixed_design(df, cols, 6), fixed_design(df, cols, 12)])
    res.to_csv(RESULTS_DIR / "revision_fixed_design_metrics.csv", index=False)
    summ = []
    for nb, g in res.groupby("n_blocks"):
        for metric in ["f1", "f1_rebalanced", "balanced_accuracy", "tpr", "fpr"]:
            means = g.groupby("distance")[metric].mean()
            rho, p = spearmanr(means.index, means.values)
            summ.append(dict(n_blocks=nb, metric=metric, rho_block_means=rho, p_two_sided=p, n_units=len(means),
                             first=means.iloc[0], last=means.iloc[-1]))
    summ = pd.DataFrame(summ)
    summ.to_csv(RESULTS_DIR / "revision_block_level_trend.csv", index=False)
    print(summ.round(4))

    # 5. Control de la ablacion
    tr = b[b.block == 0]
    imp_model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=SEED, n_jobs=-1).fit(tr[cols], tr.label)
    imp = pd.Series(imp_model.feature_importances_, index=cols).sort_values(ascending=False)
    control = [c for c in imp.index if c not in URL_SHAPE + PATH_DERIVED][:4]
    abl = []
    for label, drop in [("full", []), ("no_url_shape", URL_SHAPE), ("no_other_top4", control)]:
        keep = [c for c in cols if c not in drop]
        r = fixed_design(df, keep, 6)
        for name, g in r.groupby("model"):
            abl.append(dict(feature_set=label, dropped=";".join(drop), model=name, f1_mean=g.f1.mean(),
                            balanced_accuracy_mean=g.balanced_accuracy.mean()))
    abl = pd.DataFrame(abl)
    abl.to_csv(RESULTS_DIR / "revision_ablation_control.csv", index=False)
    imp.rename("importance").to_csv(RESULTS_DIR / "revision_rf_importance_block1.csv")
    print("control features:", control)
    print(abl.round(4))

    # 6. Duplicados en la linea base aleatoria
    dup = df.duplicated(subset=cols + ["label"])
    dd = df[~dup]
    rows = []
    for label, data in [("all_rows", df), ("dedup_feature_vectors", dd)]:
        Xtr, Xte, ytr, yte = train_test_split(data[cols], data.label, test_size=0.2, random_state=SEED, stratify=data.label)
        for name in MODELS:
            pred, _ = fit_predict(name, Xtr, ytr, Xte)
            rows.append(dict(data=label, n=len(data), model=name, f1_random_split=f1_score(yte, pred)))
    dups = pd.DataFrame(rows)
    dups.to_csv(RESULTS_DIR / "revision_dedup_random_split.csv", index=False)
    print(f"duplicated feature vectors: {int(dup.sum())} of {len(df)}")
    print(dups.round(4))


if __name__ == "__main__":
    main()
