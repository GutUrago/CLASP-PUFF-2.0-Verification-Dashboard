"""A handful of chart helpers shared by the two pages."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.branding import GREY, LIKERT, NAVY, PALETTE, TEAL
from utils.data_loader import valid


def show(fig, height=340):
    fig.update_layout(height=height, legend_title_text="")
    st.plotly_chart(fig, width="stretch", theme=None)


def no_data(title):
    """Placeholder when a question has no answers yet (or isn't published)."""
    st.markdown(f"**{title}**")
    st.caption("No data yet.")


def groups(df, by):
    """Series used to split the chart. 'All' when no breakdown is chosen."""
    if by is None:
        return pd.Series("All", index=df.index)
    return df[by].fillna("Missing").astype(str)


def percent_yes(df, flag, by, title, color=TEAL):
    """Bar of the % of respondents where `flag` is 1 / True (NaN excluded)."""
    d = pd.DataFrame({"group": groups(df, by), "y": flag.astype(float)}).dropna()
    t = d.groupby("group")["y"].agg(pct="mean", n="size").reset_index()
    if t.empty:
        return no_data(title)
    t["pct"] *= 100
    fig = px.bar(t, x="pct", y="group", orientation="h", text=t["pct"].round().astype(int).astype(str) + "%",
                 custom_data=["n"], title=title, color_discrete_sequence=[color])
    fig.update_traces(hovertemplate="%{y}: %{x:.1f}% (n=%{customdata[0]})<extra></extra>")
    fig.update_layout(xaxis=dict(range=[0, 105], ticksuffix="%", title=None), yaxis_title=None)
    show(fig, 90 + 45 * len(t))


def distribution(df, var, value_labels, by, title, ordered=False):
    """100% stacked bar of a coded variable."""
    d = pd.DataFrame({"group": groups(df, by), "v": valid(df[var])}).dropna()
    d["answer"] = d["v"].map(value_labels)
    d = d.dropna(subset=["answer"])
    t = d.groupby(["group", "answer"]).size().reset_index(name="n")
    if t.empty:
        return no_data(title)
    t["pct"] = 100 * t["n"] / t.groupby("group")["n"].transform("sum")

    order = [lab for lab in value_labels.values() if lab in set(t["answer"])]
    color_map = None
    if ordered:  # worst -> best scale: coral to navy
        pick = {3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 3, 4]}[len(value_labels)]
        color_map = {lab: LIKERT[i] for lab, i in zip(value_labels.values(), pick)}
    fig = px.bar(t, x="pct", y="group", color="answer", orientation="h", title=title,
                 category_orders={"answer": order}, custom_data=["n", "answer"],
                 color_discrete_sequence=PALETTE, color_discrete_map=color_map)
    fig.update_traces(hovertemplate="%{y}<br>%{customdata[1]}: %{x:.1f}% (n=%{customdata[0]})<extra></extra>")
    fig.update_layout(xaxis=dict(range=[0, 100], ticksuffix="%", title=None), yaxis_title=None)
    show(fig, 130 + 45 * t["group"].nunique())


def multi_select(df, var, value_labels, title):
    """% of respondents choosing each option of a select_multiple question."""
    base = df[df[var].notna()]
    rows = []
    for code, lab in value_labels.items():
        col = f"{var}_{str(code).replace('-', '_')}"
        if col in base and len(base):
            rows.append({"option": lab, "pct": 100 * base[col].mean()})
    if not rows:
        return no_data(title)
    t = pd.DataFrame(rows).sort_values("pct")
    fig = px.bar(t, x="pct", y="option", orientation="h", title=title,
                 text=t["pct"].round().astype(int).astype(str) + "%", color_discrete_sequence=[NAVY])
    fig.update_traces(hovertemplate="%{y}: %{x:.1f}%<extra></extra>")
    fig.update_layout(xaxis=dict(ticksuffix="%", title=None), yaxis_title=None)
    show(fig, 90 + 32 * len(t))


def before_after(df, before, after, value_labels, title):
    """Share using each option before vs now (two select_multiple questions)."""
    rows = []
    for when, var in [("Before", before), ("Now", after)]:
        base = df[df[var].notna()]
        for code, lab in value_labels.items():
            col = f"{var}_{str(code).replace('-', '_')}"
            if col in base and len(base):
                rows.append({"option": lab, "when": when, "pct": 100 * base[col].mean()})
    if not rows:
        return no_data(title)
    t = pd.DataFrame(rows)
    fig = px.bar(t, x="pct", y="option", color="when", orientation="h", barmode="group", title=title,
                 color_discrete_map={"Before": GREY, "Now": TEAL})
    fig.update_traces(hovertemplate="%{y}: %{x:.1f}%<extra></extra>")
    fig.update_layout(xaxis=dict(ticksuffix="%", title=None), yaxis=dict(title=None, autorange="reversed"))
    show(fig, 380)


def likert(df, items, title):
    """Stacked bar for a battery of 1-5 questions."""
    rows = []
    for var, lab in items.items():
        s = valid(df[var]).dropna()
        for code, pct in (s.value_counts(normalize=True) * 100).items():
            rows.append({"item": lab, "score": str(int(code)), "pct": pct})
    if not rows:
        return no_data(title)
    t = pd.DataFrame(rows)
    fig = px.bar(t, x="pct", y="item", color="score", orientation="h", title=title,
                 category_orders={"score": ["1", "2", "3", "4", "5"], "item": list(items.values())},
                 color_discrete_sequence=LIKERT)
    fig.update_traces(hovertemplate="%{y}<br>score %{fullData.name}: %{x:.1f}%<extra></extra>")
    fig.update_layout(xaxis=dict(range=[0, 100], ticksuffix="%", title=None), yaxis_title=None)
    show(fig, 120 + 40 * len(items))


def average(df, values, by, title, color=NAVY):
    """Bar of the mean of `values` by group (used for 0-100 scores)."""
    d = pd.DataFrame({"group": groups(df, by), "v": values}).dropna()
    t = d.groupby("group")["v"].agg(mean="mean", n="size").reset_index()
    if t.empty:
        return no_data(title)
    fig = px.bar(t, x="mean", y="group", orientation="h", text=t["mean"].round().astype(int),
                 custom_data=["n"], title=title, color_discrete_sequence=[color])
    fig.update_traces(hovertemplate="%{y}: %{x:.1f} (n=%{customdata[0]})<extra></extra>")
    fig.update_layout(xaxis=dict(range=[0, 105], title=None), yaxis_title=None)
    show(fig, 90 + 45 * len(t))
