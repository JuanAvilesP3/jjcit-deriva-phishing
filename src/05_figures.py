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
PAPER_FIG_DIR = Path(__file__).resolve().parent.parent / "paper" / "figures"
PAPER_FIG_DIR.mkdir(parents=True, exist_ok=True)
SEED = 42

KEY_FEATURES = ["url_length", "num_suspicious_keywords", "url_entropy", "has_ip_address"]
MODEL_COLORS = {"random_forest": COLORS["primary"], "xgboost": COLORS["secondary"], "logistic_regression": COLORS["neutral"]}
MODEL_LABELS = {"random_forest": "Random Forest", "xgboost": "XGBoost", "logistic_regression": "Logistic Regression"}


def fig1_curva_degradacion(df):
    # Revision cruzada (16/10): marcadores y trazos distintos por modelo para lectura en B/N,
    # lineas base rotuladas y eje Y acotado declarado en el pie.
    fija = df[df.strategy == "fija"]
    aleatoria = df[df.strategy == "aleatoria"].set_index("model")["f1"]
    styles = {"random_forest": ("o", "-"), "xgboost": ("s", "--"), "logistic_regression": ("^", ":")}

    fig, ax = plt.subplots(figsize=(7.5, 5))
    for model in fija["model"].unique():
        sub = fija[fija.model == model].sort_values("distance")
        marker, ls = styles[model]
        ax.plot(sub["distance"], sub["f1"], marker=marker, linestyle=ls, color=MODEL_COLORS[model], label=MODEL_LABELS[model])
        ax.axhline(aleatoria[model], color=MODEL_COLORS[model], linestyle=ls, linewidth=0.8, alpha=0.5)
    ax.plot([], [], color="grey", linewidth=0.8, alpha=0.6, label="Random-split baseline\n(thin line, same style as its model)")
    ax.set_xlim(0.8, 5.2)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Temporal distance to training block (blocks)")
    ax.set_ylabel("F1 Score (truncated axis)")
    ax.legend(fontsize=9, loc="lower left")
    save_figure(fig, FIG_DIR / "fig1_curva_degradacion")
    save_figure(fig, PAPER_FIG_DIR / "fig1_curva_degradacion")
    plt.close(fig)


def fig2_estrategias(df):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, model in zip(axes, MODEL_LABELS):
        for strategy, color, marker, strat_label in [("ventana", COLORS["secondary"], "s", "Sliding window"), ("acumulativa", COLORS["primary"], "o", "Cumulative retraining")]:
            sub = df[(df.model == model) & (df.strategy == strategy)].copy()
            # eval_block va de 1 a 5 con indice 0; en el articulo los bloques se numeran 1..6
            sub["eval_block"] = sub["eval_block"].astype(int) + 1
            sub = sub.sort_values("eval_block")
            ax.plot(sub["eval_block"], sub["f1"], marker=marker, color=color, label=strat_label)
        ax.set_title(MODEL_LABELS[model], fontsize=9.5)
        ax.set_xlabel("Evaluated block")
        ax.set_xticks([2, 3, 4, 5, 6])
    axes[0].set_ylabel("F1 Score")
    axes[0].legend(fontsize=8.5)
    save_figure(fig, FIG_DIR / "fig2_comparacion_estrategias")
    save_figure(fig, PAPER_FIG_DIR / "fig2_comparacion_estrategias")
    plt.close(fig)


def fig3_desplazamiento_features(dataset):
    # Revision cruzada (16/10): mismos bloques que el experimento (cuantiles de fecha sobre todo el
    # dataset), la clase legitima como referencia, barras de proporcion para las variables binarias
    # o de conteo pequeno, y url_length recortada al percentil 99.
    dataset = dataset.copy()
    dataset["timestamp"] = pd.to_datetime(dataset["timestamp"], utc=True, format="ISO8601")
    n_blocks = 6
    dataset["block"] = pd.qcut(dataset["timestamp"], q=n_blocks, labels=False)
    groups = [("Phishing, block 1", (dataset.label == 1) & (dataset.block == 0), COLORS["secondary"], "///"),
              (f"Phishing, block {n_blocks}", (dataset.label == 1) & (dataset.block == n_blocks - 1), COLORS["primary"], ""),
              ("Legitimate, all blocks", dataset.label == 0, COLORS["neutral"], "...")]

    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    for ax, feat in zip(axes.flat, KEY_FEATURES):
        if feat in ("url_length", "url_entropy"):
            hi = dataset[feat].quantile(0.99)
            bins = np.linspace(dataset[feat].min(), hi, 31)
            for label, mask, color, _ in groups:
                ax.hist(dataset.loc[mask, feat].clip(upper=hi), bins=bins, histtype="step", linewidth=1.4,
                        density=True, color=color, label=label)
            ax.set_ylabel("Density")
            if feat == "url_length":
                ax.set_xlabel("characters (clipped at 99th percentile)", fontsize=8)
        else:
            values = sorted(dataset[feat].clip(upper=3).unique())
            width = 0.27
            for i, (label, mask, color, hatch) in enumerate(groups):
                share = dataset.loc[mask, feat].clip(upper=3).value_counts(normalize=True).reindex(values, fill_value=0)
                ax.bar(np.arange(len(values)) + (i - 1) * width, share.values, width=width, color=color, alpha=0.75,
                       hatch=hatch, edgecolor="black", linewidth=0.4, label=label)
            ax.set_xticks(np.arange(len(values)))
            ax.set_xticklabels([str(int(v)) if v < 3 else "3+" for v in values])
            ax.set_ylabel("Proportion of URLs")
        ax.set_title(feat, fontsize=9.5)

    axes[0, 0].legend(fontsize=7.5)
    fig.subplots_adjust(hspace=0.38)
    save_figure(fig, FIG_DIR / "fig3_desplazamiento_features")
    save_figure(fig, PAPER_FIG_DIR / "fig3_desplazamiento_features")
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
        importances[f"Block {b + 1}"] = model.feature_importances_

    top_features = importances.mean(axis=1).nlargest(10).index
    top = importances.loc[top_features]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    im = ax.pcolormesh(top.values, cmap="Blues", edgecolors="white", linewidth=0.5)
    ax.set_yticks(np.arange(len(top_features)) + 0.5)
    ax.set_yticklabels(top_features, fontsize=8)
    ax.set_xticks(np.arange(n_blocks) + 0.5)
    ax.set_xticklabels(top.columns, fontsize=8)
    ax.invert_yaxis()
    ax.grid(False)
    
    for i in range(len(top_features)):
        for j in range(n_blocks):
            val = top.values[i, j]
            color = "white" if val > top.values.max() / 2 else "black"
            ax.text(j + 0.5, i + 0.5, f"{val:.3f}", ha="center", va="center", color=color, fontsize=7)

    fig.colorbar(im, ax=ax, label="Feature Importance (Random Forest)")
    save_figure(fig, FIG_DIR / "fig4_importancia_por_bloque")
    save_figure(fig, PAPER_FIG_DIR / "fig4_importancia_por_bloque")
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
