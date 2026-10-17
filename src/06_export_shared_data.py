"""
P8 - Deriva conceptual en deteccion de phishing por URL
06_export_shared_data.py

Escribe en data/shared/ los datos que se publican con el articulo:
  - phishtank_ids.csv: identificador de PhishTank, fecha de envio y objetivo
    declarado de cada URL de phishing usada (sin la URL, que sigue siendo un
    enlace malicioso; se recupera en phishtank.org con el identificador);
  - legitimate_sample.csv: los dominios de Tranco muestreados, su puesto en el
    ranking y la marca de tiempo sintetica asignada (misma semilla que
    02_preprocess.py);
  - phishing_dataset.csv: la tabla de variables lexicas, etiqueta y fecha que
    usan todos los experimentos.
"""
from pathlib import Path
import shutil

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "shared"
SEED = 42


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not (RAW / "phishing_urls.csv").exists() or not (RAW / "legitimate_urls.csv").exists():
        print("Sin descarga original en data/raw/: se conservan los archivos publicados de data/shared/.")
        return
    ph = pd.read_csv(RAW / "phishing_urls.csv")
    ph[["phish_id", "submission_time", "verified", "online", "target"]].to_csv(OUT / "phishtank_ids.csv", index=False)

    # Misma muestra que sample_legitimate() en 02_preprocess.py
    ts = pd.to_datetime(ph["submission_time"], utc=True)
    legit = pd.read_csv(RAW / "legitimate_urls.csv")
    rng = np.random.RandomState(SEED)
    idx = rng.choice(len(legit), size=min(len(ph), len(legit)), replace=False)
    sample = legit.iloc[idx][["rank", "domain", "legitimate_url", "snapshot_date"]].copy()
    lo, hi = ts.min().value, ts.max().value
    sample["synthetic_timestamp"] = pd.to_datetime(rng.randint(lo, hi, size=len(sample), dtype=np.int64), utc=True)
    sample.to_csv(OUT / "legitimate_sample.csv", index=False)

    shutil.copy2(ROOT / "data" / "processed" / "phishing_dataset.csv", OUT / "phishing_dataset.csv")
    print(f"{len(ph)} identificadores de phishing, {len(sample)} dominios legitimos -> {OUT}")


if __name__ == "__main__":
    main()
