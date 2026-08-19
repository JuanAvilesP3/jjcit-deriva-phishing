"""
P8 - Deriva conceptual en deteccion de phishing por URL
04_stats.py

  - Regresion OLS de F1 ~ distancia temporal (estrategia "fija"), por
    modelo y combinada.
  - Prueba de Page (L) para tendencia monotona decreciente de F1 con
    la distancia, usando los 3 modelos como "jueces". Nota: con solo 3
    jueces la aproximacion normal tiene poca potencia; se reporta con
    esa salvedad (ver ficha, seccion 4: "test de Page para tendencia
    monotona").
  - Comparacion de estrategias de mitigacion (ventana deslizante vs.
    reentrenamiento acumulativo) con prueba de Wilcoxon pareada por
    modelo.
  - Diferencia F1(aleatoria) - F1(temporal): "el numero que se cita
    del articulo" (ficha, seccion 5).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, wilcoxon

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "tables"


def page_l_test(matrix: np.ndarray):
    """matrix: filas=jueces (modelos), columnas=condiciones en el orden
    hipotetizado (distancia creciente). H1: los valores DECRECEN con la
    columna. Devuelve (L, Z, p_valor_unilateral)."""
    n_judges, k = matrix.shape
    ranks = np.array([pd.Series(row).rank().values for row in matrix])  # rank 1 = menor F1
    R_j = ranks.sum(axis=0)  # suma de rangos por condicion (columna)
    j = np.arange(1, k + 1)
    L = np.sum(j * R_j)

    E_L = n_judges * k * (k + 1) ** 2 / 4
    Var_L = n_judges * k**2 * (k + 1) * (k**2 - 1) / 144
    Z = (L - E_L) / np.sqrt(Var_L)
    # H1 = decreciente -> L sistematicamente MENOR que E[L] -> Z negativo
    p_one_sided = norm.cdf(Z)
    return L, Z, p_one_sided


def main():
    df = pd.read_csv(RESULTS_DIR / "degradation_long.csv")
    models = sorted(df["model"].unique())

    # --- Regresion sobre la curva de degradacion (estrategia "fija") ---
    fija = df[df.strategy == "fija"].copy()
    print("=== Regresión F1 ~ distancia (estrategia fija) ===")
    reg_rows = []
    for model in models + ["__combinado__"]:
        sub = fija if model == "__combinado__" else fija[fija.model == model]
        X = sm.add_constant(sub["distance"])
        fit = sm.OLS(sub["f1"], X).fit()
        slope, p_value = fit.params["distance"], fit.pvalues["distance"]
        reg_rows.append(dict(model=model, slope=slope, p_value=p_value, r2=fit.rsquared))
        print(f"{model:22s} pendiente={slope:+.5f}  p={p_value:.4f}  R²={fit.rsquared:.3f}")
    pd.DataFrame(reg_rows).to_csv(RESULTS_DIR / "regresion_degradacion.csv", index=False)

    # --- Prueba de Page: tendencia monotona decreciente ---
    pivot = fija.pivot(index="model", columns="distance", values="f1").loc[models]
    L, Z, p_one_sided = page_l_test(pivot.values)
    print(f"\n=== Prueba de Page (tendencia monótona decreciente) ===")
    print(f"L={L:.1f}  Z={Z:.3f}  p (unilateral, decreciente)={p_one_sided:.4f}")
    print("Nota: solo 3 jueces (modelos) -> la aproximación normal tiene poca potencia; interpretar con cautela.")
    pd.DataFrame([dict(L=L, Z=Z, p_one_sided=p_one_sided, n_judges=len(models), n_conditions=pivot.shape[1])]).to_csv(
        RESULTS_DIR / "page_test.csv", index=False
    )

    # --- Comparacion de estrategias: ventana vs acumulativa ---
    print("\n=== Comparación de estrategias (ventana vs. acumulativa) ===")
    comp_rows = []
    for model in models:
        v = df[(df.model == model) & (df.strategy == "ventana")].sort_values("eval_block")["f1"].values
        a = df[(df.model == model) & (df.strategy == "acumulativa")].sort_values("eval_block")["f1"].values
        n = min(len(v), len(a))
        if n >= 3:
            stat, p = wilcoxon(v[:n], a[:n])
        else:
            stat, p = np.nan, np.nan
        comp_rows.append(dict(model=model, f1_ventana_mean=v.mean(), f1_acumulativa_mean=a.mean(),
                               wilcoxon_stat=stat, p_value=p))
        print(f"{model:22s} ventana={v.mean():.4f}  acumulativa={a.mean():.4f}  p={p}")
    pd.DataFrame(comp_rows).to_csv(RESULTS_DIR / "comparacion_estrategias.csv", index=False)

    # --- El numero que se cita: F1(aleatoria) - F1(temporal) ---
    print("\n=== F1(aleatoria) - F1(temporal), el numero central del articulo ===")
    cite_rows = []
    for model in models:
        f1_random = df[(df.model == model) & (df.strategy == "aleatoria")]["f1"].iloc[0]
        f1_temporal_mean = fija[fija.model == model]["f1"].mean()
        f1_temporal_worst = fija[fija.model == model]["f1"].min()
        cite_rows.append(dict(
            model=model, f1_aleatoria=f1_random,
            f1_temporal_promedio=f1_temporal_mean, f1_temporal_peor=f1_temporal_worst,
            diferencia_promedio=f1_random - f1_temporal_mean,
            diferencia_peor_caso=f1_random - f1_temporal_worst,
        ))
        print(f"{model:22s} aleatoria={f1_random:.4f}  temporal(prom)={f1_temporal_mean:.4f}  "
              f"diferencia={f1_random - f1_temporal_mean:+.4f}")
    pd.DataFrame(cite_rows).to_csv(RESULTS_DIR / "diferencia_aleatoria_vs_temporal.csv", index=False)

    print(f"\nCompletado: tablas guardadas en {RESULTS_DIR}")


if __name__ == "__main__":
    main()
