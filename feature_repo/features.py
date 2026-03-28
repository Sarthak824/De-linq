from datetime import timedelta
from feast import Entity, FeatureView, FileSource, Field
from feast.types import Float32, Int32, String

# Connect to our Parquet data source
customer_source = FileSource(
    name="customer_stats_source",
    path="/Users/Hp/Documents/De-linq/data/processed/final_cleaned.parquet",
    timestamp_field="event_timestamp",
)

# Define the entity (Primary Key)
customer = Entity(name="customer", join_keys=["customer_id"])

# Define the Feature View that pulls all fields needed by XGBoost
customer_stats_fv = FeatureView(
    name="customer_financial_profile",
    entities=[customer],
    ttl=timedelta(days=3650), # How far back to look for data
    schema=[
        Field(name="age", dtype=Int32),
        Field(name="monthly_income", dtype=Float32),
        Field(name="emi", dtype=Float32),
        Field(name="credit_card_due", dtype=Float32),
        Field(name="emi_to_income_ratio", dtype=Float32),
        Field(name="credit_utilization", dtype=Float32),
        Field(name="missed_payments", dtype=Int32),
        Field(name="salary_delay", dtype=Int32),
        Field(name="job_loss", dtype=Int32),
        Field(name="avg_balance", dtype=Float32),
        Field(name="balance_drop_ratio", dtype=Float32),
        Field(name="atm_withdrawals", dtype=Int32),
        Field(name="spending_change", dtype=Float32),
        Field(name="bill_delay_count", dtype=Int32),
        Field(name="account_tenure", dtype=Int32),
        Field(name="total_obligations", dtype=Float32),
        Field(name="debt_stress_ratio", dtype=Float32),
        Field(name="liquidity_buffer", dtype=Float32),
        Field(name="spending_instability", dtype=Float32),
        Field(name="payment_discipline", dtype=Float32),
        Field(name="financial_health_score", dtype=Float32),
        Field(name="shock_flag", dtype=Int32),
        Field(name="credit_dependency", dtype=Float32),
        Field(name="early_risk_flag", dtype=Int32),
        Field(name="stability_score", dtype=Float32),
    ],
    source=customer_source,
    online=True,
)
