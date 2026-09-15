"""
Evidence fusion service for SagarDhristi.

Combines multiple independent evidence signals for vessel attribution.

Important:
- The final score is a heuristic evidence score.
- It is NOT a probability of guilt or responsibility.
- Missing evidence is not treated as positive evidence.
"""


from typing import Dict, List, Optional


# Prototype weights.
# These are heuristic and should be validated/tuned later.
EVIDENCE_WEIGHTS = {
    "spatial": 0.25,
    "temporal": 0.20,
    "proximity": 0.15,
    "trajectory": 0.25,
    "behaviour": 0.15,
}


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Keep a numeric score inside the [0, 1] range."""
    return max(minimum, min(maximum, float(value)))


def normalize_distance(
    distance_km: Optional[float],
    max_distance_km: float = 50.0,
) -> Optional[float]:
    """
    Convert distance to a proximity score.

    0 km -> 1.0
    max_distance_km or more -> 0.0

    Returns None when distance is unavailable.
    """
    if distance_km is None:
        return None

    try:
        distance_km = float(distance_km)
    except (TypeError, ValueError):
        return None

    if distance_km < 0:
        return None

    return clamp(1.0 - (distance_km / max_distance_km))


def calculate_spatial_score(candidate: Dict) -> Optional[float]:
    """
    Calculate spatial consistency from the candidate's
    distance to the inferred source.

    Uses the candidate's existing distance field.
    """
    distance = candidate.get("distance_to_spill_km")

    if distance is None:
        distance = candidate.get("distance_to_source_km")

    return normalize_distance(distance)


def calculate_temporal_score(candidate: Dict) -> Optional[float]:
    """
    Calculate temporal consistency.

    If a future drift/source-time integration provides a
    temporal consistency value, use it.

    Otherwise return None rather than inventing evidence.
    """
    value = candidate.get("temporal_consistency")

    if value is None:
        value = candidate.get("temporal_score")

    if value is None:
        return None

    try:
        return clamp(float(value))
    except (TypeError, ValueError):
        return None


def calculate_proximity_score(candidate: Dict) -> Optional[float]:
    """
    Calculate proximity evidence.

    This is kept separate from spatial consistency so that
    future source-zone information can distinguish:
      - general spatial consistency
      - direct proximity to the inferred source zone
    """
    value = candidate.get("proximity_score")

    if value is not None:
        try:
            return clamp(float(value))
        except (TypeError, ValueError):
            pass

    distance = candidate.get("distance_to_source_km")

    if distance is not None:
        return normalize_distance(distance)

    return None


def calculate_trajectory_score(candidate: Dict) -> Optional[float]:
    """
    Calculate trajectory consistency from the existing RNN output.

    If the existing backtracking pipeline provides a movement
    consistency score, use it.

    Otherwise return None.
    """
    value = candidate.get("trajectory_score")

    if value is None:
        value = candidate.get("movement_score")

    if value is None:
        return None

    try:
        return clamp(float(value))
    except (TypeError, ValueError):
        return None


def calculate_behaviour_score(candidate: Dict) -> Optional[float]:
    """
    Read behavioural evidence when available.

    Behaviour analysis will be implemented as a separate service.
    Until then, missing behaviour is explicitly represented as None.
    """
    value = candidate.get("behaviour_score")

    if value is None:
        value = candidate.get("behavior_score")

    if value is None:
        return None

    try:
        return clamp(float(value))
    except (TypeError, ValueError):
        return None


def fuse_evidence(candidate: Dict) -> Dict:
    """
    Combine available evidence signals into one heuristic score.

    Only available evidence contributes to the score.
    The weights are renormalized across available signals.

    This prevents missing evidence from being incorrectly
    interpreted as zero evidence.
    """
    scores = {
        "spatial": calculate_spatial_score(candidate),
        "temporal": calculate_temporal_score(candidate),
        "proximity": calculate_proximity_score(candidate),
        "trajectory": calculate_trajectory_score(candidate),
        "behaviour": calculate_behaviour_score(candidate),
    }

    available = {
        name: score
        for name, score in scores.items()
        if score is not None
    }

    if not available:
        return {
            "evidence_score": 0.0,
            "evidence_level": "INSUFFICIENT",
            "signals": scores,
            "available_signal_count": 0,
            "explanations": [
                "Insufficient evidence signals available for fusion."
            ],
        }

    total_weight = sum(
        EVIDENCE_WEIGHTS[name]
        for name in available
    )

    weighted_score = sum(
        EVIDENCE_WEIGHTS[name] * score
        for name, score in available.items()
    )

    final_score = weighted_score / total_weight

    explanations = []

    if scores["spatial"] is not None:
        if scores["spatial"] >= 0.75:
            explanations.append(
                "Strong spatial consistency with the inferred source."
            )
        elif scores["spatial"] >= 0.50:
            explanations.append(
                "Moderate spatial consistency with the inferred source."
            )

    if scores["temporal"] is not None:
        if scores["temporal"] >= 0.75:
            explanations.append(
                "Strong temporal consistency with the source window."
            )
        elif scores["temporal"] >= 0.50:
            explanations.append(
                "Moderate temporal consistency with the source window."
            )

    if scores["trajectory"] is not None:
        if scores["trajectory"] >= 0.75:
            explanations.append(
                "Vessel trajectory is strongly consistent with the analysis."
            )
        elif scores["trajectory"] >= 0.50:
            explanations.append(
                "Vessel trajectory shows moderate consistency."
            )

    if scores["behaviour"] is not None:
        if scores["behaviour"] >= 0.75:
            explanations.append(
                "Behavioural evidence indicates notable anomalous activity."
            )
        elif scores["behaviour"] >= 0.50:
            explanations.append(
                "Some behavioural anomaly evidence is present."
            )

    if scores["proximity"] is not None and scores["proximity"] >= 0.75:
        explanations.append(
            "Vessel was in close proximity to the inferred source."
        )

    if not explanations:
        explanations.append(
            "Available evidence does not provide a strong positive signal."
        )

    if final_score >= 0.75:
        level = "HIGH"
    elif final_score >= 0.50:
        level = "MEDIUM"
    elif final_score >= 0.25:
        level = "LOW"
    else:
        level = "VERY LOW"

    return {
        "evidence_score": round(float(final_score), 4),
        "evidence_level": level,
        "signals": {
            name: (
                round(float(score), 4)
                if score is not None
                else None
            )
            for name, score in scores.items()
        },
        "available_signal_count": len(available),
        "explanations": explanations,
    }


def fuse_candidates(candidates: List[Dict]) -> List[Dict]:
    """
    Apply evidence fusion to a list of vessel candidates.

    Returns candidates sorted from highest evidence score
    to lowest.
    """
    results = []

    for candidate in candidates:
        result = candidate.copy()
        evidence = fuse_evidence(candidate)

        result["evidence"] = evidence
        result["evidence_score"] = evidence["evidence_score"]
        result["evidence_level"] = evidence["evidence_level"]
        result["evidence_explanations"] = evidence["explanations"]

        results.append(result)

    results.sort(
        key=lambda item: item["evidence_score"],
        reverse=True,
    )

    for index, candidate in enumerate(results, start=1):
        candidate["evidence_rank"] = index

    return results