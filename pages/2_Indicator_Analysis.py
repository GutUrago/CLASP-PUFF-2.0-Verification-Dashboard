"""Indicator analysis, following the Indicators sheet of the PUFF 2.0 workbook.

All charts use completed interviews: the purchase was confirmed and the
interview went ahead (interview_ok = 1). Questions about using the appliance
are skipped in the form when it was never received, so those households drop
out of the use charts on their own. Refused / don't know answers are left out
of each denominator.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import labels as L
from utils.branding import GREY, NAVY, TEAL, header
from utils.charts import (average, no_data, before_after, distribution, groups, likert, multi_select,
                          percent_yes, show)
from utils.data_loader import valid

if "df" not in st.session_state:
    st.switch_page("app.py")
by = st.session_state["by"]
df = st.session_state["df"]
df = df[df["completed"]]   # interview_ok = 1

header("Indicator analysis", f"Completed interviews: {len(df):,}")
if df.empty:
    st.warning("No completed interviews for the selected filters.")
    st.stop()


def yes(var, codes=(1,), data=None):
    """1 if the answer is one of `codes`, 0 otherwise, NaN if skipped / don't know."""
    data = df if data is None else data
    s = valid(data[var])
    return s.isin(codes).astype(float).where(s.notna())


def score_0_100(var, top):
    """Rescale a 1..top answer to 0-100."""
    return (valid(df[var]) - 1) / (top - 1) * 100


def any_selected(var, codes):
    cols = [f"{var}_{c}" for c in codes if f"{var}_{c}" in df]
    return (df[cols] == 1).any(axis=1).astype(float).where(df[var].notna())


def to_usd(amount):
    fx = df["p_currency"].map({"ETB": 150, "KES": 129, "NGN": 1550})  # same rates as the form
    return valid(amount) / fx


polluting_before = any_selected("E1a", [5, 6])   # diesel / kerosene
polluting_now = any_selected("E1b", [5, 6])
csat_index = pd.concat([score_0_100(v, 5) for v in L.CSAT_ITEMS if v != "CSAT_global"], axis=1).mean(axis=1)
pcrs_index = pd.concat([score_0_100(v, 5) for v in ["PCRS_1", "PCRS_2", "PCRS_3"]], axis=1).mean(axis=1)
nps = valid(df["NPS"])
income_change = valid(df["F3"]) - valid(df["F1"])
revenue_change = valid(df["F4"]) - valid(df["F2"])

tabs = st.tabs(["Summary", "Respondents", "Verification & use", "Energy", "Livelihoods",
                "Satisfaction", "Climate resilience"])

# --------------------------------------------------------------------------- #
with tabs[0]:
    indicators = {
        "Still has the appliance (D1)": yes("D1"),
        "Still using it (D2)": yes("D2"),
        "Good working condition (D4)": yes("D4"),
        "Used for income generation (D5)": yes("D5", (2, 3)),
        "Uses diesel/kerosene - before (E1a)": polluting_before,
        "Uses diesel/kerosene - now (E1b)": polluting_now,
        "Household income increased (F1 -> F3)": (income_change > 0).astype(float).where(income_change.notna()),
        "Business revenue increased (F2 -> F4)": (revenue_change > 0).astype(float).where(revenue_change.notna()),
        "Crop yields increased (F5)": yes("F5", (3,)),
        "Started a new business (G1_new)": yes("G1_new"),
        "Serving more customers (H1)": yes("H1"),
        "Wellbeing improved (I2)": yes("I2", (4, 5)),
        "Satisfied overall - CSAT (4-5)": yes("CSAT_global", (4, 5)),
        "Satisfied with price (J1)": yes("J1", (3, 4)),
        "Resilience improved - recovery (PCRS_1)": yes("PCRS_1", (4, 5)),
    }
    g = groups(df, by)
    table = pd.DataFrame({name: s.groupby(g).mean() * 100 for name, s in indicators.items()}).T

    table.loc["Appliance received (D1a)"] = yes("appliance_received").groupby(g).mean() * 100
    table.loc["Serial number verified (in-person)"] = yes("serial_verified").groupby(g).mean() * 100
    table.loc["CSAT index (0-100)"] = csat_index.groupby(g).mean()
    table.loc["PCRS index (0-100)"] = pcrs_index.groupby(g).mean()
    table.loc["Net Promoter Score"] = nps.groupby(g).apply(lambda x: 100 * ((x >= 9).mean() - (x <= 6).mean()))

    st.caption("Percentages of respondents who were asked the question, unless marked as an index or score.")
    st.dataframe(table.round(1), width="stretch", height=680)
    st.download_button("Download table (CSV)", table.round(1).to_csv().encode(), "puff2_indicators.csv")

