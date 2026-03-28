import os
import sys
import json
import logging
from kafka import KafkaConsumer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.interventions.orchestrator import trigger_intervention

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "risk_assessments"

def main():
    logger.info(f"Connecting to Kafka at {KAFKA_BROKER} to consume {INPUT_TOPIC}...")
    consumer = KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="intervention-consumer-group",
    )

    logger.info("Listening for high risk assessments...")

    for message in consumer:
        try:
            assessment = message.value
            customer_id = assessment.get("customer_id")
            risk_band = assessment.get("risk_band")
            risk_prediction = assessment.get("risk_prediction")

            # Only trigger interventions on actual "risk" prediction (e.g. 1 means high risk in this model)
            # or if recommended_intervention is not null/empty.
            if risk_prediction == 1:
                logger.info(f"[INTERVENTION] Customer {customer_id} is {risk_band}. Triggering intervention...")
                execution = trigger_intervention(assessment)
                logger.info(f"  -> Triggered {execution.recommended_intervention} via {execution.recommended_channel}")
            else:
                logger.debug(f"Customer {customer_id} is low risk. Skipping.")

        except Exception as e:
            logger.error(f"Error processing intervention: {e}")

if __name__ == "__main__":
    main()
