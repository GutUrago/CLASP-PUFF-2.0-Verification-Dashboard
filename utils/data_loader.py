"""
Load the verification data and prepare it for the dashboard.

Data comes from the SurveyCTO API when it can be reached. If there are no
credentials or the request fails, the anonymised xlsx in data/ is used instead.

Whatever the source, PII columns are dropped straight after loading.
"""
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st

from utils import labels as L

DATA_FILE = Path(__file__).parent.parent / "data" / "puff2_verification_anonymized.xlsx"

# Dropped if they are present, so identifying data never reaches the app.
PII_COLUMNS = [
    "p_customer_name", "p_phone", "p_phone_2", "p_alt_name", "p_alt_phone", "p_alt_relation",
    "p_lat", "p_lon", "p_map_url", "p_serial", "p_area_2", "p_area_3", "p_gender", "p_age",
    "p_hhsize", "contact_name", "B4c", "B10", "serial_no", "serial_img", "appliance_img",
    "gps-Latitude", "gps-Longitude", "gps-Altitude", "gps-Accuracy", "comments", "text_audit",
    "enum", "enum_oth", "enum_name", "supervisor", "supervisor_oth", "supervisor_name",
    "username", "deviceid", "devicephonenum",
]

SELECT_MULTIPLE = ["E1a", "E1b", "F1a", "F1b", "E3", "J6", "PCRS_0", "PCRS_1b", "L2"]
DK = [-97, -98, -99]  # not applicable / refused / don't know


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def has_api_credentials():
    try:
        return "surveycto" in st.secrets
    except Exception:  # no secrets.toml at all
        return False


def fetch_surveycto():
    """Wide JSON export from the SurveyCTO API. The form is encrypted, so the
    private key must be sent along, otherwise the answers come back empty."""
    cfg = st.secrets["surveycto"]
    url = f"https://{cfg['server']}.surveycto.com/api/v2/forms/data/wide/json/{cfg['form_id']}?date=0"
    auth = (cfg["username"], cfg["password"])
    with open(cfg["private_key_path"], "rb") as key:
        r = requests.post(url, auth=auth, files={"private_key": key}, timeout=60)
    r.raise_for_status()
    return pd.DataFrame(r.json())


@st.cache_data(ttl=900, show_spinner="Loading data...")
def load_data():
    """Try SurveyCTO first, fall back to the xlsx in data/.

    Returns (data, source, warning). The result is cached for 15 minutes;
    the Refresh button in the sidebar clears the cache and calls this again.
    """
    if not has_api_credentials():
        warning = "No SurveyCTO credentials in .streamlit/secrets.toml."
    else:
        try:
            raw = fetch_surveycto()
            return clean(raw), f"SurveyCTO API (fetched {datetime.now():%d %b %H:%M})", None
        except Exception as e:
            warning = f"SurveyCTO fetch failed ({type(e).__name__}: {e})."

    if DATA_FILE.exists():
        return clean(pd.read_excel(DATA_FILE)), f"data/{DATA_FILE.name}", warning + " Showing the local file."
    return None, None, warning + f" No local file found at data/{DATA_FILE.name}."


# --------------------------------------------------------------------------- #
# Cleaning
# --------------------------------------------------------------------------- #
def clean(raw):
    df = raw.drop(columns=[c for c in PII_COLUMNS if c in raw.columns]).copy()

    for col in ["starttime", "endtime", "SubmissionDate"]:
        if col in df:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")

    # everything that looks numeric becomes numeric (codes, amounts, durations)
    text_cols = SELECT_MULTIPLE + ["KEY", "external_id", "p_company", "p_country_iso",
                                   "p_area_1", "p_technology", "p_currency", "p_purchase_date",
                                   "formdef_version", "review_status"]
    for col in df.columns:
        if col not in text_cols and df[col].dtype == object:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() >= 0.8 * df[col].notna().sum():
                df[col] = converted

    # select_multiple: "1 4 -96" -> one 0/1 column per option (E1a_1, E1a_4, E1a__96)
    for col in SELECT_MULTIPLE:
        if col not in df:
            continue
        answered = df[col].notna()
        choices = df[col].fillna("").astype(str).str.split()
        codes = sorted({c for row in choices for c in row})
        for code in codes:
            name = f"{col}_{code.replace('-', '_')}"
            df[name] = choices.apply(lambda x: float(code in x)).where(answered)

    # readable columns used by filters and charts
    df["date"] = df["starttime"].dt.normalize()
    df["country"] = df["p_country_code"].map(L.COUNTRY)
    df["appliance"] = df["appliance_code"].map(L.APPLIANCE)
    df["mode"] = df["survey_mode"].map(L.MODE)
    df["region"] = df["p_area_1"]
    df["distributor"] = df["p_company"]
    df["gender"] = df["C1"].map(L.GENDER)
    df["age_group"] = pd.cut(df["C3"].where(df["C3"] > 0), [0, 24, 34, 44, 54, 120],
                             labels=["<25", "25-34", "35-44", "45-54", "55+"]).astype(str)
    df.loc[df["C3"].isna() | (df["C3"] <= 0), "age_group"] = np.nan
    df["status"] = df["call_status"].map(L.CALL_STATUS).fillna(
        "Code " + df["call_status"].astype("Int64").astype(str))

    df["reached"] = df["response"].isin([1, 2, 5, 6])
    df["completed"] = df["call_status"] == 1
    df["verified"] = (df["B1"] == 1) | (df["B1a"] == 0)
    df["duration_min"] = df["duration_total"] / 60
    return df


def valid(s):
    """Drop refused / don't know / not applicable codes."""
    return s.where(~s.isin(DK))
