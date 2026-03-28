def map_schema(row, config):

    text = row.get(config["text_field"], "")

    meta = {}

    for f in config.get("extra_fields", []):
        meta[f] = row.get(f, "")

    # everything else = features
    features = dict(row)

    return {
        "text": text,
        "meta": meta,
        "features": features
    }