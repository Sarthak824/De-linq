import os
import json
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_FEATURES_PATH = os.path.join(BASE_DIR, "data", "processed", "features_advanced.csv")
DEFAULT_PREDICTIONS_PATH = os.path.join(BASE_DIR, "data", "output", "customer_risk_predictions.csv")
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
DEFAULT_OUTPUT_JSON = os.path.join(DEFAULT_OUTPUT_DIR, "personas.json")
DEFAULT_OUTPUT_CSV = os.path.join(DEFAULT_OUTPUT_DIR, "personas.csv")

PERSONA_CONFIG = {
    "risk_thresholds": {
        "high": 0.7,
        "moderate": 0.4,
    },
    "gig_worker": {
        "income_variability_threshold": 0.4,
        "salary_consistency_threshold": 0.5,
    },
}


def risk_level(row):
    score = row.get("risk_score", 0.5)
    if pd.isna(score): score = 0.5
    if score >= PERSONA_CONFIG["risk_thresholds"]["high"]: return "High"
    if score >= PERSONA_CONFIG["risk_thresholds"]["moderate"]: return "Moderate"
    return "Low"

def classify_spending(row):
    instability = row.get("spending_instability", 0)
    change = row.get("spending_change", 0)
    if pd.isna(instability): instability = 0
    if pd.isna(change): change = 0
    if instability > 0.4 or change > 0.2:
        return "Erratic Spending"
    inc = row.get("monthly_income", 0)
    if pd.isna(inc): inc = 0
    if inc > 100000 and change > 0.1:
        return "High Lifestyle Spender"
    return "Stable Spender"

def credit_dependency(row):
    util = row.get("credit_utilization", 0)
    if pd.isna(util): util = 0
    if util > 0.7: return "High"
    if util > 0.3: return "Moderate"
    return "Low"

def income_stability(row):
    delay = row.get("salary_delay", 0)
    loss = row.get("job_loss", 0)
    if pd.isna(delay): delay = 0
    if pd.isna(loss): loss = 0
    if delay > 0 or loss > 0:
        return "Unstable"
    return "Stable"

def derive_income_variability(row):
    income_std = row.get("income_std")
    monthly_income = row.get("monthly_income")
    if income_std is not None and monthly_income is not None and monthly_income > 0:
        return float(income_std) / float(monthly_income)

    change = row.get("spending_change", 0)
    if pd.isna(change):
        change = 0
    return abs(float(change))

def derive_salary_consistency(row):
    active_days = row.get("active_earning_days")
    if active_days is not None and not pd.isna(active_days):
        return float(active_days) / 30.0

    delay = row.get("salary_delay", 0)
    if pd.isna(delay):
        delay = 0

    clipped_delay = min(max(float(delay), 0.0), 1.0)
    return 1.0 - clipped_delay

def is_gig_worker(row):
    variability = row.get("income_variability", 0)
    consistency = row.get("salary_consistency", 1)

    if pd.isna(variability):
        variability = 0
    if pd.isna(consistency):
        consistency = 1

    income_sources = row.get("income_sources", 1)
    if pd.isna(income_sources): income_sources = 1

    # Identify as gig worker if they have multiple sources OR high variability/low consistency
    return (
        int(income_sources) > 1
        or (float(variability) > PERSONA_CONFIG["gig_worker"]["income_variability_threshold"]
            and float(consistency) < PERSONA_CONFIG["gig_worker"]["salary_consistency_threshold"])
    )

def stress_level(row):
    debt = row.get("debt_stress_ratio", 0)
    missed = row.get("missed_payments", 0)
    delay = row.get("bill_delay_count", 0)
    if pd.isna(debt): debt = 0
    if pd.isna(missed): missed = 0
    if pd.isna(delay): delay = 0
    if debt > 0.6 or missed > 0 or delay > 1:
        return "High"
    if debt > 0.4 or delay > 0:
        return "Moderate"
    return "Low"

