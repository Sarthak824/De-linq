def select_policy_decision(row):
    risk_band = row.get("risk_band", "Medium")
    intent_label = row.get("intent_label", "stable")
    persona_label = row.get("persona_label", "Moderate User")
    financial_stress_level = row.get("financial_stress_level", "Moderate")

    if risk_band == "Low":
        return {
            "policy_action": "gentle_reminder",
            "policy_priority": "low",
            "recommended_channel": "App",
        }

    if risk_band == "Medium":
        if intent_label == "willing_but_stressed":
            return {
                "policy_action": "grace_period_offer",
                "policy_priority": "medium",
                "recommended_channel": "WhatsApp",
            }
        if persona_label == "High Lifestyle Spender":
            return {
                "policy_action": "proactive_check_in",
                "policy_priority": "medium",
                "recommended_channel": "App",
            }
        return {
            "policy_action": "payment_reminder",
            "policy_priority": "medium",
            "recommended_channel": "SMS",
        }

    if intent_label == "disengaged":
        return {
            "policy_action": "assisted_support_outreach",
            "policy_priority": "high",
            "recommended_channel": "SMS",
        }
    if intent_label == "high_distress" or financial_stress_level == "High":
        return {
            "policy_action": "emi_restructure_review",
            "policy_priority": "critical",
            "recommended_channel": "WhatsApp",
        }
    return {
        "policy_action": "repayment_support_plan",
        "policy_priority": "high",
        "recommended_channel": "App",
    }


def apply_policy_engine(df):
    working_df = df.copy()
    policy_df = working_df.apply(select_policy_decision, axis=1, result_type="expand")
    return working_df.join(policy_df)
