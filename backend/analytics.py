"""
analytics.py — Pandas Data Analytics & Matplotlib / Plotly Visualization
════════════════════════════════════════════════════════════════════════
Smart Irrigation Advisory System · Hackathon Backend

Provides four analytics capabilities:
  1. Water-usage trend (daily / weekly / monthly aggregation via Pandas)
  2. Recommendation-adherence scoring (Pandas apply + groupby)
  3. Moisture trend analysis (rolling average via Pandas)
  4. Chart generation in two formats:
     • Matplotlib  → server-side PNG (returned as base64 string)
     • Plotly JSON → consumed directly by react-plotly.js on the frontend
"""

import io
import base64
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np

# Matplotlib — non-interactive backend for server-side rendering
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch

# Plotly — generates JSON figures for the React frontend
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils


# ── Colour Palette (matches frontend design system) ─────────────────
COLORS = {
    "primary":    "#059669",   # Emerald-600
    "secondary":  "#0EA5E9",   # Sky-500
    "success":    "#22C55E",   # Green-500
    "warning":    "#F59E0B",   # Amber-500
    "danger":     "#EF4444",   # Red-500
    "surface":    "#F8FAFC",   # Slate-50
    "text":       "#1E293B",   # Slate-800
    "muted":      "#94A3B8",   # Slate-400
}


# ═══════════════════════════════════════════════════════════════════════
# 1 · WATER-USAGE TREND
# ═══════════════════════════════════════════════════════════════════════

def compute_water_usage_trend(
    irrigation_logs: List[Dict[str, Any]],
    period: str = "daily",
) -> List[Dict[str, Any]]:
    """
    Aggregate irrigation amounts by time period using Pandas groupby.

    Parameters
    ----------
    irrigation_logs : list[dict]
        Each entry must have 'date' (ISO string) and 'actual_amount_mm'.
    period : str
        One of 'daily', 'weekly', 'monthly'.

    Returns
    -------
    list[dict] — Sorted by date, with keys 'date' and 'actual_amount_mm'.
    """
    if not irrigation_logs:
        return []

    df = pd.DataFrame(irrigation_logs)
    required = {"date", "actual_amount_mm"}
    if not required.issubset(df.columns):
        return []

    df["date"]             = pd.to_datetime(df["date"], errors="coerce")
    df["actual_amount_mm"] = pd.to_numeric(df["actual_amount_mm"], errors="coerce").fillna(0)
    df = df.dropna(subset=["date"])

    freq_map = {"daily": "D", "weekly": "W", "monthly": "ME"}
    freq = freq_map.get(period, "D")

    agg = (
        df.set_index("date")
          .resample(freq)["actual_amount_mm"]
          .agg(["sum", "count", "mean"])
          .reset_index()
          .rename(columns={"sum": "total_mm", "count": "irrigation_count", "mean": "avg_mm"})
    )
    agg["date"]    = agg["date"].dt.strftime("%Y-%m-%d")
    agg["total_mm"] = agg["total_mm"].round(1)
    agg["avg_mm"]   = agg["avg_mm"].round(1)
    return agg.to_dict("records")


# ═══════════════════════════════════════════════════════════════════════
# 2 · RECOMMENDATION ADHERENCE
# ═══════════════════════════════════════════════════════════════════════

