def get_risk_band(risk_score):
    if risk_score < 0.35:
        return "Low"
    if risk_score < 0.70:
        return "Medium"
    return "High"


def generate_reason_codes(row):
    reasons = []

    if row["job_loss"] == 1:
        reasons.append("job_loss_signal")
    if row["salary_delay"] == 1:
        reasons.append("salary_delay_detected")
    if row["missed_payments"] >= 2:
        reasons.append("missed_payments")
    if row["bill_delay_count"] >= 2:
        reasons.append("late_bill_payments")
    if row["credit_utilization"] >= 0.8:
        reasons.append("high_credit_utilization")
    if row["emi_to_income_ratio"] >= 0.45 or row["debt_stress_ratio"] >= 0.65:
        reasons.append("high_emi_burden")
    if row["balance_drop_ratio"] >= 0.35:
        reasons.append("balance_drawdown")
    if row["liquidity_buffer"] <= 15000:
        reasons.append("low_liquidity_buffer")
    if row["shock_flag"] == 1:
        reasons.append("financial_shock_detected")

    if not reasons:
        reasons.append("stable_payment_behavior")

    return reasons[:3]


def recommend_intervention(row, risk_score):
    policy_action = row.get("policy_action")

    if policy_action == "gentle_reminder" or policy_action == "payment_reminder":
        return "Send payment reminder"
    if policy_action == "immediate_support_review":
        return "Offer immediate support"
    if policy_action == "flexible_payment_review":
        return "Offer flexible payment plan"
    if policy_action == "flexible_payment_window":
        return "Offer flexible payment window"
    if policy_action == "dynamic_emi_review":
        return "Review dynamic EMI adjustment"
    if policy_action == "temporary_relief_review":
        return "Offer temporary payment relief"
    if policy_action == "grace_period_offer":
        return "Offer short grace period"
    if policy_action == "proactive_check_in":
        return "Offer proactive check-in"
    if policy_action == "assisted_support_outreach":
        return "Escalate to assisted support"
    if policy_action == "emi_restructure_review":
        return "Offer EMI restructuring"
    if policy_action == "repayment_support_plan":
        return "Offer proactive repayment support"

    risk_band = get_risk_band(risk_score)
    if risk_band == "Low":
        return "Send payment reminder"
    if risk_band == "Medium":
        return "Offer proactive check-in"
    return "Offer proactive repayment support"


def enrich_customer_decision(row, risk_score):
    row_data = row.to_dict()
    row_data["low_liquidity_buffer_flag"] = int(row["liquidity_buffer"] <= 15000)

    reasons = generate_reason_codes(row_data)
    risk_band = get_risk_band(risk_score)
    intervention = recommend_intervention(row_data, risk_score)

    return {
        "risk_band": risk_band,
        "top_reason_codes": reasons,
        "recommended_intervention": intervention,
    }
