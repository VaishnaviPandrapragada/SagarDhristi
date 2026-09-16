def generate_alert(spill_detected, confidence):

    if not spill_detected:

        return {
            "active": False,
            "severity": "NONE",
            "type": "NO_SPILL",
            "message": "No potential oil spill detected"
        }

    if confidence >= 0.80:

        severity = "HIGH"

    elif confidence >= 0.50:

        severity = "MEDIUM"

    else:

        severity = "LOW"

    return {
        "active": True,
        "severity": severity,
        "type": "OIL_SPILL_DETECTED",
        "message": "Potential oil spill detected"
    }