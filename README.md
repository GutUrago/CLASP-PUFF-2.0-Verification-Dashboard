# CLASP PUFF 2.0 – Verification dashboard

```
pip install -r requirements.txt
python -m streamlit run app.py
```

## Files

| File | What it does |
|---|---|
| `app.py` | Loads the data, sidebar filters, page navigation |
| `pages/1_Overview.py` | Progress vs target, daily completions, call outcomes, regions |
| `pages/2_Indicator_Analysis.py` | Indicators from the PUFF 2.0 workbook, by breakdown |
| `utils/data_loader.py` | Fetches from SurveyCTO (falls back to the local xlsx), drops PII, cleans |
| `utils/labels.py` | Value labels for the coded questions |
| `utils/charts.py` | Chart helpers |
| `utils/branding.py` | Laterite colours and styling |
| `data/puff2_verification_anonymized.xlsx` | Synthetic test data (no real respondents) |

## Data

The dashboard only works with anonymised data. Any PII column that arrives
(names, phones, GPS, serial numbers, enumerator details, free text) is dropped
in `data_loader.py` before anything is shown.

On start-up, and each time you press **Refresh data**, the app:

1. fetches the submissions from SurveyCTO, using `.streamlit/secrets.toml`
   (copy `secrets.toml.example` and fill it in);
2. if there are no credentials or the request fails, falls back to
   `data/puff2_verification_anonymized.xlsx` and shows a warning in the sidebar.

Data is cached for 15 minutes between refreshes. The local file must be a
SurveyCTO wide export (same column names as the form).

## Things to update

- Sample targets: `TARGET` at the top of `pages/1_Overview.py`
- Exchange rates: `to_usd()` in `pages/2_Indicator_Analysis.py`
- Value labels: `utils/labels.py` if the form choices change