# --------------------------------------------------------------------------- #
with tabs[1]:
    a, b = st.columns(2)
    with a:
        distribution(df, "C1", L.GENDER, by, "Respondent gender (C1)")
        distribution(df, "C2", L.EDUCATION, by, "Education (C2)")
    with b:
        age = df.assign(group=groups(df, by)).dropna(subset=["age_group"])
        t = age.groupby(["group", "age_group"]).size().reset_index(name="n")
        t["pct"] = 100 * t["n"] / t.groupby("group")["n"].transform("sum")
        fig = px.bar(t, x="age_group", y="pct", color="group", barmode="group", title="Age group (C3)",
                     category_orders={"age_group": ["<25", "25-34", "35-44", "45-54", "55+"]})
        fig.update_layout(yaxis=dict(ticksuffix="%", title=None), xaxis_title=None)
        show(fig, 340)
        # C4_1..C4_6 are only asked when the screening question C4_screen = Yes
        difficulty = (df[[f"C4_{i}" for i in range(1, 7)]] == 1).any(axis=1)
        difficulty = difficulty.astype(float).where(valid(df["C4_screen"]).notna())
        percent_yes(df, difficulty, by, "Any functional difficulty (C4, Washington Group)")

# --------------------------------------------------------------------------- #
with tabs[2]:
    st.markdown("#### Verification")
    a, b = st.columns(2)
    with a:
        percent_yes(df, yes("appliance_received"), by,
                    "Appliance received and installed (D1a)")
        percent_yes(df, yes("B8"), by, "Purchase month confirmed (B8)")
        distribution(df, "B0a", L.CONTACTED_BY, by, "Who told them about this survey (B0a)")
    with b:
        distribution(df, "D1b", L.NOT_RECEIVED, by, "Why it was not received or installed (D1b)")
        distribution(df, "B10a", L.DESC_MATCH, by, "Phone: description vs sales record (B10a)")
        distribution(df, "serial_access", L.SERIAL_ACCESS, by, "In-person: serial number (M2)")
    percent_yes(df, yes("serial_verified"), by,
                "In-person: serial number matches the record (M3)")

    st.markdown("#### Ownership and use")
    a, b = st.columns(2)
    with a:
        percent_yes(df, yes("D1"), by, "Still has the appliance (D1)")
        percent_yes(df, yes("D4"), by, "Good working condition (D4)")
        distribution(df, "D5", L.USE_PURPOSE, by, "Main use of the appliance (D5)")
    with b:
        distribution(df, "D1a", L.APPLIANCE_FATE, by, "What happened to it, if no longer owned (D1a)")
        percent_yes(df, yes("D2"), by, "Still using it (D2)")
        distribution(df, "D8", L.DECISION, by, "Who decided to buy it (D8)")
    a, b = st.columns(2)
    with a:
        distribution(df, "D3", L.NOT_USING, by, "Why it is no longer used (D3)")
    with b:
        multi_select(df, "D5b", L.PUMP_USE, "Solar pumps: what the pump is used for (D5b)")

# --------------------------------------------------------------------------- #
with tabs[3]:
    a, b = st.columns(2)
    with a:
        before_after(df, "E1a", "E1b", L.ENERGY_SOURCE, "Household energy sources, before vs now")
        percent_yes(df, polluting_before, by, "Uses diesel or kerosene - before", color=GREY)
    with b:
        before_after(df, "F1a", "F1b", L.ENERGY_SOURCE, "Business energy sources, before vs now")
        percent_yes(df, polluting_now, by, "Uses diesel or kerosene - now")
    a, b = st.columns(2)
    with a:
        distribution(df, "E5", L.REPLACE, by, "Replace or complement the previous appliance? (E5)")
    with b:
        multi_select(df, "E6", L.PREVIOUS_FATE, "What happened to the previous appliance (E6)")

