"""
P8 - Deriva conceptual en deteccion de phishing por URL
02_preprocess.py

Extraccion de ~30 caracteristicas lexicas por URL (ficha tecnica,
seccion 4): longitud, numero de subdominios, presencia de IP, entropia
de caracteres, uso de acortadores, palabras clave sospechosas, TLD,
guiones, digitos.

Las URLs legitimas (Tranco, instantanea unica) se muestrean para
tener un volumen comparable al de phishing -- sesgo documentado: el
ranking de Tranco favorece dominios muy establecidos, asi que se
muestrea en todo el rango de rank (no solo el top), para variedad.
"""

import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
SEED = 42

SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "adf.ly", "shorte.st", "cutt.ly", "rebrand.ly", "tiny.cc", "rb.gy",
}
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "confirm", "signin",
    "bank", "paypal", "ebay", "webscr", "password", "billing", "suspend",
    "urgent", "alert", "unlock", "recover",
]


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def extract_features(url: str) -> dict:
    try:
        parsed = urlparse(url if "://" in url else f"http://{url}")
    except Exception:
        parsed = urlparse("http://invalid")

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    full = url

    labels = hostname.split(".") if hostname else []
    is_ip = bool(re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", hostname))

    return {
        "url_length": len(full),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "num_dots": full.count("."),
        "num_hyphens": full.count("-"),
        "num_underscores": full.count("_"),
        "num_slashes": full.count("/"),
        "num_question_marks": full.count("?"),
        "num_equals": full.count("="),
        "num_at": full.count("@"),
        "num_ampersands": full.count("&"),
        "num_percent": full.count("%"),
        "num_digits": sum(c.isdigit() for c in full),
        "digit_ratio": (sum(c.isdigit() for c in full) / len(full)) if full else 0.0,
        "num_subdomains": max(len(labels) - 2, 0),
        "has_ip_address": int(is_ip),
        "has_port": int(parsed.port is not None),
        "is_https": int(parsed.scheme == "https"),
        "url_entropy": shannon_entropy(full),
        "hostname_entropy": shannon_entropy(hostname),
        "is_shortened": int(hostname in SHORTENERS),
        "num_suspicious_keywords": sum(kw in full.lower() for kw in SUSPICIOUS_KEYWORDS),
        "has_suspicious_keyword": int(any(kw in full.lower() for kw in SUSPICIOUS_KEYWORDS)),
        "domain_length": len(labels[-2]) if len(labels) >= 2 else len(hostname),
        "path_num_segments": len([s for s in path.split("/") if s]),
        "has_double_slash_in_path": int("//" in path),
        "num_www": int(hostname.startswith("www.")),
        "longest_label_length": max((len(l) for l in labels), default=0),
        "tld_length": len(labels[-1]) if labels else 0,
        "has_at_symbol": int("@" in full),
        "num_dashes_in_hostname": hostname.count("-"),
        "vowel_ratio_hostname": (sum(c in "aeiou" for c in hostname.lower()) / len(hostname)) if hostname else 0.0,
    }


def sample_legitimate(n: int, time_min, time_max) -> pd.DataFrame:
    """Las URLs legitimas vienen de una unica instantanea de Tranco (no
    tienen fecha real por URL). Para que cada bloque temporal del
    experimento tenga ambas clases, se les asigna una marca de tiempo
    sintetica, uniforme sobre el mismo rango que cubre el phishing.
    Decision documentada explicitamente (limitaciones del manuscrito):
    asume que la reputacion de un dominio legitimo no cambia dentro de
    la ventana de estudio (180 dias), a diferencia del phishing, que es
    justamente lo que el articulo mide que SI cambia."""
    df = pd.read_csv(RAW_DIR / "legitimate_urls.csv")
    rng = np.random.RandomState(SEED)
    idx = rng.choice(len(df), size=min(n, len(df)), replace=False)
    sample = df.iloc[idx].copy()
    sample = sample.rename(columns={"legitimate_url": "url"})
    sample["label"] = 0

    time_min_ts, time_max_ts = pd.Timestamp(time_min).value, pd.Timestamp(time_max).value
    random_ts = rng.randint(time_min_ts, time_max_ts, size=len(sample), dtype=np.int64)
    sample["timestamp"] = pd.to_datetime(random_ts, utc=True)
    return sample[["url", "label", "timestamp"]]


def main():
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    phishing = pd.read_csv(RAW_DIR / "phishing_urls.csv")
    phishing = phishing.rename(columns={"submission_time": "timestamp"})
    phishing["label"] = 1
    phishing = phishing[["url", "label", "timestamp"]]
    phishing["timestamp"] = pd.to_datetime(phishing["timestamp"], utc=True)

    legit = sample_legitimate(n=len(phishing), time_min=phishing["timestamp"].min(), time_max=phishing["timestamp"].max())

    combined = pd.concat([phishing, legit], ignore_index=True)
    combined["timestamp"] = pd.to_datetime(combined["timestamp"], utc=True)

    print(f"Extrayendo características de {len(combined)} URLs...")
    features = combined["url"].apply(extract_features).apply(pd.Series)
    out = pd.concat([combined[["timestamp", "label"]], features], axis=1)
    out = out.sort_values("timestamp").reset_index(drop=True)

    out.to_csv(PROC_DIR / "phishing_dataset.csv", index=False)
    print(f"{out.shape[0]} filas, {features.shape[1]} características. Guardado en {PROC_DIR / 'phishing_dataset.csv'}")
    print(f"Balance: {out['label'].value_counts().to_dict()}")
    print(f"Rango temporal: {out['timestamp'].min()} a {out['timestamp'].max()}")


if __name__ == "__main__":
    main()
