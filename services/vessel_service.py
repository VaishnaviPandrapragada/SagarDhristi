from typing import List, Dict, Optional


class VesselService:
    """
    Final vessel attribution service.

    Takes ranked vessel candidates from the
    BacktrackingService and produces a final
    source-vessel assessment.

    The service calculates:
        1. Attribution score
        2. Numeric confidence percentage
        3. Confidence level
        4. Final vessel ranking
    """

    def __init__(self):
        print("Vessel Service initialized.")

    # ========================================================
    # Calculate attribution score
    # ========================================================

    def calculate_score(
        self,
        distance_to_spill_km: float,
        predicted_movement_km: float,
        max_radius_km: float = 50.0
    ) -> float:
        """
        Calculate the attribution score.

        Smaller distance to the spill produces
        a higher score.

        Predicted movement is also considered.

        Score range:
            0.0 -> 1.0
        """

        # ----------------------------------------------------
        # Distance component
        # ----------------------------------------------------

        distance_score = max(
            0.0,
            1.0 -
            (
                distance_to_spill_km /
                max_radius_km
            )
        )

        # ----------------------------------------------------
        # Movement component
        # ----------------------------------------------------

        movement_score = min(
            predicted_movement_km / 1.0,
            1.0
        )

        # ----------------------------------------------------
        # Combined attribution score
        # ----------------------------------------------------

        score = (
            0.7 * distance_score
            +
            0.3 * movement_score
        )

        # Make sure score stays between 0 and 1

        score = max(
            0.0,
            min(1.0, score)
        )

        return float(score)

    # ========================================================
    # Convert score to percentage
    # ========================================================

    def confidence_percentage(
        self,
        score: float
    ) -> float:
        """
        Convert attribution score into a
        numeric confidence index.

        Example:
            0.751 -> 75.1
            0.726 -> 72.6
            0.685 -> 68.5

        IMPORTANT:
        This is a confidence index derived from
        the attribution score. It is NOT a
        statistically calibrated probability that
        the vessel caused the spill.
        """

        percentage = score * 100.0

        return round(
            percentage,
            2
        )

    # ========================================================
    # Assign confidence level
    # ========================================================

    def confidence_level(
        self,
        score: float
    ) -> str:
        """
        Convert attribution score into
        a qualitative confidence level.
        """

        if score >= 0.75:
            return "HIGH"

        elif score >= 0.50:
            return "MEDIUM"

        elif score >= 0.25:
            return "LOW"

        return "VERY LOW"

    # ========================================================
    # Process candidates
    # ========================================================

    def process_candidates(
        self,
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        Add attribution score, numeric confidence
        percentage, and confidence level to each
        candidate vessel.

        Candidates are then sorted by attribution
        score from highest to lowest.
        """

        processed = []

        for candidate in candidates:

            # ------------------------------------------------
            # Extract candidate information
            # ------------------------------------------------

            distance = float(
                candidate[
                    "distance_to_spill_km"
                ]
            )

            movement = float(
                candidate[
                    "predicted_movement_km"
                ]
            )

            # ------------------------------------------------
            # Calculate attribution score
            # ------------------------------------------------

            score = self.calculate_score(
                distance_to_spill_km=distance,
                predicted_movement_km=movement
            )

            # ------------------------------------------------
            # Calculate numeric confidence
            # ------------------------------------------------

            confidence_percentage = (
                self.confidence_percentage(
                    score
                )
            )

            # ------------------------------------------------
            # Calculate qualitative confidence
            # ------------------------------------------------

            confidence = self.confidence_level(
                score
            )

            # ------------------------------------------------
            # Create result
            # ------------------------------------------------

            result = candidate.copy()

            result[
                "attribution_score"
            ] = score

            result[
                "confidence_percentage"
            ] = confidence_percentage

            result[
                "confidence"
            ] = confidence

            processed.append(
                result
            )

        # ====================================================
        # Highest attribution score first
        # ====================================================

        processed.sort(
            key=lambda item:
                item["attribution_score"],
            reverse=True
        )

        # ====================================================
        # Assign final ranks
        # ====================================================

        for index, candidate in enumerate(
            processed
        ):

            candidate[
                "rank"
            ] = index + 1

            candidate[
                "source_vessel"
            ] = (
                index == 0
            )

        return processed

    # ========================================================
    # Select most likely vessel
    # ========================================================

    def identify_source_vessel(
        self,
        candidates: List[Dict]
    ) -> Optional[Dict]:
        """
        Select the vessel with the highest
        attribution score.
        """

        if not candidates:
            return None

        processed = self.process_candidates(
            candidates
        )

        source = processed[0].copy()

        source[
            "source_vessel"
        ] = True

        source[
            "rank"
        ] = 1

        return source

    # ========================================================
    # Generate final report
    # ========================================================

    def generate_report(
        self,
        candidates: List[Dict],
        spill_latitude: float,
        spill_longitude: float
    ) -> Dict:
        """
        Generate the final vessel attribution report.
        """

        processed = self.process_candidates(
            candidates
        )

        source = None

        if processed:

            source = processed[0].copy()

            source[
                "source_vessel"
            ] = True

            source[
                "rank"
            ] = 1

        return {
            "spill_location": {
                "latitude":
                    float(spill_latitude),

                "longitude":
                    float(spill_longitude)
            },

            "candidate_count":
                len(processed),

            "most_likely_source":
                source,

            "candidates":
                processed
        }


# ============================================================
# SINGLETON
# ============================================================

_vessel_service = None


def get_vessel_service():

    global _vessel_service

    if _vessel_service is None:

        _vessel_service = VesselService()

    return _vessel_service