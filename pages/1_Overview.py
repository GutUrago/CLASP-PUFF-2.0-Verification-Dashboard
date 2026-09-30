"""Overview: sample progress, response rates, timeline and geography."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.branding import CORAL, GREY, GRID, NAVY, PALETTE, TEAL, header
from utils.charts import percent_yes, show

# Sample targets (completed interviews) - update with the sampling plan
TARGET = {"Ethiopia": 300, "Kenya": 300, "Nigeria": 300}

if "df" not in st.session_state:
    st.switch_page("app.py")
df = st.session_state["df"]
by = st.session_state["by"] or "mode"

header("Fieldwork overview", f"{df['date'].min():%d %b} to {df['date'].max():%d %b %Y}")
if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---- key numbers ---------------------------------------------------------- #
completed = int(df["completed"].sum())
target = sum(TARGET.values())
consented = df[df["consent_ok"] == 1]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Attempts", f"{len(df):,}")
c2.metric("Reach rate", f"{df['reached'].mean():.0%}")
c3.metric("Completed", f"{completed:,}", f"{completed / target:.0%} of target", delta_color="off")
c4.metric("Purchase verified", f"{consented['verified'].mean():.0%}", help="Among consented respondents")
c5.metric("Median length", f"{df.loc[df['completed'], 'duration_min'].median():.0f} min")

# ---- progress ------------------------------------------------------------- #
st.subheader("Sample progress")
left, right = st.columns([1, 1.6])

with left:
    done = df.groupby("country")["completed"].sum()
    countries = list(TARGET)
    fig = go.Figure()
    fig.add_bar(y=countries, x=list(TARGET.values()), orientation="h", name="Target", marker_color=GRID)
    fig.add_bar(y=countries, x=[done.get(c, 0) for c in countries], orientation="h", name="Completed",
                marker_color=TEAL)
    fig.update_layout(barmode="overlay", title="Completed vs target")
    show(fig, 320)

with right:
    daily = df.groupby("date").agg(attempts=("KEY", "size"), completed=("completed", "sum")).reset_index()
    daily["cumulative"] = daily["completed"].cumsum()
    fig = go.Figure()
    fig.add_bar(x=daily["date"], y=daily["attempts"], name="Attempts", marker_color=GRID)
    fig.add_bar(x=daily["date"], y=daily["completed"], name="Completed", marker_color=TEAL)
    fig.add_scatter(x=daily["date"], y=daily["cumulative"], name="Cumulative completed", yaxis="y2",
                    mode="lines+markers", line=dict(color=NAVY, width=3))
    fig.add_hline(y=target, yref="y2", line_dash="dot", line_color=CORAL,
                  annotation_text=f"Target {target}")
    fig.update_layout(title="Daily progress", barmode="overlay",
                      yaxis2=dict(overlaying="y", side="right", showgrid=False, range=[0, target * 1.1]),
                      legend=dict(orientation="h", y=-0.15))
    show(fig, 320)

# ---- outcomes ------------------------------------------------------------- #
st.subheader("Attempt outcomes")
left, right = st.columns(2)

with left:
    status = df["status"].value_counts().reset_index()
    status["pct"] = 100 * status["count"] / status["count"].sum()
    fig = px.bar(status, x="count", y="status", orientation="h", title="Final status of each attempt",
                 text=status["pct"].round().astype(int).astype(str) + "%", color_discrete_sequence=[NAVY])
    fig.update_layout(yaxis=dict(autorange="reversed", title=None), xaxis_title=None)
    show(fig, 420)

with right:
    percent_yes(df, df["reached"], by, "Reach rate")
    percent_yes(df, df["completed"], by, "Completion rate", color=NAVY)

# ---- geography ------------------------------------------------------------ #
st.subheader("Where interviews were completed")
left, right = st.columns(2)
done = df[df["completed"]]

with left:
    t = done.groupby(["country", "region"]).size().reset_index(name="completed").sort_values("completed")
    fig = px.bar(t, x="completed", y="region", color="country", orientation="h",
                 title="Completed interviews by region", color_discrete_sequence=PALETTE)
    fig.update_layout(yaxis_title=None, xaxis_title=None)
    show(fig, 480)

with right:
    t = done.groupby(["country", "appliance"]).size().reset_index(name="completed")
    fig = px.bar(t, x="country", y="completed", color="appliance", title="Completed by country and appliance",
                 color_discrete_sequence=PALETTE)
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    show(fig, 480)
