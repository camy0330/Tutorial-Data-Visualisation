
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Malaysian District Data Visualisation",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path(__file__).parent / "processed_data"


# =========================================================
# 2. COLOUR PALETTE
# =========================================================

COLORS = {
    "navy": "#24445C",
    "blue": "#397F91",
    "orange": "#D6A66B",
    "red": "#B85C50",
    "green": "#79AFA8",
    "purple": "#81749B",
    "teal": "#397F91",
    "gold": "#C6A36A",
    "dark": "#263442",
    "grey": "#718096",
    "grid": "#E5EAF0",
    "white": "#FFFFFF",
    "sage": "#79AFA8",
    "slate": "#8795A5"
}

CATEGORY_COLORS = [
    "#24445C", "#397F91", "#79AFA8", "#D6A66B",
    "#81749B", "#8795A5", "#A6B7B2", "#C28E78"
]


# =========================================================
# 3. GLOBAL CHART STYLE
# =========================================================

def style_chart(fig, height=600):

    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color=COLORS["dark"]
        ),
        title=dict(
            font=dict(
                size=19,
                color=COLORS["dark"]
            ),
            x=0.02,
            xanchor="left"
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(
            l=90,
            r=90,
            t=85,
            b=75
        ),
        legend=dict(
            font=dict(
                size=12,
                color=COLORS["dark"]
            ),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#D9E0E8",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#687385",
            font=dict(
                color="#202A35",
                size=13
            )
        ),
        hovermode="closest"
