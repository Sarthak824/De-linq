from intent_module import intent_detection


row1 = {
    "customer_id": "C1",
    "message": "I lost my job",
    "missed_payments": 2,
    "financial_health_score": 0.4,
    "shock_flag": 1,
    "debt_stress_ratio": 0.6,
    "emi_to_income_ratio": 0.5,
    "credit_utilization": 0.8,
    "early_risk_flag": 1,
    "stability_score": 0.3,
    "salary_delay": 1,
    "job_loss": 1
}


row2 = {
    "customer_id": "C1",
    "message": "I will pay later",
    "missed_payments": 1,
    "financial_health_score": 0.5,
    "shock_flag": 0,
    "debt_stress_ratio": 0.4,
    "emi_to_income_ratio": 0.3,
    "credit_utilization": 0.6,
    "early_risk_flag": 0,
    "stability_score": 0.5,
    "salary_delay": 0,
    "job_loss": 0
}


row3 = {
    "customer_id": "C1",
    "message": "I got salary today",
    "missed_payments": 0,
    "financial_health_score": 0.8,
    "shock_flag": 0,
    "debt_stress_ratio": 0.2,
    "emi_to_income_ratio": 0.2,
    "credit_utilization": 0.3,
    "early_risk_flag": 0,
    "stability_score": 0.9,
    "salary_delay": 0,
    "job_loss": 0
}


print(intent_detection(row1))
print(intent_detection(row2))
print(intent_detection(row3))