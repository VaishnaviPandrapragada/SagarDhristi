"""
Behavioural analysis service for SagarDhristi.

Detects interpretable vessel behaviour patterns from historical AIS data.

Important:
- Behaviour score is a heuristic evidence signal.
- It is NOT a probability of illegal activity or spill responsibility.
- An anomaly does not imply wrongdoing.
"""

from typing import Dict, List, Optional

import math
import pandas as pd


def _normalize_angle_difference(angle1: float, angle2: float) -> float:
    """
    Return the smallest absolute difference between two headings,
    in degrees.
    """
    difference = abs(float(angle1) - float(angle2))
    return min(difference, 360.0 - difference)


def calculate_speed_statistics(
    ais_history: pd.DataFrame,
) -> Dict[str, Optional[float]]:
    """
    Calculate basic speed statistics from AIS history.
    """

    if ais_history.empty or "sog_knots" not in ais_history.columns:
        return {
            "median_speed": None,
            "mean_speed": None,
            "speed_std": None,
        }

    speeds = pd.to_numeric(
        ais_history["sog_knots"],
        errors="coerce",
    ).dropna()

    if speeds.empty:
        return {
            "median_speed": None,
            "mean_speed": None,
            "speed_std": None,
        }

    return {
        "median_speed": float(speeds.median()),
        "mean_speed": float(speeds.mean()),
        "speed_std": float(speeds.std()) if len(speeds) > 1 else 0.0,
    }


def detect_speed_anomaly(
    ais_history: pd.DataFrame,
) -> Dict:
    """
    Detect unusually high or low vessel speed relative to
    the vessel's own historical behaviour.
    """

    if ais_history.empty or "sog_knots" not in ais_history.columns:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    speeds = pd.to_numeric(
        ais_history["sog_knots"],
        errors="coerce",
    ).dropna()

    if len(speeds) < 3:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    median_speed = float(speeds.median())
    std_speed = float(speeds.std())

    latest_speed = float(speeds.iloc[-1])

    # Avoid treating a stationary vessel as anomalous simply
    # because its historical speed variation is small.
    if std_speed < 0.25:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    z_score = abs(latest_speed - median_speed) / std_speed

    if z_score >= 2.0:
        score = min(1.0, z_score / 4.0)

        return {
            "detected": True,
            "score": round(score, 4),
            "reason": (
                f"Latest speed ({latest_speed:.2f} knots) "
                f"differs substantially from the vessel's "
                f"historical median ({median_speed:.2f} knots)."
            ),
        }

    return {
        "detected": False,
        "score": 0.0,
        "reason": None,
    }


def detect_sudden_slowdown(
    ais_history: pd.DataFrame,
) -> Dict:
    """
    Detect a substantial decrease in speed between consecutive
    AIS observations.
    """

    if ais_history.empty or "sog_knots" not in ais_history.columns:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    speeds = pd.to_numeric(
        ais_history["sog_knots"],
        errors="coerce",
    ).dropna()

    if len(speeds) < 2:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    previous_speed = float(speeds.iloc[-2])
    latest_speed = float(speeds.iloc[-1])

    slowdown = previous_speed - latest_speed

    # Prototype threshold.
    if slowdown >= 5.0:
        score = min(1.0, slowdown / 10.0)

        return {
            "detected": True,
            "score": round(score, 4),
            "reason": (
                f"Speed decreased by {slowdown:.2f} knots "
                f"between consecutive observations."
            ),
        }

    return {
        "detected": False,
        "score": 0.0,
        "reason": None,
    }


