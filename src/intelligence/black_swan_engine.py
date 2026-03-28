import pandas as pd


SHOCK_CONFIG = {
    "income": {"income_drop_threshold": 0.5, "salary_loss_flag": 1},
    "balance": {"balance_drop_threshold": 0.4},
    "liquidity": {"withdrawal_spike_threshold": 10, "low_balance_threshold": 5000},
    "spending": {"spending_spike_threshold": 0.3},
    "risk_boost": {"low": 0.1, "moderate": 0.2, "high": 0.3},
}


def detect_income_shock(row, config=SHOCK_CONFIG):
    signals = []
    if row.get("job_loss", 0) == config["income"]["salary_loss_flag"]:
        signals.append("Job loss detected")
    if row.get("balance_drop_ratio", 0) > config["income"]["income_drop_threshold"]:
        signals.append("Income drop")
    return signals


def detect_balance_shock(row, config=SHOCK_CONFIG):
    if row.get("balance_drop_ratio", 0) > config["balance"]["balance_drop_threshold"]:
        return ["Sharp balance decline"]
    return []


def detect_liquidity_shock(row, config=SHOCK_CONFIG):
    signals = []
    if row.get("atm_withdrawals", 0) > config["liquidity"]["withdrawal_spike_threshold"]:
        signals.append("Withdrawal spike")
    if row.get("avg_balance", 0) < config["liquidity"]["low_balance_threshold"]:
        signals.append("Low balance")
    return signals


def detect_spending_shock(row, config=SHOCK_CONFIG):
    if row.get("spending_change", 0) > config["spending"]["spending_spike_threshold"]:
        return ["Spending spike"]
    return []


def analyze_black_swan_event(row, config=SHOCK_CONFIG):
    signals = []
    signals += detect_income_shock(row, config)
    signals += detect_balance_shock(row, config)
    signals += detect_liquidity_shock(row, config)
    signals += detect_spending_shock(row, config)

    score = len(signals)
    if score >= 3:
        severity = "High"
        intervention_hint = "Immediate support"
    elif score == 2:
        severity = "Moderate"
        intervention_hint = "Flexible payment"
    elif score == 1:
        severity = "Low"
        intervention_hint = "Reminder"
    else:
        severity = "None"
        intervention_hint = "No action"

    boosted_risk_score = row.get("risk_score", 0.5)
    if pd.isna(boosted_risk_score):
        boosted_risk_score = 0.5

    if severity == "High":
        boosted_risk_score = min(float(boosted_risk_score) + config["risk_boost"]["high"], 1.0)
    elif severity == "Moderate":
        boosted_risk_score = min(float(boosted_risk_score) + config["risk_boost"]["moderate"], 1.0)
    elif severity == "Low":
        boosted_risk_score = min(float(boosted_risk_score) + config["risk_boost"]["low"], 1.0)

    return {
        "shock_flag": int(score > 0),
        "shock_score": int(score),
        "shock_severity": severity,
        "shock_signals": signals if signals else ["No shock"],
        "shock_intervention_hint": intervention_hint,
        "risk_score_after_shock": round(float(boosted_risk_score), 4),
    }


def batch_analyze_black_swan(df):
    results = df.apply(analyze_black_swan_event, axis=1)
    results_df = pd.DataFrame(list(results), index=df.index)
    working_df = df.drop(columns=[column for column in results_df.columns if column in df.columns], errors="ignore")
    return pd.concat([working_df, results_df], axis=1)
