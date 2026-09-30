"""
CLASP PUFF 2.0 - Verification survey dashboard (Laterite)

Run with:   streamlit run app.py

app.py loads the data, draws the sidebar filters and then opens the selected
page. The filtered data is shared with the pages through st.session_state.
"""
import streamlit as st

st.set_page_config(page_title="PUFF 2.0 Verification", page_icon=":material/bolt:", layout="wide")

from utils.branding import setup      # noqa: E402
from utils.data_loader import load_data  # noqa: E402

setup()

pages = st.navigation([
    st.Page("pages/1_Overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("pages/2_Indicator_Analysis.py", title="Indicator analysis", icon=":material/insights:",
            url_path="indicators"),
])

# ---- data ---------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## PUFF 2.0 Verification")
    if st.button("Refresh data", help="Fetch the latest submissions from SurveyCTO"):
        load_data.clear()

df, source, warning = load_data()

if df is None:
    st.error(warning)
    st.stop()

if warning:
    print(f"[data] {warning}")  # shown in the terminal only, not in the app

with st.sidebar:
    st.markdown("### Filters")
    start, end = df["date"].min().date(), df["date"].max().date()
    dates = st.date_input("Interview date", (start, end), min_value=start, max_value=end)
    if len(dates) == 2:
        df = df[(df["date"].dt.date >= dates[0]) & (df["date"].dt.date <= dates[1])]

    for label, col in [("Country", "country"), ("Region", "region"), ("Distributor", "distributor"),
                       ("Appliance", "appliance"), ("Survey mode", "mode")]:
        picked = st.multiselect(label, sorted(df[col].dropna().unique()), placeholder="All")
        if picked:
            df = df[df[col].isin(picked)]

    st.markdown("### Disaggregate by")
    breakdowns = {"None": None, "Country": "country", "Distributor": "distributor",
                  "Appliance": "appliance", "Survey mode": "mode", "Region": "region",
                  "Gender": "gender", "Age group": "age_group"}
    by = breakdowns[st.selectbox("Breakdown", list(breakdowns), index=1, label_visibility="collapsed")]

st.session_state["df"] = df
st.session_state["by"] = by

pages.run()
