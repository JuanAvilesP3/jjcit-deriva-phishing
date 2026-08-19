"""
P8 - Deriva conceptual en deteccion de phishing por URL
05_figures.py

Las 4 figuras que pide la ficha tecnica (seccion 6):
  Fig. 1 (la que sostiene el argumento): curva de F1 vs. distancia
         temporal al bloque de entrenamiento, con la particion
         aleatoria como referencia horizontal.
  Fig. 2: comparacion de las dos estrategias de mitigacion (ventana
         deslizante vs. acumulativa) a lo largo del tiempo.
  Fig. 3: desplazamiento de la distribucion de 4 caracteristicas clave
         entre el primer y el ultimo bloque (solo phishing, que es la
         clase que de verdad varia en el tiempo).
  Fig. 4: importancia de caracteristicas por bloque (Random Forest),
         mostrando como cambia lo que el modelo usa.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from figures_style import COLORS, apply_style, save_figure

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"
FIG_DIR = Path(__file__).resolve().parent.parent / "results" / "figures"
SEED = 42

KEY_FEATURES = ["url_length", "num_suspicious_keywords", "url_entropy", "has_ip_address"]
MODEL_COLORS = {"random_forest": COLORS["primary"], "xgboost": COLORS["secondary"], "logistic_regression": COLORS["neutral"]}
MODEL_LABELS = {"random_forest": "Random Forest", "xgboost": "XGBoost", "logistic_regression": "Regresión Logística"}


def fig1_curva_degradacion(df):
    fija = df[df.strategy == "fija"]
    aleatoria = df[df.strategy == "aleatoria"].set_index("model")["f1"]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    for model in fija["model"].unique():
        sub = fija[fija.model == model].sort_values("distance")
        ax.plot(sub["distance"], sub["f1"], marker="o", color=MODEL_COLORS[model], label=MODEL_LABELS[model])
        ax.axhline(aleatoria[model], color=MODEL_COLORS[model], linestyle="--", linewidth=1, alpha=0.6)

    ax.set_xlabel("Distancia temporal al bloque de entrenamiento (bloques)")
    ax.set_ylabel("F1")
    ax.set_title("Fig. 1 — Degradación de F1 con la distancia temporal\n(líneas punteadas = partición aleatoria, referencia)")
    ax.legend(fontsize=9)
    save_figure(fig, FIG_DIR / "fig1_curva_degradacion")
    plt.close(fig)


def fig2_estrategias(df):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, model in zip(axes, MODEL_LABELS):
        for strategy, color, marker in [("ventana", COLORS["secondary"], "s"), ("acumulativa", COLORS["primary"], "o")]:
            sub = df[(df.model == model) & (df.strategy == strategy)].copy()
            sub["eval_block"] = sub["eval_block"].astype(int)
            sub = sub.sort_values("eval_block")
            ax.plot(sub["eval_block"], sub["f1"], marker=marker, color=color, label=strategy)
        ax.set_title(MODEL_LABELS[model], fontsize=10)
        ax.set_xlabel("Bloque evaluado")
    axes[0].set_ylabel("F1")
    axes[0].legend(fontsize=9)
    fig.suptitle("Fig. 2 — Ventana deslizante vs. reentrenamiento acumulativo", fontsize=12)
    save_figure(fig, FIG_DIR / "fig2_comparacion_estrategias")
    plt.close(fig)


def fig3_desplazamiento_features(dataset):
    dataset = dataset.copy()
    dataset["timestamp"] = pd.to_datetime(dataset["timestamp"], utc=True, format="ISO8601")
    phishing = dataset[dataset.label == 1].sort_values("timestamp")
    n_blocks = 6
    phishing["block"] = pd.qcut(phishing["timestamp"], q=n_blocks, labels=False)
    first_block = phishing[phishing.block == 0]
    last_block = phishing[phishing.block == n_blocks - 1]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, feat in zip(axes.flat, KEY_FEATURES):
        ax.hist(first_block[feat], bins=30, alpha=0.55, color=COLORS["secondary"], density=True, label="Bloque 1 (más antiguo)")
        ax.hist(last_block[feat], bins=30, alpha=0.55, color=COLORS["primary"], density=True, label=f"Bloque {n_blocks} (más reciente)")
        ax.set_title(feat, fontsize=10)
        ax.set_ylabel("Densidad")

    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Fig. 3 — Desplazamiento de características clave (solo phishing)\nprimer vs. último bloque temporal", fontsize=12)
    save_figure(fig, FIG_DIR / "fig3_desplazamiento_features")
    plt.close(fig)


def fig4_importancia_por_bloque(dataset):
    dataset = dataset.copy()
    dataset["timestamp"] = pd.to_datetime(dataset["timestamp"], utc=True, format="ISO8601")
    dataset = dataset.sort_values("timestamp")
    n_blocks = 6
    dataset["block"] = pd.qcut(dataset["timestamp"], q=n_blocks, labels=False)

    feature_cols = [c for c in dataset.columns if c not in ("timestamp", "label", "block")]
    importances = pd.DataFrame(index=feature_cols)

    for b in range(n_blocks):
        sub = dataset[dataset.block == b]
        X = StandardScaler().fit_transform(sub[feature_cols].astype(float))
        y = sub["label"]
        model = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=SEED, n_jobs=-1)
        model.fit(X, y)
        importances[f"bloque {b + 1}"] = model.feature_importances_

    top_features = importances.mean(axis=1).nlargest(10).index
    top = importances.loc[top_features]

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.pcolormesh(top.values, cmap="Blues", edgecolors="white", linewidth=0.5)
    ax.set_yticks(np.arange(len(top_features)) + 0.5)
    ax.set_yticklabels(top_features, fontsize=8)
    ax.set_xticks(np.arange(n_blocks) + 0.5)
    ax.set_xticklabels(top.columns, fontsize=8)
    ax.invert_yaxis()
    ax.grid(False)  # el grid global cae en el centro de cada celda (ticks ahi para las etiquetas)
    fig.colorbar(im, ax=ax, label="Importancia (Random Forest)")
    ax.set_title("Fig. 4 — Importancia de características por bloque temporal")
    save_figure(fig, FIG_DIR / "fig4_importancia_por_bloque")
    plt.close(fig)


def main():
    apply_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    degradation = pd.read_csv(RESULTS_DIR / "degradation_long.csv")
    dataset = pd.read_csv(PROC_DIR / "phishing_dataset.csv")

    fig1_curva_degradacion(degradation)
    print("Fig. 1 lista")
    fig2_estrategias(degradation)
    print("Fig. 2 lista")
    fig3_desplazamiento_features(dataset)
    print("Fig. 3 lista")
    fig4_importancia_por_bloque(dataset)
    print("Fig. 4 lista")

    print(f"\nCompletado: 4 figuras guardadas en {FIG_DIR}")


if __name__ == "__main__":
    main()
