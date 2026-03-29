"""
Cash Flow Reliability Score (CRS) Engine
=========================================
Post-inference enrichment layer for gig-economy workers who lack a fixed salary.

CRS = 0.30·C + 0.25·R + 0.20·F + 0.15·V + 0.10·D

Components
----------
C  — Consistency   : active_earning_days / total_days
R  — Recovery      : 1 / (1 + avg_earning_gap_days)
F  — Income Floor  : min_weekly_income / avg_weekly_income
V  — Volatility    : 1 − (income_std / monthly_income)   [clipped to [0, 1]]
D  — Diversification : income_sources / MAX_INCOME_SOURCES

CRS Bands
---------
≥ 0.75  →  Reliable   — best loan terms
0.50–0.75 → Moderate  — controlled lending
< 0.50  →  Risky      — safeguards triggered
"""

import numpy as np
import pandas as pd

# ── Weights ──────────────────────────────────────────────────────────────────
W_CONSISTENCY = 0.30
W_RECOVERY = 0.25
W_FLOOR = 0.20
W_VOLATILITY = 0.15
W_DIVERSIFICATION = 0.10

MAX_INCOME_SOURCES = 4

# ── Band thresholds ───────────────────────────────────────────────────────────
CRS_RELIABLE_THRESHOLD = 0.75
CRS_MODERATE_THRESHOLD = 0.50


def _safe(value, default=0.0):
    """Return *value* as float, falling back to *default* if missing/NaN."""
    if value is None:
        return float(default)
    try:
        fv = float(value)
        return default if np.isnan(fv) else fv
    except (TypeError, ValueError):
        return float(default)


def _crs_band(score: float) -> str:
    if score >= CRS_RELIABLE_THRESHOLD:
        return "Reliable"
    if score >= CRS_MODERATE_THRESHOLD:
        return "Moderate"
    return "Risky"


# ── Single-row computation ────────────────────────────────────────────────────

def compute_crs(row) -> dict:
    """
    Compute CRS for a single customer row (dict or Series).

    Returns a dict with keys:
        crs_c, crs_r, crs_f, crs_v, crs_d, crs_score, crs_band
    """
    row = dict(row) if not isinstance(row, dict) else row

    # ── C: Consistency ────────────────────────────────────────────────────────
    active_days = _safe(row.get("active_earning_days"), 22)
    total_days = _safe(row.get("total_days"), 30)
    total_days = max(total_days, 1.0)
    crs_c = float(np.clip(active_days / total_days, 0.0, 1.0))

    # ── R: Recovery ───────────────────────────────────────────────────────────
    avg_gap = _safe(row.get("avg_earning_gap_days"), 3)
    crs_r = float(1.0 / (1.0 + avg_gap))

    # ── F: Income Floor ───────────────────────────────────────────────────────
    min_weekly = _safe(row.get("min_weekly_income"), 0)
    avg_weekly = _safe(row.get("avg_weekly_income"), 1)
    avg_weekly = max(avg_weekly, 1.0)
    crs_f = float(np.clip(min_weekly / avg_weekly, 0.0, 1.0))

    # ── V: Volatility (stability) ─────────────────────────────────────────────
    income_std = _safe(row.get("income_std"), 0)
    monthly_income = _safe(row.get("monthly_income"), 1)
    monthly_income = max(monthly_income, 1.0)
    crs_v = float(np.clip(1.0 - (income_std / monthly_income), 0.0, 1.0))

    # ── D: Diversification ────────────────────────────────────────────────────
    sources = _safe(row.get("income_sources"), 1)
    crs_d = float(np.clip(sources / MAX_INCOME_SOURCES, 0.0, 1.0))

    # ── Final score ───────────────────────────────────────────────────────────
    crs_score = round(
        W_CONSISTENCY * crs_c
        + W_RECOVERY * crs_r
        + W_FLOOR * crs_f
        + W_VOLATILITY * crs_v
        + W_DIVERSIFICATION * crs_d,
        4,
    )

    return {
        "crs_c": round(crs_c, 4),
        "crs_r": round(crs_r, 4),
        "crs_f": round(crs_f, 4),
        "crs_v": round(crs_v, 4),
        "crs_d": round(crs_d, 4),
        "crs_score": crs_score,
        "crs_band": _crs_band(crs_score),
    }


# ── Batch computation (vectorised) ────────────────────────────────────────────

def batch_compute_crs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add CRS columns to *df* in-place (returns the mutated DataFrame).

    New columns: crs_c, crs_r, crs_f, crs_v, crs_d, crs_score, crs_band
    """
    total_days = df.get("total_days", pd.Series(30, index=df.index)).fillna(30).clip(lower=1)
    active_days = df.get("active_earning_days", pd.Series(22, index=df.index)).fillna(22)

    avg_gap = df.get("avg_earning_gap_days", pd.Series(3, index=df.index)).fillna(3)

    min_weekly = df.get("min_weekly_income", pd.Series(0, index=df.index)).fillna(0)
    avg_weekly = df.get("avg_weekly_income", pd.Series(1, index=df.index)).fillna(1).clip(lower=1)

    income_std = df.get("income_std", pd.Series(0, index=df.index)).fillna(0)
    monthly_income = df["monthly_income"].fillna(1).clip(lower=1)

    sources = df.get("income_sources", pd.Series(1, index=df.index)).fillna(1)

    # Helper to safely get a Series from the DataFrame
    def _col(key, fallback):
        if key in df.columns:
            return df[key].fillna(fallback)
        return pd.Series(fallback, index=df.index)

    crs_c = (active_days / total_days).clip(0, 1)
    crs_r = 1.0 / (1.0 + avg_gap)
    crs_f = (min_weekly / avg_weekly).clip(0, 1)
    crs_v = (1.0 - (income_std / monthly_income)).clip(0, 1)
    crs_d = (sources / MAX_INCOME_SOURCES).clip(0, 1)

    crs_score = (
        W_CONSISTENCY * crs_c
        + W_RECOVERY * crs_r
        + W_FLOOR * crs_f
        + W_VOLATILITY * crs_v
        + W_DIVERSIFICATION * crs_d
    ).round(4)

    df = df.copy()
    df["crs_c"] = crs_c.round(4)
    df["crs_r"] = crs_r.round(4)
    df["crs_f"] = crs_f.round(4)
    df["crs_v"] = crs_v.round(4)
    df["crs_d"] = crs_d.round(4)
    df["crs_score"] = crs_score
    df["crs_band"] = crs_score.apply(_crs_band)

    return df
