from typing import Dict, List


class PhaseBEvidenceService:
    """
    Combines Phase-B source-zone, source-time, AIS proximity,
    and trajectory evidence into a normalized vessel score.
    """

    def __init__(
        self,
        spatial_weight: float = 0.40,
        temporal_weight: float = 0.20,
        proximity_weight: float = 0.25,
        trajectory_weight: float = 0.15,
    ):
        weights = [
            spatial_weight,
            temporal_weight,
            proximity_weight,
            trajectory_weight,
        ]

        if any(weight < 0 for weight in weights):
            raise ValueError("Evidence weights cannot be negative")

        total = sum(weights)

        if total <= 0:
            raise ValueError("At least one evidence weight is required")

        self.weights = {
            "spatial": spatial_weight / total,
            "temporal": temporal_weight / total,
            "proximity": proximity_weight / total,
            "trajectory": trajectory_weight / total,
        }

    @staticmethod
    def _distance_score(distance_km: float) -> float:
        """
        Convert source distance into a [0,1] score.
        """

        if distance_km < 0:
            return 0.0

        return max(
            0.0,
            1.0 - (distance_km / 50.0),
        )

    @staticmethod
    def _time_score(time_difference_hours: float) -> float:
        """
        Convert source-time difference into a [0,1] score.
        """

        if time_difference_hours < 0:
            return 0.0

        return max(
            0.0,
            1.0 - (time_difference_hours / 6.0),
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def score_candidate(
        self,
        candidate: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Calculate the combined Phase-B evidence score.
        """

        distance_km = float(
            candidate.get(
                "distance_to_source_km",
                999.0,
            )
        )

        time_difference_hours = float(
            candidate.get(
                "time_difference_hours",
                999.0,
            )
        )

        spatial_score = self._distance_score(
            distance_km
        )

        temporal_score = self._time_score(
            time_difference_hours
        )

        proximity_score = spatial_score

        trajectory_score = self._clamp(
            float(
                candidate.get(
                    "trajectory_score",
                    0.0,
                )
            )
        )

        evidence_score = (
            self.weights["spatial"] * spatial_score
            + self.weights["temporal"] * temporal_score
            + self.weights["proximity"] * proximity_score
            + self.weights["trajectory"] * trajectory_score
        )

        result = dict(candidate)

        result["evidence"] = {
            "spatial_score": spatial_score,
            "temporal_score": temporal_score,
            "proximity_score": proximity_score,
            "trajectory_score": trajectory_score,
        }

        result["evidence_score"] = evidence_score

        return result

    def rank_candidates(
        self,
        candidates: List[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        """
        Score and rank all candidate vessels.
        """

        scored = [
            self.score_candidate(candidate)
            for candidate in candidates
        ]

        scored.sort(
            key=lambda item: item["evidence_score"],
            reverse=True,
        )

        for rank, candidate in enumerate(
            scored,
            start=1,
        ):
            candidate["evidence_rank"] = rank

        return scored


if __name__ == "__main__":
    print("\n===== PHASE B EVIDENCE FUSION TEST =====")

    candidates = [
        {
            "vessel_id": "SIM030012",
            "distance_to_source_km": 0.011,
            "time_difference_hours": 0.00,
            "trajectory_score": 0.90,
        },
        {
            "vessel_id": "SIM030013",
            "distance_to_source_km": 0.141,
            "time_difference_hours": 0.08,
            "trajectory_score": 0.65,
        },
        {
            "vessel_id": "SIM030015",
            "distance_to_source_km": 12.0,
            "time_difference_hours": 2.0,
            "trajectory_score": 0.30,
        },
    ]

    service = PhaseBEvidenceService()

    ranked = service.rank_candidates(
        candidates
    )

    print("\nRanked candidates:")

    for candidate in ranked:
        evidence = candidate["evidence"]

        print(
            f"\n  Rank {candidate['evidence_rank']}: "
            f"{candidate['vessel_id']}"
        )

        print(
            f"    Spatial    : "
            f"{evidence['spatial_score']:.3f}"
        )

        print(
            f"    Temporal   : "
            f"{evidence['temporal_score']:.3f}"
        )

        print(
            f"    Proximity  : "
            f"{evidence['proximity_score']:.3f}"
        )

        print(
            f"    Trajectory : "
            f"{evidence['trajectory_score']:.3f}"
        )

        print(
            f"    FINAL SCORE: "
            f"{candidate['evidence_score']:.3f}"
        )

    print("\n===== EVIDENCE FUSION TEST COMPLETE =====")