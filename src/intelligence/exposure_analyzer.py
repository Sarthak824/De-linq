import pandas as pd


def analyze_exposure(row):
    """
    Evaluates how heavy and risky a user's debt structure is.
    Identifying fragile users due to high debt even before stress starts.
    """
    active_loans = row.get("active_loans", 0)
    personal_loans = row.get("personal_loans", 0)
    gold_loans = row.get("gold_loans", 0)
    secured_loans = row.get("secured_loans", 0)
    emi_ratio = row.get("emi_to_income_ratio", 0)
    utilization = row.get("credit_utilization", 0)
    top_up = row.get("loan_top_up_indicator", 0)
    exposure_score = row.get("credit_exposure_score", 0)

    # Classification logic
    if exposure_score >= 0.7 or (personal_loans >= 3 and emi_ratio >= 0.45):
        level = "High"
        message = "High exposure due to multiple unsecured personal loans and heavy EMI burden."
    elif exposure_score >= 0.4 or top_up == 1 or active_loans >= 3:
        level = "Moderate"
        message = "Moderate exposure; monitor for top-up usage and increasing loan count."
    else:
        level = "Low"
        message = "Stable credit structure with manageable loan exposure."

    # Insights on structure
    structure = "Secured" if secured_loans >= personal_loans else "Unsecured-Heavy"
    
    return {
        "credit_exposure_level": level,
        "credit_exposure_message": message,
        "debt_structure": structure,
        "active_loan_summary": f"{int(active_loans)} active ({int(secured_loans)}S, {int(personal_loans)}P, {int(gold_loans)}G)",
        "exposure_score": round(float(exposure_score), 2)
    }


def batch_analyze_exposure(df):
    results = df.apply(analyze_exposure, axis=1)
    results_df = pd.DataFrame(list(results), index=df.index)
    return pd.concat([df, results_df], axis=1)
