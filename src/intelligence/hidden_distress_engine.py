import pandas as pd


def analyze_hidden_distress(row):
    """
    Detects how users cope with stress invisibly (informal borrowing, fragmented inflows).
    """
    p2p_count = row.get("p2p_inflow_count", 0)
    small_deposits = row.get("small_deposit_count", 0)
    emi_timing = row.get("days_before_emi_inflow", 0)
    informal_borrowing = row.get("informal_borrowing_indicator", 0)
    distress_score = row.get("hidden_distress_score", 0)

    # Classification logic
    if distress_score >= 0.7 or (informal_borrowing == 1 and emi_timing <= 2):
        level = "High"
        message = "Critical hidden distress; customer relies on last-minute informal borrowing for EMI."
    elif distress_score >= 0.4 or p2p_count >= 3 or small_deposits >= 5:
        level = "Moderate"
        message = "Moderate liquidity fragmentation; multiple small inflows detected before obligations."
    else:
        level = "Low"
        message = "Organic money movement; no signs of informal borrowing or patchwork liquidity."

    # Pattern identification
    if p2p_count >= 3:
        pattern = "P2P-Heavy"
    elif small_deposits >= 5:
        pattern = "Fragmented"
    else:
        pattern = "Stable"

    return {
        "hidden_distress_level": level,
        "hidden_distress_message": message,
        "liquidity_pattern": pattern,
        "patchwork_index": round(float(distress_score), 2),
        "emi_buffer_days": int(emi_timing)
    }


def batch_analyze_hidden_distress(df):
    results = df.apply(analyze_hidden_distress, axis=1)
    return pd.concat([df, pd.DataFrame(list(results))], axis=1)
