import os
import sys

# Ensure paths correctly resolve
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# VERY IMPORTANT: Load xgboost/torch BEFORE feast/pandas/pyarrow to prevent macOS segfault 11
from src.inference.predict import load_model, score_records
from src.api.app import CustomerFeatures

import json
import logging
from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
from feast import FeatureStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "customer_events"
OUTPUT_TOPIC = "risk_assessments"

# All features we need from the Feast Online Store
FEAST_FEATURES = [
    "customer_financial_profile:age", "customer_financial_profile:monthly_income",
    "customer_financial_profile:emi", "customer_financial_profile:credit_card_due",
    "customer_financial_profile:emi_to_income_ratio", "customer_financial_profile:credit_utilization",
    "customer_financial_profile:missed_payments", "customer_financial_profile:salary_delay",
    "customer_financial_profile:job_loss", "customer_financial_profile:avg_balance",
    "customer_financial_profile:balance_drop_ratio", "customer_financial_profile:atm_withdrawals",
    "customer_financial_profile:spending_change", "customer_financial_profile:bill_delay_count",
    "customer_financial_profile:account_tenure", "customer_financial_profile:total_obligations",
    "customer_financial_profile:debt_stress_ratio", "customer_financial_profile:liquidity_buffer",
    "customer_financial_profile:spending_instability", "customer_financial_profile:payment_discipline",
    "customer_financial_profile:financial_health_score", "customer_financial_profile:shock_flag",
    "customer_financial_profile:credit_dependency", "customer_financial_profile:early_risk_flag",
    "customer_financial_profile:stability_score"
]

def main():
    logger.info("Loading ML Model...")
    model = load_model()

    logger.info("Initializing Feast Feature Store...")
    store = FeatureStore(repo_path=os.path.join(BASE_DIR, "feature_repo"))

    logger.info(f"Connecting to Kafka at {KAFKA_BROKER}...")
    consumer = KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="risk-consumer-group",
    )

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    logger.info(f"Listening on topic: {INPUT_TOPIC}")

    for message in consumer:
        try:
            payload = message.value
            customer_id = payload.get("customer_id")
            
            if not customer_id:
                logger.warning("Received event without customer_id. Skipping.")
                continue
                
            logger.info(f"Received customer event for {customer_id}. Fetching features from Feast...")

            # 1. Fetch real-time feature dictionary from Feast Online Store (SQLite)
            feature_vector = store.get_online_features(
                features=FEAST_FEATURES,
                entity_rows=[{"customer_id": customer_id}]
            ).to_dict()
            
            # 2. Reconstruct payload matching exactly what the model expects
            customer_features_dict = {}
            for k, v in feature_vector.items():
                key_name = k.split('__')[-1] if '__' in k else k
                customer_features_dict[key_name] = v[0]
                
            customer_features_dict["customer_id"] = customer_id

            # 3. Predict
            predictions = score_records([customer_features_dict], model)
            result = predictions[0]

            # 4. Route to output topic for orchestrator
            producer.send(OUTPUT_TOPIC, value=result)
            logger.info(f"➜ Scored customer {customer_id}: Risk={result['risk_score']} - Action required!")

        except Exception as e:
            logger.error(f"Error processing record: {e}")

if __name__ == "__main__":
    main()