def extract_signals(row):
    signals = []
    r_score = row.get("risk_score", 0.5)
    if pd.isna(r_score): r_score = 0.5
    if r_score >= 0.7: signals.append("High risk score detected")
    
    util = row.get("credit_utilization", 0)
    if pd.isna(util): util = 0
    if util > 0.7: signals.append("High credit utilization")
    
    instab = row.get("spending_instability", 0)
    if pd.isna(instab): instab = 0
    if instab > 0.4: signals.append("Erratic spending behavior")
    
    debt = row.get("debt_stress_ratio", 0)
    if pd.isna(debt): debt = 0
    if debt > 0.6: signals.append("High debt-to-income stress")
    
    missed = row.get("missed_payments", 0)
    if pd.isna(missed): missed = 0
    if missed > 0: signals.append(f"Missed {int(missed)} payments")
    
    delay = row.get("salary_delay", 0)
    if pd.isna(delay): delay = 0
    if delay > 0: signals.append("Recent salary delay")

    variability = row.get("income_variability", 0)
    if pd.isna(variability): variability = 0
    if variability > PERSONA_CONFIG["gig_worker"]["income_variability_threshold"]:
        signals.append("High income variability detected")

    consistency = row.get("salary_consistency", 1)
    if pd.isna(consistency): consistency = 1
    if consistency < PERSONA_CONFIG["gig_worker"]["salary_consistency_threshold"]:
        signals.append("Irregular salary pattern detected")
    
    crs_score = row.get("crs_score")
    if crs_score is not None and not pd.isna(crs_score):
        if crs_score < 0.5:
            signals.append(f"Low cash flow reliability (CRS: {crs_score})")
        elif crs_score < 0.75:
            signals.append(f"Borderline cash flow reliability (CRS: {crs_score})")

    exp_level = row.get("credit_exposure_level")
    if exp_level == "High":
        signals.append("High overall credit exposure")
    elif row.get("loan_top_up_indicator") == 1:
        signals.append("Loan top-up usage detected")
        
    distress_level = row.get("hidden_distress_level")
    if distress_level == "High":
        signals.append("Acute hidden distress detected")
    elif row.get("liquidity_pattern") == "P2P-Heavy":
        signals.append("Frequent P2P inflows detected")

    shock_severity = row.get("shock_severity")
    if shock_severity == "High":
        signals.append("Black swan shock event detected")
    elif shock_severity == "Moderate":
        signals.append("Moderate shock event detected")
    elif shock_severity == "Low":
        signals.append("Emerging shock signal detected")

    shock_signals = row.get("shock_signals", [])
    if isinstance(shock_signals, str):
        shock_signals = [item.strip() for item in shock_signals.split(",") if item.strip()]
    for signal in shock_signals:
        if signal and signal != "No shock" and signal not in signals:
            signals.append(signal)
        
    liq_level = row.get("liquidity_stress_level")
    if liq_level == "Critical":
        signals.append("Forced asset liquidation detected")
    elif row.get("asset_depletion_strategy") == "OD-Reliant":
        signals.append("Heavy overdraft usage detected")
    
    if not signals: signals.append("No immediate risk signals")
    return signals

def assign_persona(row):
    stress = row.get("financial_stress_level", "Moderate")
    credit = row.get("credit_dependency_level", "Moderate")
    spending = row.get("spending_behavior", "Stable Spender")
    risk = row.get("risk_level", "Moderate")

    if row.get("shock_severity") == "High":
        return "At-Risk Shocked User"
    if row.get("shock_severity") == "Moderate":
        return "Potentially Distressed User"

    if is_gig_worker(row):
        crs_band = row.get("crs_band")
        if crs_band == "Risky":
            return "Declining Gig Worker"
        if crs_band == "Moderate":
            return "Volatile Gig Worker"
        return "Stable Gig Worker"

    if row.get("hidden_distress_level") == "High":
        return "Distressed informal borrower"
    if row.get("liquidity_stress_level") == "Critical":
        return "Asset-Rich Stressed User"
    if stress == "High" and credit == "High":
        return "Credit Dependent Stressed User"
    if row.get("credit_exposure_level") == "High":
        return "Fragile Debt Holder"
    if spending == "Erratic Spending" and stress == "High":
        return "Impulse Spender Under Stress"
    if spending == "High Lifestyle Spender":
        return "High Lifestyle Spender"
    if stress == "Low" and risk == "Low":
        return "Stable Planner"
    return "Moderate User"

