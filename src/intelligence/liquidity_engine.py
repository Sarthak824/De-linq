import pandas as pd


def analyze_liquidity_stress(row):
    """
    Detects how users generate cash under pressure (FD breaks, fund liquidation, OD usage).
    """
    fd_break = row.get("fd_break_flag", 0)
    mf_amount = row.get("mf_liquidation_amount", 0)
    gold_loan = row.get("gold_loan_active", 0)
    od_util = row.get("od_utilization_pct", 0)
    stress_score = row.get("liquidity_stress_score", 0)

    # Classification logic
    if stress_score >= 0.7 or fd_break == 1:
        level = "Critical"
        message = "Severe asset depletion; customer is breaking fixed deposits to maintain liquidity."
    elif stress_score >= 0.4 or gold_loan == 1 or od_util >= 50:
        level = "High"
        message = "Heavy reliance on forced liquidity (Gold Loans/OD) to meet obligations."
    elif mf_amount > 50000:
        level = "Moderate"
        message = "Noticeable investment liquidation detected; monitoring depletion velocity."
    else:
        level = "Healthy"
        message = "Assets remain intact; no signs of forced liquidation or OD dependence."

    # Strategy identification
    if fd_break == 1:
        strategy = "Savings-Heavy"
    elif mf_amount > 0:
        strategy = "Asset-Depl"
    elif od_util > 50:
        strategy = "OD-Reliant"
    else:
        strategy = "Stable"

    return {
        "liquidity_stress_level": level,
        "liquidity_stress_message": message,
        "asset_depletion_strategy": strategy,
        "depletion_index": round(float(stress_score), 2),
        "od_usage_pct": round(float(od_util), 2)
    }


def batch_analyze_liquidity_stress(df):
    results = df.apply(analyze_liquidity_stress, axis=1)
    results_df = pd.DataFrame(list(results), index=df.index)
    return pd.concat([df, results_df], axis=1)
