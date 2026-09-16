from datetime import datetime, timezone
from typing import Dict, List


class AlertService:
    """
    Generates a structured backend alert from Phase-B
    evidence-fusion results.

    This service does not modify the frontend.
    """

    def __init__(
        self,
        high_threshold: float = 0.85,
        medium_threshold: float = 0.65,
    ):
        if not 0.0 <= medium_threshold <= 1.0:
            raise ValueError(
                "medium_threshold must be between 0 and 1"
            )

        if not 0.0 <= high_threshold <= 1.0:
            raise ValueError(
                "high_threshold must be between 0 and 1"
            )

        if medium_threshold > high_threshold:
            raise ValueError(
                "medium_threshold cannot exceed high_threshold"
            )

        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def _severity(self, score: float) -> str:
        if score >= self.high_threshold:
            return "HIGH"

        if score >= self.medium_threshold:
            return "MEDIUM"

        return "LOW"

    def create_alert(
        self,
        spill_detected: bool,
        confidence: float,
        latitude: float,
        longitude: float,
        timestamp: str,
        ranked_candidates: List[Dict[str, object]],
    ) -> Dict[str, object]:
        """
        Create the structured alert response.
        """

        confidence = max(
            0.0,
            min(1.0, float(confidence)),
        )

        if not spill_detected:
            return {
                "active": False,
                "severity": "NONE",
                "type": "NO_OIL_SPILL_DETECTED",
                "title": "No Oil Spill Detected",
                "message": (
                    "The analysis did not detect a confirmed "
                    "oil spill."
                ),
                "confidence": confidence,
                "timestamp": timestamp,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "candidate_vessels": [],
            }

        severity = self._severity(confidence)

        if severity == "HIGH":
            title = "Potential Oil Spill Detected"
            message = (
                "A high-confidence potential oil spill has "
                "been detected."
            )
        elif severity == "MEDIUM":
            title = "Possible Oil Spill Detected"
            message = (
                "A potential oil spill has been detected "
                "with moderate confidence."
            )
        else:
            title = "Low-Confidence Spill Detection"
            message = (
                "A possible oil spill has been detected, "
                "but confidence is low."
            )

        candidate_vessels = []

        for candidate in ranked_candidates:
            candidate_vessels.append(
                {
                    "rank": candidate.get(
                        "evidence_rank",
                        candidate.get("rank"),
                    ),
                    "vessel_id": candidate.get(
                        "vessel_id"
                    ),
                    "evidence_score": candidate.get(
                        "evidence_score",
                        0.0,
                    ),
                    "distance_to_source_km": candidate.get(
                        "distance_to_source_km"
                    ),
                    "time_difference_hours": candidate.get(
                        "time_difference_hours"
                    ),
                }
            )

        return {
            "active": True,
            "severity": severity,
            "type": "OIL_SPILL_DETECTED",
            "title": title,
            "message": message,
            "confidence": confidence,
            "timestamp": timestamp,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "candidate_vessels": candidate_vessels,
        }


if __name__ == "__main__":
    print("\n===== PHASE B ALERT SERVICE TEST =====")

    service = AlertService()

    ranked_candidates = [
        {
            "evidence_rank": 1,
            "vessel_id": "SIM030012",
            "evidence_score": 0.985,
            "distance_to_source_km": 0.011,
            "time_difference_hours": 0.00,
        },
        {
            "evidence_rank": 2,
            "vessel_id": "SIM030013",
            "evidence_score": 0.943,
            "distance_to_source_km": 0.141,
            "time_difference_hours": 0.08,
        },
    ]

    alert = service.create_alert(
        spill_detected=True,
        confidence=0.93,
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:20:00Z",
        ranked_candidates=ranked_candidates,
    )

    print("\nAlert:")

    print(
        f"  Active     : "
        f"{alert['active']}"
    )

    print(
        f"  Severity   : "
        f"{alert['severity']}"
    )

    print(
        f"  Type       : "
        f"{alert['type']}"
    )

    print(
        f"  Title      : "
        f"{alert['title']}"
    )

    print(
        f"  Confidence : "
        f"{alert['confidence']:.2f}"
    )

    print(
        f"  Location   : "
        f"{alert['location']['latitude']:.6f}, "
        f"{alert['location']['longitude']:.6f}"
    )

    print("\nCandidate vessels:")

    for candidate in alert["candidate_vessels"]:
        print(
            f"  Rank {candidate['rank']}: "
            f"{candidate['vessel_id']} "
            f"(score="
            f"{candidate['evidence_score']:.3f})"
        )

    print("\n===== ALERT SERVICE TEST COMPLETE =====")
