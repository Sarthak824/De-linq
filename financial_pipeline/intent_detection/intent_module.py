from config import SCHEMA_CONFIG
from schema_mapper import map_schema
from retriever import retrieve_context
from prompt_builder import build_prompt
from llm_engine import run_llm
from memory import add_to_history, get_history


def intent_detection(row):

    data = map_schema(row, SCHEMA_CONFIG)

    text = data["text"]
    features = data["features"]

    customer_id = row.get("customer_id", 0)

    history = get_history(customer_id)

    context = retrieve_context(text)

    prompt = build_prompt(
        text,
        context,
        history,
        features
    )

    output = run_llm(prompt)

    add_to_history(customer_id, text)

    return output