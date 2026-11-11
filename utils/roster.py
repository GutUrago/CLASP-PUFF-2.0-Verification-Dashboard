"""
Sample roster and household progress.

The roster lists every household in the sample with its company, county,
sample type (main / replacement) and the mode it was assigned. Progress is
measured against the main households.

Where the roster comes from:
  1. a SurveyCTO server dataset, when secrets.toml has
     roster_id under [surveycto] (used for the hosted app, so the
     roster never has to sit in the public GitHub repo)
  2. otherwise data/CLASP_PUFF_2.0_Sample_Roster.xlsx on this computer

A household counts as completed when any of its attempts has interview_ok = 1
(purchase confirmed). Otherwise it takes the outcome of its latest attempt.
"""
import io
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from utils.data_loader import REFRESH_HOURS

ROSTER_FILE = Path(__file__).parent.parent / "data" / "CLASP_PUFF_2.0_Sample_Roster.xlsx"

# survey_status codes (calculated in the form) grouped for the progress charts
STATUS_GROUPS = {
    11: "Completed", 14: "Completed", 15: "Completed",
    12: "Purchase not confirmed", 13: "Purchase not confirmed",
    21: "Callback pending", 22: "Callback pending", 23: "Callback pending",
    31: "Not reached", 32: "Not reached", 33: "Not reached", 34: "Not reached",
    35: "Not reached", 36: "Not reached",   # phone switched off, wrong number
    41: "Refused", 42: "Refused", 43: "Refused",
    51: "Ended early",
}
GROUP_ORDER = ["Completed", "Purchase not confirmed", "Callback pending", "Ended early",
               "Not reached", "Refused", "Other", "Not attempted"]


def fetch_roster_dataset():
    """Download the roster from a SurveyCTO server dataset (CSV)."""
    cfg = st.secrets["surveycto"]
    url = f"https://{cfg['server']}.surveycto.com/api/v2/datasets/data/csv/{cfg['roster_id']}"
    r = requests.get(url, auth=(cfg["username"], cfg["password"]), timeout=60)
    if r.status_code == 401:
        raise ValueError("the API user cannot read the roster dataset")
    if r.status_code == 404:
        raise ValueError(f"dataset '{cfg['roster_id']}' not found")
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text), dtype=str)


def roster_dataset_configured():
    try:
        return "roster_id" in st.secrets["surveycto"]
    except Exception:
        return False


@st.cache_data(ttl=REFRESH_HOURS * 3600, show_spinner=False)
def load_roster():
    """SurveyCTO dataset first, then the local xlsx. None if neither works."""
    r = None
    if roster_dataset_configured():
        try:
            r = fetch_roster_dataset()
        except Exception as e:
            print(f"[roster] SurveyCTO dataset failed ({e}), trying the local file")
    if r is None and ROSTER_FILE.exists():
        r = pd.read_excel(ROSTER_FILE, dtype=str)
    if r is None:
        return None

    # Same columns whether they come from the xlsx ("Area 1") or a dataset
    # (where names can't have spaces, e.g. "area_1"): compare them in lower
    # case with spaces and dashes as underscores.
    r.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in r.columns]
    return pd.DataFrame({
        "hh_id": r["hh_id"].str.strip(),
        "company": r["company"],
        "county": r["county"],
        "area": r["area_1"],
        "sample": r["type"].str.strip().str.capitalize(),            # Main / Replacement
        "assigned_mode": r["mode"].str.strip().str.lower().map({"phone": "Phone",
                                                                "in-person": "In-person"}),
    })


def attach_roster(df, roster):
    """Add roster details to every submission. Attempts whose hh_id is not on
    the roster keep their preloaded company/county and are flagged."""
    out = df.merge(roster, on="hh_id", how="left", suffixes=("", "_roster")).copy()
    out["on_roster"] = out["hh_id"].isin(roster["hh_id"])
    out["company"] = out["company"].fillna(out["p_company"])
    out["county"] = out["county"].fillna(out["p_county"])
    out["sample"] = out["sample"].fillna("Not on roster")
    out["status_group"] = out["survey_status"].map(STATUS_GROUPS).fillna("Other")
    out.loc[out["completed"], "status_group"] = "Completed"
    out["mode_mismatch"] = out["assigned_mode"].notna() & out["mode"].notna() & \
        (out["assigned_mode"] != out["mode"])
    return out


def household_status(roster, attempts):
    """One row per roster household: attempts, outcome and flags."""
    a = attempts[attempts["on_roster"]].sort_values("starttime")
    per_hh = a.groupby("hh_id").agg(
        attempts=("KEY", "size"),
        last_attempt=("starttime", "max"),
        completed=("completed", "any"),
        mode_mismatch=("mode_mismatch", "any"),
        latest_status=("status", "last"),
        latest_group=("status_group", "last"),
    )
    completed_on = a[a["completed"]].groupby("hh_id")["date"].min().rename("completed_on")
    hh = roster.set_index("hh_id").join(per_hh).join(completed_on).reset_index()

    hh["attempts"] = hh["attempts"].fillna(0).astype(int)
    hh["completed"] = hh["completed"].fillna(False).astype(bool)
    hh["mode_mismatch"] = hh["mode_mismatch"].fillna(False).astype(bool)
    hh["outcome"] = hh["latest_group"].fillna("Not attempted")
    hh.loc[hh["completed"], "outcome"] = "Completed"
    return hh
