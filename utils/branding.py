"""Laterite colours, page CSS and the Plotly template used by every chart."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Brand colours (from the brief - confirm with comms)
NAVY = "#1B365D"
TEAL = "#00A3B1"
CORAL = "#FF6B6B"
LIGHT = "#F8F9FA"
TEXT = "#2C3E50"
GREY = "#8A99A8"
GRID = "#E3E8EE"

PALETTE = [NAVY, TEAL, CORAL, "#F2A541", "#7A8FA6", "#5CC8C2", "#9B5DE5"]
LIKERT = [CORAL, "#FFB3B3", "#D5DBE1", "#66C8D0", NAVY]  # worst -> best


CSS = f"""
<style>
.stApp {{ background: {LIGHT}; }}
h1, h2, h3 {{ color: {NAVY} !important; }}

section[data-testid="stSidebar"] {{ background: {NAVY}; }}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {{ color: #FFFFFF !important; }}
section[data-testid="stSidebar"] [data-baseweb="tag"] {{ background: {TEAL} !important; }}
section[data-testid="stSidebar"] [data-baseweb="tag"] span {{ color: #FFFFFF !important; }}

div[data-testid="stMetric"] {{
    background: #FFFFFF;
    border: 1px solid {GRID};
    border-left: 5px solid {TEAL};
    border-radius: 10px;
    padding: 12px 16px;
}}
div[data-testid="stMetricValue"] {{ color: {NAVY}; }}

.header {{
    background: linear-gradient(90deg, {NAVY}, #1F6F8B);
    color: white; border-radius: 12px; padding: 18px 24px; margin-bottom: 18px;
}}
.header h1 {{ color: white !important; margin: 0; font-size: 1.7rem; }}
.header p {{ color: #DDE6EE; margin: 4px 0 0 0; }}
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)

    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Source Sans Pro, sans-serif", color=TEXT, size=13),
        title=dict(font=dict(size=15, color=NAVY)),
        colorway=PALETTE,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, automargin=True),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, automargin=True),
        legend=dict(title=dict(text="")),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    pio.templates["laterite"] = template
    pio.templates.default = "laterite"


def header(title, subtitle=""):
    st.markdown(f"<div class='header'><h1>{title}</h1><p>{subtitle}</p></div>",
                unsafe_allow_html=True)
