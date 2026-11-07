"""
CLASP PUFF 2.0 - Verification survey dashboard (Laterite)

Run with:   python -m streamlit run app.py

app.py loads the submissions and the sample roster, draws the sidebar filters
and then opens the selected page. The filtered data is shared with the pages
through st.session_state:
    df      - one row per attempt (submission), with roster details attached
    roster  - one row per sampled household
    by      - the breakdown chosen for the indicator charts
"""
import time

import streamlit as st

st.set_page_config(page_title="PUFF 2.0 Verification", page_icon=":material/bolt:", layout="wide")

from utils.branding import setup                       # noqa: E402
from utils.data_loader import REFRESH_HOURS, load_data  # noqa: E402
from utils.roster import attach_roster, load_roster    # noqa: E402

setup()

pages = st.navigation([
    st.Page("pages/1_Overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("pages/2_Indicator_Analysis.py", title="Indicator analysis", icon=":material/insights:",
            url_path="indicators"),
])


# Scheduled refresh: this small fragment wakes up every REFRESH_HOURS while
# the dashboard is open, pulls the data again and redraws the whole app.
# Filters and the selected page stay as they were.
@st.fragment(run_every=REFRESH_HOURS * 3600)
def scheduled_refresh():
    last = st.session_state.setdefault("last_refresh", time.time())
    if time.time() - last >= REFRESH_HOURS * 3600 - 5:
        st.session_state["last_refresh"] = time.time()
        load_data.clear()
        load_roster.clear()
        st.rerun(scope="app")


# ---- data ---------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## PUFF 2.0 Verification")
    refresh = st.button("Refresh data", help="Fetch the latest submissions from SurveyCTO")
    if refresh:
        load_data.clear()
        load_roster.clear()
        st.session_state["last_refresh"] = time.time()
    scheduled_refresh()
    st.caption(f"Refreshes every {REFRESH_HOURS} hours")

df, source, warning = load_data()

if refresh:  # short pop-up so you can see whether the pull worked
    if warning:
        st.toast(warning, icon=":material/warning:")
    else:
        st.toast(source, icon=":material/check_circle:")

if df is None:
    st.error(warning)
    st.stop()

if warning:
    print(f"[data] {warning}")  # shown in the terminal only, not in the app

roster = load_roster()
if roster is None:
    st.error("The sample roster could not be loaded: set roster_id in secrets.toml "
             "or add data/CLASP_PUFF_2.0_Sample_Roster.xlsx.")
    st.stop()
df = attach_roster(df, roster)

# ---- filters ------------------------------------------------------------- #
# Company, county, sample and assigned mode filter both the roster and the
# attempts; the date filter only applies to attempts.
with st.sidebar:
    st.markdown("### Filters")
    if df["date"].notna().any():
        start, end = df["date"].min().date(), df["date"].max().date()
        dates = st.date_input("Interview date", (start, end), min_value=start, max_value=end)
        if len(dates) == 2:
            df = df[(df["date"].dt.date >= dates[0]) & (df["date"].dt.date <= dates[1])]

    for label, col in [("Company", "company"), ("County", "county"),
                       ("Sample", "sample"), ("Assigned mode", "assigned_mode")]:
        options = sorted(set(roster[col].dropna()) | set(df[col].dropna()))
        picked = st.multiselect(label, options, placeholder="All")
        if picked:
            df = df[df[col].isin(picked)]
            roster = roster[roster[col].isin(picked)]

    st.markdown("### Disaggregate by")
    breakdowns = {"None": None, "Company": "company", "County": "county", "Sample": "sample",
                  "Survey mode": "mode", "Appliance": "appliance", "Gender": "gender",
                  "Age group": "age_group"}
    by = breakdowns[st.selectbox("Breakdown", list(breakdowns), index=1, label_visibility="collapsed")]

st.session_state["df"] = df
st.session_state["roster"] = roster
st.session_state["by"] = by

pages.run()
