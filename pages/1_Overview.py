"""Overview: progress against the sample roster.

Progress is measured against the main households on the roster. A household
is completed when one of its attempts has interview_ok = 1 (purchase
confirmed). Replacement households are shown separately.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.branding import CORAL, GREY, GRID, NAVY, TEAL, header
from utils.charts import show
from utils.data_loader import valid
from utils.roster import GROUP_ORDER, household_status

# Current submissions are from pilot IDs, which are not on the roster.
# Set to True once the fetch date skips the pilot.
CHECK_IDS_AGAINST_ROSTER = False

if "df" not in st.session_state:
    st.switch_page("app.py")
df = st.session_state["df"]            # attempts
roster = st.session_state["roster"]    # sampled households

hh = household_status(roster, df)
main = hh[hh["sample"] == "Main"]
repl = hh[hh["sample"] == "Replacement"]

period = f"{df['date'].min():%d %b} to {df['date'].max():%d %b %Y}" if df["date"].notna().any() else "No attempts yet"
header("Fieldwork progress", f"{period} · target: {len(main):,} main households")

# ---- key numbers ---------------------------------------------------------- #
# Total sample = main households on the roster. While the data is pilot only
# (IDs not on the roster), attempted / completed count the IDs in the data.
if CHECK_IDS_AGAINST_ROSTER:
    attempted = int((main["attempts"] > 0).sum())
    completed = int(main["completed"].sum())
else:
    attempted = df["hh_id"].nunique()
    completed = df.loc[df["completed"], "hh_id"].nunique()

asked_b1 = df.loc[df["B1"].isin([0, 1]), "hh_id"].nunique()
confirmed = df.loc[df["B1"] == 1, "hh_id"].nunique()
csat = valid(df.loc[df["completed"], "CSAT_global"]).dropna()


def share(part, whole):
    return f"{part / whole:.0%} of {whole:,}" if whole else None


c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total sample", f"{len(main):,}", help="Main households on the roster")
c2.metric("Attempted", f"{attempted:,}", share(attempted, len(main)), delta_color="off",
          help="Households with at least one attempt")
c3.metric("Completed", f"{completed:,}", share(completed, len(main)), delta_color="off",
          help="Households with an interview where the purchase was confirmed (interview_ok = 1)")
c4.metric("Confirmed (B1)", f"{confirmed:,}", share(confirmed, asked_b1), delta_color="off",
          help="Households where the respondent confirmed they or a household member bought "
               "the appliance (B1 = Yes), out of households asked")
c5.metric("CSAT", f"{(csat >= 4).mean():.0%}" if len(csat) else "-",
          f"n = {len(csat):,}" if len(csat) else None, delta_color="off",
          help="Share of completed interviews satisfied overall with the appliance (CSAT_global 4 or 5)")

# ---- progress over time ----------------------------------------------------- #
st.subheader("Progress over time")
left, right = st.columns([1.6, 1])

with left:
    daily = df.groupby("date").size().rename("attempts").to_frame()
    daily = daily.join(main.groupby("completed_on").size().rename("main_completed"), how="outer").fillna(0)
    daily["cumulative"] = daily["main_completed"].cumsum()
    fig = go.Figure()
    fig.add_bar(x=daily.index, y=daily["attempts"], name="Attempts", marker_color=GRID)
    fig.add_bar(x=daily.index, y=daily["main_completed"], name="Main completed", marker_color=TEAL)
    fig.add_scatter(x=daily.index, y=daily["cumulative"], name="Cumulative main completed", yaxis="y2",
                    mode="lines+markers", line=dict(color=NAVY, width=3))
    fig.add_hline(y=len(main), yref="y2", line_dash="dot", line_color=CORAL,
                  annotation_text=f"Target {len(main)}")
    fig.update_layout(title="Daily attempts and completed main households", barmode="overlay",
                      yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                  range=[0, max(len(main), 1) * 1.1]),
                      legend=dict(orientation="h", y=-0.15))
    show(fig, 360)

with right:
    counts = pd.DataFrame({
        "Main": main["outcome"].value_counts(),
        "Replacement": repl["outcome"].value_counts(),
    }).reindex(GROUP_ORDER).fillna(0).reset_index(names="outcome")
    t = counts.melt("outcome", var_name="sample", value_name="households")
    t = t[t["households"] > 0]
    fig = px.bar(t, x="households", y="sample", color="outcome", orientation="h",
                 title="Where each household stands", category_orders={"outcome": GROUP_ORDER},
                 color_discrete_map=dict(zip(GROUP_ORDER, [TEAL, CORAL, "#F2A541", "#9B5DE5", GREY,
                                                           NAVY, "#5CC8C2", GRID])))
    fig.update_layout(xaxis_title=None, yaxis_title=None, legend=dict(orientation="h", y=-0.2))
    show(fig, 360)

# ---- progress by company and county --------------------------------------- #
st.subheader("Main sample by company and county")


def progress_bars(by, title, top=None):
    t = main.groupby(by).agg(households=("hh_id", "size"), completed=("completed", "sum")).reset_index()
    t["pct"] = 100 * t["completed"] / t["households"]
    t = t.sort_values("households", ascending=False)
    if top:
        t = t.head(top)
    t = t.iloc[::-1]
    # percentage bars, so small companies are as readable as large ones
    fig = px.bar(t, x="pct", y=by, orientation="h", title=title,
                 text=t["completed"].astype(int).astype(str) + " of " + t["households"].astype(str),
                 color_discrete_sequence=[TEAL])
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}: %{x:.0f}% (%{text})<extra></extra>")
    fig.update_layout(xaxis=dict(range=[0, 115], ticksuffix="%", title=None), yaxis_title=None)
    show(fig, 100 + 28 * len(t))


left, right = st.columns(2)
with left:
    progress_bars("company", "% of main households completed, by company")
with right:
    progress_bars("county", "% of main households completed, by county (15 largest)", top=15)

# ---- attempts and outcomes -------------------------------------------------- #
st.subheader("Attempts")
left, right = st.columns(2)

with left:
    tried = hh[hh["attempts"] > 0]
    t = tried["attempts"].clip(upper=5).value_counts().sort_index().reset_index()
    t["label"] = t["attempts"].astype(str).replace({"5": "5+"})
    fig = px.bar(t, x="label", y="count", title="Attempts per household (attempted households)",
                 color_discrete_sequence=[NAVY])
    fig.update_layout(xaxis_title="attempts", yaxis_title="households")
    show(fig, 340)

with right:
    status = df["status"].value_counts().reset_index()
    fig = px.bar(status, x="count", y="status", orientation="h", title="Outcome of every attempt",
                 color_discrete_sequence=[NAVY])
    fig.update_layout(yaxis=dict(autorange="reversed", title=None), xaxis_title=None)
    show(fig, 340)
