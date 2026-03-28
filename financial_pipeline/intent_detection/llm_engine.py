import ollama
import json
import re


VALID = [
    "stress",
    "promise",
    "angry",
    "negotiation",
    "paid",
    "no_response",
    "unknown"
]


def extract_json(text):

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group())
    except:
        return None


def run_llm(prompt):

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response["message"]["content"]

    data = extract_json(text)

    if not data:
        return {
            "intent": "unknown",
            "emotion": "unknown",
            "risk": "unknown"
        }

    if data.get("intent") not in VALID:
        data["intent"] = "unknown"

    return data