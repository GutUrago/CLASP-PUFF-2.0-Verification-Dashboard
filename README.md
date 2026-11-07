# CLASP PUFF 2.0 – Verification dashboard

```
pip install -r requirements.txt
python -m streamlit run app.py
```

## Files

| File | What it does |
|---|---|
| `app.py` | Loads the data, sidebar filters, page navigation |
| `pages/1_Overview.py` | Progress against the roster's main households, outcomes, follow-up list |
| `pages/2_Indicator_Analysis.py` | Indicators from the PUFF 2.0 workbook, by breakdown |
| `utils/data_loader.py` | Fetches from SurveyCTO (falls back to the local xlsx), drops PII, cleans |
| `utils/fields.py` | The SurveyCTO fields the dashboard uses (all publishable and enabled) |
| `utils/roster.py` | Loads the sample roster, links it to submissions, household status |
| `utils/labels.py` | Value labels for the coded questions |
| `utils/charts.py` | Chart helpers |
| `utils/branding.py` | Laterite colours and styling |
| `data/puff2_verification_anonymized.xlsx` | Latest anonymised pull (fallback when SurveyCTO can't be reached) |
| `data/CLASP_PUFF_2.0_Sample_Roster.xlsx` | Sample roster for local use (the hosted app reads it from a SurveyCTO server dataset): household ID, company, county, sample type, assigned mode |

## Data

The dashboard only works with anonymised data.

**SurveyCTO.** Credentials go in your *user* secrets file, not in this shared
folder: `C:\Users\<you>\.streamlit\secrets.toml` (see `.streamlit/secrets.toml.example`).
No private key is used. Because the form is encrypted, the API returns only
the fields marked `publishable` in the form, so PII stays encrypted on the
server. The app then keeps only the fields listed in `utils/fields.py`;
everything else the API returns is dropped. Each field on that list was
checked against the latest form (`1_instruments`): publishable and not
disabled. The pull is treated as failed without `KEY, starttime, hh_id,
survey_status, response, survey_mode, p_company`. Any other field with no
answers yet shows "No data yet" instead of a chart.

**Fallback.** On start-up and on **Refresh data** the app pulls from
SurveyCTO. After each successful pull it saves the anonymised data to
`data/puff2_verification_anonymized.xlsx`. If a later pull fails (no
credentials, no internet, a required field not published), it shows that
file instead. The reason is printed in the terminal on a line starting with
`[data]`.

Any PII column that still arrives (names, phones, GPS, serial numbers,
enumerator details, free text) is dropped in `data_loader.py` before anything
is shown or saved.

**Refreshing.** While the dashboard is open it pulls the data again every 6
hours on its own (`REFRESH_HOURS` in `utils/data_loader.py`). The
**Refresh data** button pulls straight away. Filters and the open page are
kept when the data refreshes.

Only submissions received after 1 Nov 2026 are fetched (`FETCH_FROM` in
`utils/data_loader.py`). Asking for data from a date, rather than everything,
also avoids SurveyCTO's limit of one full download every 5 minutes.

## Sample roster

The hosted app is public on GitHub, so the roster is not in the repo. It is
uploaded to SurveyCTO as a server dataset and fetched with the same API user
(`roster_id` in the secrets, currently `clasp_puff_roster_r1`). Locally, if no dataset is set, the app
reads `data/CLASP_PUFF_2.0_Sample_Roster.xlsx`. Column names can be either the
xlsx headers (`HH_ID`, `Area 1`, ...) or dataset-style names (`hh_id`, `area_1`, ...).

## Progress rules

- A household is **completed** when any of its attempts has `interview_ok = 1`
  (purchase confirmed and the interview went ahead). The indicator page uses
  the same rule.
- Progress is measured against the **main** households on the roster.
  Replacement households are counted separately.
- A household that isn't completed takes the outcome of its latest attempt,
  grouped from `survey_status` (callback pending, not reached, refused, ...).
- A **mode mismatch** is an attempt made in a different mode from the one
  assigned on the roster. These households, pending callbacks, interviews that
  ended early and IDs not on the roster appear in the follow-up list.

## Things to update

- Sample: replace `data/CLASP_PUFF_2.0_Sample_Roster.xlsx` (same column names)
- Exchange rates: `to_usd()` in `pages/2_Indicator_Analysis.py`
- Value labels: `utils/labels.py` if the form choices change