def build_persona(row_series):
    row = dict(row_series)
    row["risk_level"] = risk_level(row)
    row["spending_behavior"] = classify_spending(row)
    row["credit_dependency_level"] = credit_dependency(row)
    row["income_stability"] = income_stability(row)
    row["financial_stress_level"] = stress_level(row)
    row["income_variability"] = derive_income_variability(row)
    row["salary_consistency"] = derive_salary_consistency(row)
    
    row["persona_label"] = assign_persona(row)
    row["key_signals"] = extract_signals(row)
    
    score = row.get("risk_score")
    conf = 0.9 if score is not None and not pd.isna(score) else 0.7
    row["confidence_score"] = conf
    
    user_id = row.get("user_id")
    if pd.isna(user_id) or user_id is None:
        user_id = row.get("customer_id", "UNKNOWN")
        
    return {
        "customer_id": str(user_id),
        "risk_level": row["risk_level"],
        "spending_behavior": row["spending_behavior"],
        "income_stability": row["income_stability"],
        "credit_dependency_level": row["credit_dependency_level"],
        "financial_stress_level": row["financial_stress_level"],
        "persona_label": row["persona_label"],
        "confidence_score": row["confidence_score"],
        "key_signals": row["key_signals"]
    }

def generate_personas(df: pd.DataFrame) -> pd.DataFrame:
    df_working = df.copy()
    
    if "customer_id" not in df_working.columns and "user_id" in df_working.columns:
        df_working["customer_id"] = df_working["user_id"]
    
    if "risk_score" not in df_working.columns:
        df_working["risk_score"] = 0.5
        
    personas = []
    for _, row in df_working.iterrows():
        personas.append(build_persona(row))
        
    df_personas = pd.DataFrame(personas)
    
    df_working["persona_json"] = df_personas.apply(lambda x: dict(x), axis=1)
    df_working["persona_label"] = df_personas["persona_label"].values
    df_working["persona_signals"] = df_personas["key_signals"].apply(lambda items: ", ".join(items)).values
    df_working["financial_stress_level"] = df_personas["financial_stress_level"].values
    df_working["income_stability"] = df_personas["income_stability"].values
    df_working["spending_behavior"] = df_personas["spending_behavior"].values
    df_working["credit_dependency_level"] = df_personas["credit_dependency_level"].values
    df_working["confidence_score"] = df_personas["confidence_score"].values

    if "customer_id" not in df.columns and "customer_id" in df_working.columns:
        df["customer_id"] = df_working["customer_id"]
    df["persona_json"] = df_working["persona_json"].apply(json.dumps)
    df["persona_label"] = df_working["persona_label"]
    df["persona_signals"] = df_working["persona_signals"]
    df["financial_stress_level"] = df_working["financial_stress_level"]
    df["income_stability"] = df_working["income_stability"]
    df["spending_behavior"] = df_working["spending_behavior"]
    df["credit_dependency_level"] = df_working["credit_dependency_level"]
    df["persona_confidence_score"] = df_working["confidence_score"]
    if "risk_score" not in df:
        df["risk_score"] = df_working["risk_score"]
        
    return df

def merge_features_and_predictions(
    features_path=DEFAULT_FEATURES_PATH,
    predictions_path=DEFAULT_PREDICTIONS_PATH,
):
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features file not found: {features_path}")

    features_df = pd.read_csv(features_path)

    if os.path.exists(predictions_path):
        predictions_df = pd.read_csv(predictions_path)
        if "risk_score" in predictions_df.columns:
            features_df = features_df.merge(
                predictions_df[["customer_id", "risk_score"]],
                on="customer_id",
                how="left",
            )
        else:
            features_df["risk_score"] = 0.5
    else:
        features_df["risk_score"] = 0.5

    features_df["risk_score"] = features_df["risk_score"].fillna(0.5)
    return features_df


def run_persona_generation(
    features_path=DEFAULT_FEATURES_PATH,
    predictions_path=DEFAULT_PREDICTIONS_PATH,
    output_json_path=DEFAULT_OUTPUT_JSON,
    output_csv_path=DEFAULT_OUTPUT_CSV,
):
    merged_df = merge_features_and_predictions(
        features_path=features_path,
        predictions_path=predictions_path,
    )
    output_df = generate_personas(merged_df)

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    personas_list = [json.loads(value) for value in output_df["persona_json"]]
    with open(output_json_path, "w") as output_file:
        json.dump(personas_list, output_file, indent=4)

    pd.DataFrame(personas_list).to_csv(output_csv_path, index=False)

    print(f"✅ Personas generated: {len(output_df)}")
    print(f"📁 JSON saved to: {output_json_path}")
    print(f"📁 CSV saved to: {output_csv_path}")

    return output_df


if __name__ == "__main__":
    run_persona_generation()