# --------------------------------------------------------------------------- #
with tabs[4]:
    rows = []
    for name, before, now in [("Household income", "F1", "F3"), ("Business revenue", "F2", "F4")]:
        pair = pd.DataFrame({"group": groups(df, by), "Before": to_usd(df[before]), "Now": to_usd(df[now])}).dropna()
        med = pair.groupby("group")[["Before", "Now"]].median().reset_index().melt("group", var_name="when")
        med["measure"] = name
        rows.append(med)
    t = pd.concat(rows)
    if t.empty:
        no_data("Median monthly income and revenue (USD)")
    else:
        fig = px.bar(t, x="group", y="value", color="when", facet_col="measure", barmode="group",
                     title="Median monthly income and revenue (USD)",
                     color_discrete_map={"Before": GREY, "Now": TEAL})
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_yaxes(title=None, tickprefix="$", matches=None)
        fig.update_xaxes(title=None)
        show(fig, 380)

    a, b = st.columns(2)
    with a:
        distribution(df, "F4a", L.YESNO_PARTIAL, by, "Household income change due to the appliance? (F4a)")
        distribution(df, "F4b", L.YESNO_PARTIAL, by, "Business revenue change due to the appliance? (F4b)")
        percent_yes(df, yes("G1_new"), by, "Started a new business thanks to the appliance (G1_new)")
    with b:
        distribution(df, "F5", L.YIELD_CHANGE, by, "Change in crop yields (F5)", ordered=True)
        percent_yes(df, yes("H1"), by, "Serving more customers (H1, businesses before purchase)")

    rows = []
    for key, name in L.TIME_ACTIVITIES.items():
        if f"G11_{key}" not in df or f"G10_{key}" not in df:
            continue
        pair = df[[f"G11_{key}", f"G10_{key}"]].apply(valid).dropna()
        if len(pair):
            rows.append({"activity": name, "Before": pair.iloc[:, 0].mean(), "Now": pair.iloc[:, 1].mean()})
    title = "Hours per day spent on each activity (G11 before, G10 now)"
    if rows:
        t = pd.DataFrame(rows).melt("activity", var_name="when", value_name="hours")
        fig = px.bar(t, x="hours", y="activity", color="when", barmode="group", orientation="h",
                     title=title, color_discrete_map={"Before": GREY, "Now": TEAL})
        fig.update_layout(yaxis_title=None, xaxis_title="hours / day")
        show(fig, 400)
    else:
        no_data(title)
    distribution(df, "I2", L.WELLBEING, by, "Change in household wellbeing (I2)", ordered=True)

# --------------------------------------------------------------------------- #
with tabs[5]:
    likert(df, L.CSAT_ITEMS, "Customer satisfaction items (1 = worst, 5 = best)")
    a, b = st.columns(2)
    with a:
        average(df, csat_index, by, "CSAT index (0-100)")
        distribution(df, "J1", L.SATISFACTION_4, by, "Satisfaction with the price (J1)", ordered=True)
        multi_select(df, "J6", L.PAYMENT, "How the appliance was paid for (J6)")
    with b:
        title = "Net Promoter Score (% promoters - % detractors)"
        t = pd.DataFrame({"group": groups(df, by), "nps": nps}).dropna()
        if t.empty:
            no_data(title)
        else:
            t = t.groupby("group")["nps"].apply(lambda x: 100 * ((x >= 9).mean() - (x <= 6).mean())).reset_index()
            fig = px.bar(t, x="nps", y="group", orientation="h", text=t["nps"].round().astype(int),
                         title=title, color_discrete_sequence=[TEAL])
            fig.update_layout(xaxis=dict(range=[-100, 100], title=None), yaxis_title=None)
            show(fig, 90 + 45 * len(t))
        average(df, score_0_100("CES", 7), by, "Customer Effort Score (0-100)", color=TEAL)
        distribution(df, "K_warranty", L.WARRANTY_KNOW, by, "Knows about the warranty (J16)")

# --------------------------------------------------------------------------- #
with tabs[6]:
    a, b = st.columns(2)
    with a:
        multi_select(df, "PCRS_0", L.SHOCKS, "Climate shocks experienced (PCRS_0)")
    with b:
        average(df, pcrs_index, by, "Perceived Climate Resilience Score (0-100, 50 = no change)", color=TEAL)
    likert(df, L.PCRS_ITEMS, "Resilience pillars (1 = much worse, 3 = no change, 5 = much better)")
