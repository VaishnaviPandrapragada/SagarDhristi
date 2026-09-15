from datetime import datetime, timedelta, timezone
from typing import Dict


class SourceTimeService:
    """
    Estimates the probable oil-release time from an observed
    spill timestamp and a backward-hindcast lookback period.
    """

    def estimate_source_time(
        self,
        spill_timestamp: str,
        lookback_hours: float,
    ) -> Dict[str, object]:
        """
        Estimate the source time by moving backward from the
        observed spill time by the hindcast duration.
        """

        if lookback_hours < 0:
            raise ValueError("lookback_hours cannot be negative")

        observed_time = self._parse_timestamp(spill_timestamp)

        source_time = observed_time - timedelta(
            hours=lookback_hours
        )

        return {
            "observed_spill_time": observed_time.isoformat(),
            "estimated_source_time": source_time.isoformat(),
            "lookback_hours": float(lookback_hours),
            "confidence": self._calculate_confidence(
                lookback_hours
            ),
        }

    @staticmethod
    def _parse_timestamp(timestamp: str) -> datetime:
        """
        Parse an ISO-8601 timestamp and normalize it to UTC.
        """

        if not timestamp or not isinstance(timestamp, str):
            raise ValueError(
                "spill_timestamp must be a non-empty string"
            )

        normalized = timestamp.strip()

        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(
                "spill_timestamp must be a valid ISO-8601 timestamp"
            ) from exc

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _calculate_confidence(
        lookback_hours: float,
    ) -> str:
        """
        Assign a simple confidence category based on the
        length of the hindcast window.

        This is a model-development confidence indicator,
        not a statistical probability.
        """

        if lookback_hours <= 3.0:
            return "HIGH"

        if lookback_hours <= 6.0:
            return "MEDIUM"

        if lookback_hours <= 12.0:
            return "LOW"

        return "VERY_LOW"


if __name__ == "__main__":
    print("\n===== PHASE B SOURCE TIME TEST =====")

    service = SourceTimeService()

    result = service.estimate_source_time(
        spill_timestamp="2021-06-15T03:20:00Z",
        lookback_hours=6.0,
    )

    print("\nObserved spill time:")
    print(
        f"  {result['observed_spill_time']}"
    )

    print("\nEstimated source time:")
    print(
        f"  {result['estimated_source_time']}"
    )

    print("\nHindcast lookback:")
    print(
        f"  {result['lookback_hours']:.1f} hours"
    )

    print("\nTime-estimation confidence:")
    print(
        f"  {result['confidence']}"
    )

    print("\n===== SOURCE TIME TEST COMPLETE =====")