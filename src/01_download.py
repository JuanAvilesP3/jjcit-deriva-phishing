"""
P8 - Deriva conceptual en deteccion de phishing por URL
01_download.py

Descarga y consolida:
  - PhishTank (data.phishtank.com/data/online-valid.csv): URLs de
    phishing con marca temporal (submission_time). Es la UNICA fuente
    de phishing usada en este diseno -- ver decision documentada abajo.
  - Tranco (tranco-list.eu): ranking de dominios legitimos, como
    instantanea unica con fecha registrada.

Decision de diseno (ficha tecnica, seccion 3: "La marca temporal es
indispensable. Verificarla antes de nada"):
  - OpenPhish (feed comunitario) se descarto: es una lista de URLs
    activas en el momento de la consulta, SIN marca temporal por
    registro -- no sirve para medir degradacion a lo largo del tiempo.
  - UCI Phishing Websites y PhiUSIIL se descartaron por el mismo
    motivo: son extracciones de caracteristicas en un punto fijo del
    tiempo, sin fecha por fila.
  - PhishTank SI trae 'submission_time' por URL y no requiere cuenta
    para el feed publico (verificado 19/08/2026). Cubre suficiente
    volumen: ~29,300 URLs en los ultimos 180 dias, con densidad
    creciente y sin huecos grandes.
  - Las URLs legitimas (Tranco) se usan como una unica instantanea
    estable -- el diseno de "deriva" es sobre el phishing, no sobre
    los dominios legitimos, que cambian mucho mas lento.
"""

import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PHISHTANK_URL = "https://data.phishtank.com/data/online-valid.csv"
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

WINDOW_DAYS = 180  # ver 01b: fuera de esta ventana la densidad es demasiado baja


def download_phishtank():
    print("Descargando PhishTank...")
    resp = requests.get(PHISHTANK_URL, timeout=60)
    resp.raise_for_status()
    raw_path = RAW_DIR / "phishtank_online_valid.csv"
    raw_path.write_bytes(resp.content)

    df = pd.read_csv(raw_path)
    assert "submission_time" in df.columns, "PhishTank sin submission_time: el diseno no es viable con esta fuente"
    df["submission_time"] = pd.to_datetime(df["submission_time"])

    cutoff = df["submission_time"].max() - pd.Timedelta(days=WINDOW_DAYS)
    recent = df[df["submission_time"] >= cutoff].copy()
    recent = recent[["phish_id", "url", "submission_time", "verified", "online", "target"]]
    recent.to_csv(RAW_DIR / "phishing_urls.csv", index=False)

    print(f"PhishTank: {len(df)} filas totales, {len(recent)} en los últimos {WINDOW_DAYS} días")
    print(f"Rango usado: {recent['submission_time'].min()} a {recent['submission_time'].max()}")
    return recent


def download_tranco():
    print("Descargando Tranco...")
    resp = requests.get(TRANCO_URL, timeout=60)
    resp.raise_for_status()
    zip_path = RAW_DIR / "tranco_top1m.zip"
    zip_path.write_bytes(resp.content)

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(RAW_DIR / "tranco")

    csv_files = list((RAW_DIR / "tranco").glob("*.csv"))
    df = pd.read_csv(csv_files[0], names=["rank", "domain"])
    df["legitimate_url"] = "http://" + df["domain"]
    df["snapshot_date"] = datetime.now(timezone.utc).date().isoformat()
    df.to_csv(RAW_DIR / "legitimate_urls.csv", index=False)

    print(f"Tranco: {len(df)} dominios, instantánea del {df['snapshot_date'].iloc[0]}")
    return df


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    phishing = download_phishtank()
    legit = download_tranco()
    print(f"\nCompletado: {len(phishing)} URLs de phishing + {len(legit)} URLs legítimas en {RAW_DIR}")


if __name__ == "__main__":
    main()