def detect_course_change(
    ais_history: pd.DataFrame,
) -> Dict:
    """
    Detect a large course change between consecutive AIS points.
    """

    if ais_history.empty or "cog" not in ais_history.columns:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    courses = pd.to_numeric(
        ais_history["cog"],
        errors="coerce",
    ).dropna()

    if len(courses) < 2:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    previous_course = float(courses.iloc[-2])
    latest_course = float(courses.iloc[-1])

    change = _normalize_angle_difference(
        previous_course,
        latest_course,
    )

    # Prototype threshold.
    if change >= 45.0:
        score = min(1.0, change / 180.0)

        return {
            "detected": True,
            "score": round(score, 4),
            "reason": (
                f"Course changed by {change:.1f} degrees "
                f"between consecutive observations."
            ),
        }

    return {
        "detected": False,
        "score": 0.0,
        "reason": None,
    }


def detect_ais_gap(
    ais_history: pd.DataFrame,
    gap_threshold_minutes: float = 30.0,
) -> Dict:
    """
    Detect unusually large gaps between AIS observations.
    """

    if ais_history.empty or "timestamp_utc" not in ais_history.columns:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    timestamps = pd.to_datetime(
        ais_history["timestamp_utc"],
        errors="coerce",
        utc=True,
    ).dropna().sort_values()

    if len(timestamps) < 2:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    gaps = timestamps.diff().dt.total_seconds() / 60.0
    largest_gap = float(gaps.max())

    if largest_gap >= gap_threshold_minutes:
        score = min(
            1.0,
            largest_gap / (gap_threshold_minutes * 4.0),
        )

        return {
            "detected": True,
            "score": round(score, 4),
            "reason": (
                f"Largest AIS reporting gap was "
                f"{largest_gap:.1f} minutes."
            ),
        }

    return {
        "detected": False,
        "score": 0.0,
        "reason": None,
    }


def detect_loitering(
    ais_history: pd.DataFrame,
) -> Dict:
    """
    Detect potential low-speed loitering.

    This is a simple prototype heuristic and should not be
    interpreted as evidence of wrongdoing.
    """

    if ais_history.empty or "sog_knots" not in ais_history.columns:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    speeds = pd.to_numeric(
        ais_history["sog_knots"],
        errors="coerce",
    ).dropna()

    if len(speeds) < 4:
        return {
            "detected": False,
            "score": 0.0,
            "reason": None,
        }

    low_speed_fraction = float(
        (speeds <= 2.0).mean()
    )

    if low_speed_fraction >= 0.70:
        score = min(1.0, low_speed_fraction)

        return {
            "detected": True,
            "score": round(score, 4),
            "reason": (
                f"{low_speed_fraction * 100:.1f}% of available "
                f"AIS observations show speeds at or below "
                f"2 knots."
            ),
        }

    return {
        "detected": False,
        "score": 0.0,
        "reason": None,
    }


def analyze_behaviour(
    ais_history: pd.DataFrame,
) -> Dict:
    """
    Run all behavioural checks and combine their results.
    """

    if ais_history is None or ais_history.empty:
        return {
            "behaviour_score": 0.0,
            "anomaly_count": 0,
            "anomalies": [],
            "explanations": [
                "No AIS history available for behavioural analysis."
            ],
        }

    checks = {
        "speed_anomaly": detect_speed_anomaly(ais_history),
        "sudden_slowdown": detect_sudden_slowdown(ais_history),
        "course_change": detect_course_change(ais_history),
        "ais_gap": detect_ais_gap(ais_history),
        "loitering": detect_loitering(ais_history),
    }

    detected = {
        name: result
        for name, result in checks.items()
        if result["detected"]
    }

    if not detected:
        return {
            "behaviour_score": 0.0,
            "anomaly_count": 0,
            "anomalies": [],
            "explanations": [
                "No prototype behavioural anomalies detected."
            ],
        }

    scores = [
        result["score"]
        for result in detected.values()
    ]

    # Use the strongest observed anomaly as the primary signal.
    behaviour_score = max(scores)

    explanations = [
        result["reason"]
        for result in detected.values()
        if result["reason"]
    ]

    return {
        "behaviour_score": round(
            float(behaviour_score),
            4,
        ),
        "anomaly_count": len(detected),
        "anomalies": list(detected.keys()),
        "explanations": explanations,
    }