# Concept drift in URL-based phishing detection

Data and code for the article *Concept Drift in URL-Based Phishing Detection: A Temporal Evaluation*, submitted to the *Journal of Universal Computer Science* (J.UCS).

**Authors:** Juan Pablo Aviles-Esparza, Italo Javier Tenempaguay-Granizo, Isaac David Torres-Paredes. Software Engineering, Faculty of Informatics and Electronics, Escuela Superior Politécnica de Chimborazo (ESPOCH), Riobamba, Ecuador.

## What the study does

Three lexical-feature classifiers (random forest, XGBoost, logistic regression) are trained on 180 days of PhishTank reports plus an equal number of Tranco domains and evaluated under four designs: a random split, a fixed training block tested on later blocks, a sliding retraining window, and cumulative retraining. Additional analyses test the trend with the evaluation block as the unit, use prevalence-independent metrics, and run a feature ablation with a control feature set.

## Repository layout

| Path | Content |
|---|---|
| `src/01_download.py` | Download the PhishTank feed and the Tranco list |
| `src/02_preprocess.py` | Build the dataset and extract 32 lexical features per URL |
| `src/03_experiment.py` | The four evaluation designs |
| `src/03b_ablation_experiment.py` | Ablation of the URL-shape features |
| `src/03c_bootstrap_strategy_comparison.py` | Paired bootstrap, sliding window vs. cumulative retraining |
| `src/03d_size_matched_cumulative.py` | Size-matched control for cumulative retraining |
| `src/03e_revision_checks.py` | Block composition, block-level trend, prevalence-independent metrics, ablation control, duplicates |
| `src/04_stats.py` | Regression, ANCOVA and Page test |
| `src/05_figures.py` | Figures 1-4 |
| `src/06_export_shared_data.py` | Writes the published data files in `data/shared/` |
| `src/run_all.py` | Runs the pipeline in order and logs package versions to `results/logs/` |
| `data/shared/phishtank_ids.csv` | PhishTank identifier, submission time and target of each phishing URL |
| `data/shared/legitimate_sample.csv` | Sampled Tranco domains with their synthetic timestamps |
| `data/shared/phishing_dataset.csv` | Feature table, label and timestamp used by every experiment |
| `results/tables/`, `results/figures/` | Every table and figure reported in the article |
| `paper/` | LaTeX source and compiled manuscript |

## Reproducing the analysis

```bash
pip install -r requirements.txt
mkdir -p data/processed
cp data/shared/phishing_dataset.csv data/processed/
python src/run_all.py --from 03   # every experiment, from the published feature table
```

`python src/run_all.py` without `--from` starts again from a new download.

The phishing URLs themselves are not redistributed, since they are malicious links; they can be retrieved from PhishTank by identifier. PhishTank's downloadable feed lists only phishing that is still online, so a new download will not reproduce the same sample; the published feature table does.

## Citation

Archived on Zenodo: [10.5281/zenodo.22907771](https://doi.org/10.5281/zenodo.22907771) (this DOI always resolves to the latest version).
