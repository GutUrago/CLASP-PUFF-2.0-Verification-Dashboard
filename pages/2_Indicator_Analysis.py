"""Indicator analysis, following the Indicators sheet of the PUFF 2.0 workbook.

Only completed interviews (call_status = 1) are used. Refused / don't know
answers are left out of each denominator.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import labels as L
from utils.branding import GREY, NAVY, TEAL, header
from utils.charts import (average, before_after, distribution, groups, likert, multi_select,
                          percent_yes, show)
from utils.data_loader import valid

if "df" not in st.session_state:
    st.switch_page("app.py")
by = st.session_state["by"]
df = st.session_state["df"]
df = df[df["completed"]]

header("Indicator analysis", f"Completed interviews: {len(df):,}")
if df.empty:
    st.warning("No completed interviews for the selected filters.")
    st.stop()


def yes(var, codes=(1,)):
    """1 if the answer is one of `codes`, 0 otherwise, NaN if skipped / don't know."""
    s = valid(df[var])
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
        "Aware of the subsidy (J1a)": yes("J1a"),
        "Resilience improved overall (PCRS_global)": yes("PCRS_global", (4, 5)),
    }
    g = groups(df, by)
    table = pd.DataFrame({name: s.groupby(g).mean() * 100 for name, s in indicators.items()}).T
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
        disability = (df[[f"C4_{i}" for i in range(1, 7)]] == 1).any(axis=1)
        percent_yes(df, disability, by, "Any functional difficulty (C4, Washington Group)")

# --------------------------------------------------------------------------- #
with tabs[2]:
    a, b = st.columns(2)
    with a:
        percent_yes(df, yes("B8"), by, "Purchase month confirmed (B8)")
        percent_yes(df, yes("D1"), by, "Still has the appliance (D1)")
        percent_yes(df, yes("D4"), by, "Good working condition (D4)")
    with b:
        distribution(df, "D5", L.USE_PURPOSE, by, "Main use of the appliance (D5)")
        percent_yes(df, yes("D2"), by, "Still using it (D2)")
        distribution(df, "D8", L.DECISION, by, "Who decided to buy it (D8)")
    distribution(df, "D3", L.NOT_USING, by, "Why it is no longer used (D3)")

# --------------------------------------------------------------------------- #
with tabs[3]:
    a, b = st.columns(2)
    with a:
        before_after(df, "E1a", "E1b", L.ENERGY_SOURCE, "Household energy sources, before vs now")
        percent_yes(df, polluting_before, by, "Uses diesel or kerosene - before", color=GREY)
    with b:
        before_after(df, "F1a", "F1b", L.ENERGY_SOURCE, "Business energy sources, before vs now")
        percent_yes(df, polluting_now, by, "Uses diesel or kerosene - now")
    distribution(df, "E5", L.REPLACE, by, "Does the appliance replace or complement the previous one? (E5)")

# --------------------------------------------------------------------------- #
with tabs[4]:
    rows = []
    for name, before, now in [("Household income", "F1", "F3"), ("Business revenue", "F2", "F4")]:
        pair = pd.DataFrame({"group": groups(df, by), "Before": to_usd(df[before]), "Now": to_usd(df[now])}).dropna()
        med = pair.groupby("group")[["Before", "Now"]].median().reset_index().melt("group", var_name="when")
        med["measure"] = name
        rows.append(med)
    t = pd.concat(rows)
    fig = px.bar(t, x="group", y="value", color="when", facet_col="measure", barmode="group",
                 title="Median monthly income and revenue (USD)",
                 color_discrete_map={"Before": GREY, "Now": TEAL})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_yaxes(title=None, tickprefix="$", matches=None)
    fig.update_xaxes(title=None)
    show(fig, 380)

    a, b = st.columns(2)
    with a:
        distribution(df, "F4a", L.YESNO_PARTIAL, by, "Income change due to the appliance? (F4a)")
        percent_yes(df, yes("G1_new"), by, "Started a new business thanks to the appliance (G1_new)")
    with b:
        distribution(df, "F5", L.YIELD_CHANGE, by, "Change in crop yields (F5)", ordered=True)
        percent_yes(df, yes("H1"), by, "Serving more customers (H1)")

    rows = []
    for key, name in L.TIME_ACTIVITIES.items():
        pair = df[[f"G11_{key}", f"G10_{key}"]].apply(valid).dropna()
        if len(pair):
            rows.append({"activity": name, "Before": pair.iloc[:, 0].mean(), "Now": pair.iloc[:, 1].mean()})
    t = pd.DataFrame(rows).melt("activity", var_name="when", value_name="hours")
    fig = px.bar(t, x="hours", y="activity", color="when", barmode="group", orientation="h",
                 title="Hours per day spent on each activity (G11 before, G10 now)",
                 color_discrete_map={"Before": GREY, "Now": TEAL})
    fig.update_layout(yaxis_title=None, xaxis_title="hours / day")
    show(fig, 400)
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
        t = pd.DataFrame({"group": groups(df, by), "nps": nps}).dropna()
        t = t.groupby("group")["nps"].apply(lambda x: 100 * ((x >= 9).mean() - (x <= 6).mean())).reset_index()
        fig = px.bar(t, x="nps", y="group", orientation="h", text=t["nps"].round().astype(int),
                     title="Net Promoter Score (% promoters - % detractors)", color_discrete_sequence=[TEAL])
        fig.update_layout(xaxis=dict(range=[-100, 100], title=None), yaxis_title=None)
        show(fig, 90 + 45 * len(t))
        average(df, score_0_100("CES", 7), by, "Customer Effort Score (0-100)", color=TEAL)
        percent_yes(df, yes("J1a"), by, "Aware the price was subsidised (J1a)")

# --------------------------------------------------------------------------- #
with tabs[6]:
    a, b = st.columns(2)
    with a:
        multi_select(df, "PCRS_0", L.SHOCKS, "Climate shocks experienced (PCRS_0)")
    with b:
        average(df, pcrs_index, by, "Perceived Climate Resilience Score (0-100, 50 = no change)", color=TEAL)
    likert(df, L.PCRS_ITEMS, "Resilience pillars (1 = much worse, 3 = no change, 5 = much better)")
