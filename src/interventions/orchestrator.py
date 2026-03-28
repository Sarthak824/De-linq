import hashlib
import os
import uuid
from datetime import datetime, timezone

import pandas as pd
from src.storage.database import append_intervention_event, load_intervention_history as load_intervention_history_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
HISTORY_PATH = os.path.join(OUTPUT_DIR, "intervention_history.csv")

HISTORY_COLUMNS = [
    "execution_id",
    "customer_id",
    "triggered_at",
    "risk_score",
    "risk_band",
    "intent_label",
    "persona_label",
    "policy_action",
    "policy_priority",
    "recommended_channel",
    "recommended_intervention",
    "delivery_status",
]


def _current_timestamp():
    return datetime.now(timezone.utc).isoformat()


def _ensure_history_file():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        pd.DataFrame(columns=HISTORY_COLUMNS).to_csv(HISTORY_PATH, index=False)


def _simulate_delivery_status(customer_id, policy_action, channel):
    token = f"{customer_id}:{policy_action}:{channel}".encode("utf-8")
    bucket = int(hashlib.sha256(token).hexdigest(), 16) % 100

    if bucket < 6:
        return "failed"
    if bucket < 30:
        return "queued"
    if bucket < 82:
        return "sent"
    return "acknowledged"


def recommend_intervention_payload(prediction):
    return {
        "customer_id": prediction.get("customer_id"),
        "risk_score": prediction.get("risk_score"),
        "risk_band": prediction.get("risk_band"),
        "intent_label": prediction.get("intent_label"),
        "persona_label": prediction.get("persona_label"),
        "policy_action": prediction.get("policy_action"),
        "policy_priority": prediction.get("policy_priority"),
        "recommended_channel": prediction.get("recommended_channel"),
        "recommended_intervention": prediction.get("recommended_intervention"),
        "top_reason_codes": prediction.get("top_reason_codes", []),
    }


def trigger_intervention(prediction, override_channel=None, override_action=None):
    _ensure_history_file()

    customer_id = prediction.get("customer_id") or "UNKNOWN"
    policy_action = override_action or prediction.get("policy_action") or "payment_reminder"
    recommended_channel = override_channel or prediction.get("recommended_channel") or "App"
    recommended_intervention = prediction.get("recommended_intervention", "Send payment reminder")
    delivery_status = _simulate_delivery_status(customer_id, policy_action, recommended_channel)

    event = {
        "execution_id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "triggered_at": _current_timestamp(),
        "risk_score": prediction.get("risk_score"),
        "risk_band": prediction.get("risk_band"),
        "intent_label": prediction.get("intent_label"),
        "persona_label": prediction.get("persona_label"),
        "policy_action": policy_action,
        "policy_priority": prediction.get("policy_priority"),
        "recommended_channel": recommended_channel,
        "recommended_intervention": recommended_intervention,
        "delivery_status": delivery_status,
    }

    history_df = pd.read_csv(HISTORY_PATH)
    history_df = pd.concat([history_df, pd.DataFrame([event])], ignore_index=True)
    history_df.to_csv(HISTORY_PATH, index=False)
    append_intervention_event(event)

    return event


def get_intervention_history(customer_id):
    database_history_df = load_intervention_history_db(customer_id=customer_id)
    if not database_history_df.empty:
        records = database_history_df.to_dict(orient="records")
        for record in records:
            if pd.notna(record.get("risk_score")):
                record["risk_score"] = float(record["risk_score"])
        return records

    _ensure_history_file()
    history_df = pd.read_csv(HISTORY_PATH)
    filtered = history_df[history_df["customer_id"] == customer_id].copy()

    if filtered.empty:
        return []

    filtered = filtered.sort_values("triggered_at", ascending=False)
    records = filtered.to_dict(orient="records")

    for record in records:
        if pd.notna(record.get("risk_score")):
            record["risk_score"] = float(record["risk_score"])

    return records
