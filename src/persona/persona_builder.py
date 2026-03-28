import os
import json
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_FEATURES_PATH = os.path.join(BASE_DIR, "data", "processed", "features_advanced.csv")
DEFAULT_PREDICTIONS_PATH = os.path.join(BASE_DIR, "data", "output", "customer_risk_predictions.csv")
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
DEFAULT_OUTPUT_JSON = os.path.join(DEFAULT_OUTPUT_DIR, "personas.json")
DEFAULT_OUTPUT_CSV = os.path.join(DEFAULT_OUTPUT_DIR, "personas.csv")


def risk_level(row):
    score = row.get("risk_score", 0.5)
    if pd.isna(score): score = 0.5
    if score >= 0.7: return "High"
    if score >= 0.4: return "Moderate"
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
    
    exp_level = row.get("credit_exposure_level")
    if exp_level == "High":
        signals.append("High overall credit exposure")
    elif row.get("loan_top_up_indicator") == 1:
        signals.append("Loan top-up usage detected")
    
    if not signals: signals.append("No immediate risk signals")
    return signals

def assign_persona(row):
    stress = row.get("financial_stress_level", "Moderate")
    credit = row.get("credit_dependency", "Moderate")
    spending = row.get("spending_behavior", "Stable Spender")
    risk = row.get("risk_level", "Moderate")
    
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