def compute_adherence(irrigation_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate how often farmers followed the advisory recommendation.

    Adherence rules (matching original Cloud Functions logic):
      • recommendation == 'irrigate' AND action_taken == 'irrigated' → ✓
      • recommendation == 'wait'     AND action_taken == 'skipped'   → ✓
      • Amount within ±20% of recommended                           → ✓ (partial)
    """
    if not irrigation_logs:
        return {"adherence_percent": 0.0, "total_logs": 0, "adherent_count": 0, "details": []}

    df = pd.DataFrame(irrigation_logs)
    required = {"recommendation", "action_taken"}
    if not required.issubset(df.columns):
        return {"adherence_percent": 0.0, "total_logs": len(df), "adherent_count": 0, "details": []}

    def is_adherent(row: pd.Series) -> bool:
        rec    = str(row.get("recommendation", "")).lower().strip()
        action = str(row.get("action_taken", "")).lower().strip()
        # Exact match
        if rec == "irrigate" and action == "irrigated":
            return True
        if rec == "wait" and action in ("skipped", "waited"):
            return True
        # Amount-based partial match
        rec_amt = pd.to_numeric(row.get("recommended_amount_mm", 0), errors="coerce") or 0
        act_amt = pd.to_numeric(row.get("actual_amount_mm", 0), errors="coerce") or 0
        if rec_amt > 0 and act_amt > 0:
            ratio = act_amt / rec_amt
            if 0.8 <= ratio <= 1.2:
                return True
        return False

    df["adherent"] = df.apply(is_adherent, axis=1)
    adherent_count = int(df["adherent"].sum())
    total          = len(df)
    rate           = round((adherent_count / total) * 100, 1) if total > 0 else 0.0

    return {
        "adherence_percent": rate,
        "total_logs":        total,
        "adherent_count":    adherent_count,
        "non_adherent":      total - adherent_count,
    }


# ═══════════════════════════════════════════════════════════════════════
# 3 · MOISTURE TREND
# ═══════════════════════════════════════════════════════════════════════

def compute_moisture_trend(moisture_readings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse moisture readings: rolling average, min/max, trend direction.
    """
    if not moisture_readings:
        return {"readings": [], "stats": {}}

    df = pd.DataFrame(moisture_readings)
    if "moisture_percent" not in df.columns:
        return {"readings": [], "stats": {}}

    df["moisture_percent"] = pd.to_numeric(df["moisture_percent"], errors="coerce").fillna(0)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp")
        df["date_str"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    else:
        df["date_str"] = [f"Reading {i+1}" for i in range(len(df))]

    # Rolling average (window = 3)
    df["rolling_avg"] = df["moisture_percent"].rolling(window=min(3, len(df)), min_periods=1).mean().round(1)

    # Trend direction
    if len(df) >= 2:
        first_half = df["moisture_percent"].iloc[: len(df) // 2].mean()
        second_half = df["moisture_percent"].iloc[len(df) // 2:].mean()
        trend = "rising" if second_half > first_half + 2 else ("falling" if second_half < first_half - 2 else "stable")
    else:
        trend = "insufficient_data"

    stats = {
        "current":    round(float(df["moisture_percent"].iloc[-1]), 1),
        "average":    round(float(df["moisture_percent"].mean()), 1),
        "min":        round(float(df["moisture_percent"].min()), 1),
        "max":        round(float(df["moisture_percent"].max()), 1),
        "std_dev":    round(float(df["moisture_percent"].std()), 1) if len(df) > 1 else 0,
        "trend":      trend,
        "num_readings": len(df),
    }

    records = df[["date_str", "moisture_percent", "rolling_avg"]].to_dict("records")
    return {"readings": records, "stats": stats}


# ═══════════════════════════════════════════════════════════════════════
# 4 · CHART GENERATION — MATPLOTLIB
# ═══════════════════════════════════════════════════════════════════════

def _fig_to_base64(fig) -> str:
    """Convert a Matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=COLORS["surface"])
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_water_usage_chart(usage_data: List[Dict[str, Any]]) -> str:
    """
    Matplotlib bar chart of daily water usage.
    Returns base64-encoded PNG.
    """
    if not usage_data:
        return ""

    df = pd.DataFrame(usage_data)
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(COLORS["surface"])
    ax.set_facecolor(COLORS["surface"])

    bars = ax.bar(
        range(len(df)),
        df.get("total_mm", df.get("actual_amount_mm", [])),
        color=COLORS["primary"],
        edgecolor="white",
        linewidth=0.5,
        width=0.7,
        zorder=3,
    )

    # Value labels on bars
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3, f"{h:.1f}",
                    ha="center", va="bottom", fontsize=8, color=COLORS["text"])

    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["date"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Water Used (mm)", fontsize=10, color=COLORS["text"])
    ax.set_title("Daily Water Usage Trend", fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    return _fig_to_base64(fig)


def generate_adherence_chart(adherence_data: Dict[str, Any]) -> str:
    """
    Matplotlib donut chart showing recommendation adherence.
    Returns base64-encoded PNG.
    """
    pct = adherence_data.get("adherence_percent", 0)
    labels = ["Followed", "Skipped"]
    sizes  = [pct, 100 - pct]
    colors = [COLORS["success"], COLORS["danger"]]
    explode = (0.03, 0)

    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor(COLORS["surface"])

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=140, explode=explode, pctdistance=0.82,
        textprops={"fontsize": 11, "color": COLORS["text"]},
    )
    for t in autotexts:
        t.set_fontweight("bold")

    # Donut hole
    circle = plt.Circle((0, 0), 0.65, fc=COLORS["surface"])
    ax.add_artist(circle)

    # Center text
    ax.text(0, 0.05, f"{pct:.0f}%", ha="center", va="center",
            fontsize=28, fontweight="bold", color=COLORS["primary"])
    ax.text(0, -0.12, "Adherence", ha="center", va="center",
            fontsize=10, color=COLORS["muted"])

    ax.set_title("Recommendation Adherence", fontsize=13, fontweight="bold",
                 color=COLORS["text"], pad=16)
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_moisture_chart(moisture_data: Dict[str, Any]) -> str:
    """
    Matplotlib line chart for soil moisture readings with rolling average.
    Returns base64-encoded PNG.
    """
    readings = moisture_data.get("readings", [])
    if not readings:
        return ""

    df = pd.DataFrame(readings)
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(COLORS["surface"])
    ax.set_facecolor(COLORS["surface"])

    x = range(len(df))
    ax.plot(x, df["moisture_percent"], marker="o", markersize=5, linewidth=2,
            color=COLORS["secondary"], label="Moisture %", zorder=3)
    ax.plot(x, df["rolling_avg"], linewidth=2, linestyle="--",
            color=COLORS["warning"], label="Rolling Avg", zorder=3)

    ax.fill_between(x, df["moisture_percent"], alpha=0.1, color=COLORS["secondary"])
    ax.set_xticks(x)
    ax.set_xticklabels(df["date_str"], rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("Soil Moisture (%)", fontsize=10, color=COLORS["text"])
    ax.set_title("Soil Moisture Trend", fontsize=13, fontweight="bold", color=COLORS["text"], pad=12)
    ax.legend(fontsize=9, framealpha=0.8)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return _fig_to_base64(fig)


# ═══════════════════════════════════════════════════════════════════════
# 5 · CHART GENERATION — PLOTLY (JSON for React frontend)
# ═══════════════════════════════════════════════════════════════════════

def generate_plotly_water_usage(usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Plotly figure as JSON dict — consumed by react-plotly.js.
    """
    if not usage_data:
        return {}

    df = pd.DataFrame(usage_data)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df.get("total_mm", df.get("actual_amount_mm", [])),
        marker_color=COLORS["primary"],
        name="Water Used (mm)",
        hovertemplate="<b>%{x}</b><br>%{y:.1f} mm<extra></extra>",
    ))
    fig.update_layout(
        title="Daily Water Usage",
        xaxis_title="Date",
        yaxis_title="Amount (mm)",
        template="plotly_white",
        height=400,
        margin=dict(t=50, b=40, l=50, r=20),
    )
    return fig.to_dict()


def generate_plotly_adherence(adherence_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Plotly donut chart as JSON dict.
    """
    pct = adherence_data.get("adherence_percent", 0)
    fig = go.Figure(go.Pie(
        labels=["Followed", "Skipped"],
        values=[pct, 100 - pct],
        hole=0.6,
        marker=dict(colors=[COLORS["success"], COLORS["danger"]]),
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        title="Recommendation Adherence",
        template="plotly_white",
        height=350,
        margin=dict(t=50, b=20, l=20, r=20),
        annotations=[dict(
            text=f"{pct:.0f}%", x=0.5, y=0.5,
            font_size=28, font_color=COLORS["primary"],
            showarrow=False,
        )],
    )
    return fig.to_dict()


def generate_plotly_moisture(moisture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Plotly line + scatter chart for moisture trend.
    """
    readings = moisture_data.get("readings", [])
    if not readings:
        return {}

    df = pd.DataFrame(readings)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date_str"], y=df["moisture_percent"],
        mode="lines+markers", name="Moisture %",
        marker=dict(size=6, color=COLORS["secondary"]),
        line=dict(width=2, color=COLORS["secondary"]),
    ))
    fig.add_trace(go.Scatter(
        x=df["date_str"], y=df["rolling_avg"],
        mode="lines", name="Rolling Avg",
        line=dict(width=2, dash="dash", color=COLORS["warning"]),
    ))
    fig.update_layout(
        title="Soil Moisture Trend",
        xaxis_title="Time",
        yaxis_title="Moisture (%)",
        template="plotly_white",
        height=400,
        margin=dict(t=50, b=60, l=50, r=20),
    )
    return fig.to_dict()
