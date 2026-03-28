IMPORTANT_FEATURES = [
    "missed_payments",
    "financial_health_score",
    "shock_flag",
    "debt_stress_ratio",
    "emi_to_income_ratio",
    "credit_utilization",
    "early_risk_flag",
    "stability_score",
    "salary_delay",
    "job_loss",
]


def build_prompt(text, context, history, features):

    history_text = "\n".join(history)

    filtered = {
        k: features.get(k, None)
        for k in IMPORTANT_FEATURES
    }

    feature_text = "\n".join(
        [f"{k}: {v}" for k, v in filtered.items()]
    )

    prompt = f"""
You are a financial stress intelligence AI.

Use message, history, and financial features.

Allowed intents:
stress
promise
angry
negotiation
paid
no_response
unknown

Conversation history:
{history_text}

Message:
{text}

Financial indicators:
{feature_text}

Knowledge:
{context}

Return JSON only:

{{
"intent": "",
"emotion": "",
"risk": ""
}}
"""

    return prompt