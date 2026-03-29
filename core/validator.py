from typing import Any


REQUIRED_FIELDS = {
    "fire": ["fire_age", "corpus_needed", "monthly_sip_needed", "top_actions", "mentor_insight"],
    "health_score": ["overall_score", "grade", "dimensions", "mentor_insight"],
    "tax": ["recommended_regime", "old_regime", "new_regime", "missed_deductions", "mentor_insight"],
    "life_event": ["event_type", "immediate_actions", "allocation_plan", "mentor_insight"],
    "mf_xray": ["xirr", "overlap_score", "fund_breakdown", "rebalancing_plan", "mentor_insight"],
}

NUMERIC_RANGES = {
    "fire_age": (20, 80),
    "overall_score": (0, 100),
    "overlap_score": (0, 100),
    "xirr": (-1.0, 2.0),
}


def validate_ai_response(feature: str, data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        return {"valid": False, "errors": ["Empty response from AI"], "data": None}

    errors = []
    required = REQUIRED_FIELDS.get(feature, [])

    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    for field, (min_val, max_val) in NUMERIC_RANGES.items():
        if field in data and data[field] is not None:
            try:
                val = float(data[field])
                if not (min_val <= val <= max_val):
                    errors.append(f"Field {field} value {val} out of range [{min_val}, {max_val}]")
            except (TypeError, ValueError):
                errors.append(f"Field {field} is not numeric")

    if errors:
        return {"valid": False, "errors": errors, "data": data}

    return {"valid": True, "errors": [], "data": data}


def sanitize_response(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_response(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_response(i) if isinstance(i, dict) else i for i in value]
        elif isinstance(value, float):
            sanitized[key] = round(value, 4)
        elif isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized