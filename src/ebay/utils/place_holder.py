def is_placeholder_value(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        not normalized
        or normalized in {"select", "choose", "please select"}
        or normalized.startswith("select ")
        or normalized.startswith("choose ")
    )
