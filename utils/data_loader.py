"""
Load the verification data and prepare it for the dashboard.

Data comes from the SurveyCTO API when it can be reached. If there are no
credentials or the request fails, the anonymised xlsx in data/ is used instead.

No private key is sent. The form is encrypted, so the API only returns the
fields marked "publishable"; PII stays encrypted on the server. On top of
that, only the fields listed in utils/fields.py are kept, so nothing else
(enumerator names, serial numbers, ...) is shown or saved.

After every successful pull the kept fields are saved to data/, so the
fallback file always holds the latest real data.
"""
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st

from utils import labels as L
from utils.fields import ALL_FIELDS, REQUIRED, SELECT_MULTIPLE, TEXT

DATA_FILE = Path(__file__).parent.parent / "data" / "puff2_verification_anonymized.xlsx"

DK = [-97, -98, -99]  # not applicable / refused / don't know

# Only fetch submissions received after this date. A date other than 0 also
# avoids SurveyCTO's limit of one full download (date=0) every 5 minutes.
FETCH_FROM = datetime(2026, 11, 8, tzinfo=timezone.utc)

# How often the data is pulled again on its own (hours). An open dashboard
# refreshes itself on this schedule; the Refresh button pulls immediately.
REFRESH_HOURS = 6


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def has_api_credentials():
    try:
        return "surveycto" in st.secrets
    except Exception:  # no secrets.toml at all
        return False


def fetch_surveycto():
    """Wide JSON export of the submissions received since FETCH_FROM."""
    cfg = st.secrets["surveycto"]
    since = int(FETCH_FROM.timestamp())  # SurveyCTO expects seconds since 1970
    url = f"https://{cfg['server']}.surveycto.com/api/v2/forms/data/wide/json/{cfg['form_id']}?date={since}"
    r = requests.get(url, auth=(cfg["username"], cfg["password"]), timeout=60)
    if r.status_code == 417:
        raise ValueError("SurveyCTO rate limit reached, wait a few minutes and refresh again")
    if r.status_code == 401:
        raise ValueError("wrong username or password, or the user has no API access")
    if r.status_code == 404:
        raise ValueError(f"form '{cfg['form_id']}' not found on {cfg['server']}")
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        raise ValueError(f"no submissions returned ({str(data)[:200]})")

    raw = pd.DataFrame(data)
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError(f"fields not published in the form: {', '.join(missing)}")
    return keep_fields(raw)


def option_columns(columns, field):
    """The 0/1 columns SurveyCTO sends for a select_multiple field:
    PCRS_0_1, PCRS_0_2, ... and PCRS_0__96 for the code -96."""
    return [c for c in columns if re.fullmatch(rf"{re.escape(field)}_(_?\d+)", c)]


def keep_fields(raw):
    """Keep only the fields in utils/fields.py, plus the 0/1 option columns
    of the select_multiple fields."""
    keep = [c for c in ALL_FIELDS if c in raw.columns]
    for field in SELECT_MULTIPLE:
        keep += option_columns(raw.columns, field)
    return raw[keep].copy()


@st.cache_data(ttl=REFRESH_HOURS * 3600, show_spinner="Loading data...")
def load_data():
    """Try SurveyCTO first, fall back to the xlsx in data/.

    Returns (data, source, warning). The result is cached for REFRESH_HOURS;
    the Refresh button in the sidebar clears the cache and calls this again.
    """
    if not has_api_credentials():
        warning = "No SurveyCTO credentials in secrets.toml."
    else:
        try:
            raw = fetch_surveycto()
            save_snapshot(raw)
            return clean(raw), f"SurveyCTO: {len(raw)} submissions ({datetime.now():%d %b %H:%M})", None
        except Exception as e:
            warning = f"SurveyCTO fetch failed ({type(e).__name__}: {e})."

    if DATA_FILE.exists():
        raw = keep_fields(pd.read_excel(DATA_FILE, dtype=str))
        return clean(raw), f"data/{DATA_FILE.name}", warning + " Showing the local file."
    return None, None, warning + f" No local file found at data/{DATA_FILE.name}."


def save_snapshot(raw):
    """Keep the latest pull (kept fields only) as the fallback file."""
    try:
        raw.to_excel(DATA_FILE, index=False)
    except Exception as e:  # e.g. the file is open in Excel
        print(f"[data] Could not save snapshot: {e}")


