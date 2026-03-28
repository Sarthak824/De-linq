HISTORY_DB = {}


def add_to_history(customer_id, message):

    if customer_id not in HISTORY_DB:
        HISTORY_DB[customer_id] = []

    HISTORY_DB[customer_id].append(message)


def get_history(customer_id, k=1):

    history = HISTORY_DB.get(customer_id, [])

    return history[-k:]