# --------------------------------------------------------------------------- #
# Cleaning
# --------------------------------------------------------------------------- #
def clean(raw):
    df = raw.replace("", np.nan)  # the API sends blanks as empty strings

    # a field with no answers yet (or dropped from the form) becomes an empty
    # column, so its chart shows "No data yet" instead of failing
    for col in ALL_FIELDS:
        if col not in df:
            df[col] = np.nan

    for col in ["starttime", "endtime", "SubmissionDate"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")

    for col in ALL_FIELDS:
        if col not in TEXT + SELECT_MULTIPLE + ["starttime", "endtime", "SubmissionDate"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # select_multiple. The API sends one column per option (PCRS_0_1,
    # PCRS_0_2, ...) with 1 when it was ticked and blank otherwise. Anyone
    # with at least one tick answered the question, so their blanks become 0;
    # everyone else stays blank (not asked). The field itself is rebuilt as
    # "1 4" from the ticks, so the charts know who answered.
    # (A file that has the field as "1 4 -96" instead gets the 0/1 columns.)
    new_cols = {}
    for field in SELECT_MULTIPLE:
        options = option_columns(df.columns, field)
        if options:
            ticks = df[options].apply(pd.to_numeric, errors="coerce")
            codes = [c[len(field) + 1:].replace("_", "-") for c in options]
            answered = ticks.notna().any(axis=1)
            picked = ticks.eq(1).apply(lambda row: " ".join(c for c, t in zip(codes, row) if t), axis=1)
            new_cols[field] = picked.where(answered)
            new_cols.update({c: ticks[c].eq(1).astype(float).where(answered) for c in options})
        elif df[field].notna().any():
            answered = df[field].notna()
            choices = df[field].fillna("").astype(str).str.replace(r"\.0\b", "", regex=True).str.split()
            for code in sorted({c for row in choices[answered] for c in row}):
                name = f"{field}_{code.replace('-', '_')}"
                new_cols[name] = choices.apply(lambda x, code=code: float(code in x)).where(answered)
    df = df.drop(columns=[c for c in new_cols if c in df.columns])
    df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

    # appliance_received, appliance_in_use and serial_verified were added to
    # the form over time, so older submissions don't have them. Fill the gaps
    # row by row with the same formulas as the form.
    interviewed = df["interview_ok"] == 1
    received = (df["D1a"] != 7).astype(float).where(interviewed)
    df["appliance_received"] = df["appliance_received"].fillna(received)
    in_use = ((df["appliance_received"] == 1) & (df["D1"] == 1) & (df["D2"] != 2)).astype(float)
    df["appliance_in_use"] = df["appliance_in_use"].fillna(in_use.where(interviewed))
    serial = df["serial_match"].where(df["serial_access"] == 1, -97).where(df["serial_access"].notna())
    df["serial_verified"] = df["serial_verified"].fillna(serial)

    # readable columns used by filters and charts
    df["date"] = df["starttime"].dt.normalize()
    df["country"] = df["p_country_code"].map(L.COUNTRY)
    df["appliance"] = df["appliance_code"].map(L.APPLIANCE)
    df["mode"] = df["survey_mode"].map(L.MODE)
    df["gender"] = df["C1"].map(L.GENDER)
    df["age_group"] = pd.cut(df["C3"].where(df["C3"] > 0), [0, 24, 34, 44, 54, 120],
                             labels=["<25", "25-34", "35-44", "45-54", "55+"]).astype(object)

    # outcome of each attempt: survey_status and its label (calculated in the form)
    df["status"] = df["survey_status_lbl"].fillna("Code " + df["survey_status"].astype("Int64").astype(str))
    # completed = purchase confirmed and the interview went ahead (interview_ok = 1)
    df["completed"] = df["interview_ok"] == 1
    df["reached"] = df["response"].isin([1, 2, 5, 6])
    df["verified"] = (df["B1"] == 1) | (df["B1a"] == 0)
    df["duration_min"] = df["duration_total"] / 60
    return df


def valid(s):
    """Drop refused / don't know / not applicable codes."""
    return s.where(~s.isin(DK))
