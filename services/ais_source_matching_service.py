from datetime import datetime, timedelta, timezone
from typing import Dict, List

import pandas as pd


class AISSourceMatchingService:
    """
    Matches historical AIS vessel positions against a probable
    oil-spill source zone and estimated source time.
    """

    def __init__(
        self,
        time_tolerance_hours: float = 1.0,
    ):
        if time_tolerance_hours < 0:
            raise ValueError(
                "time_tolerance_hours cannot be negative"
            )

        self.time_tolerance_hours = time_tolerance_hours

    @staticmethod
    def _parse_timestamp(timestamp: str) -> datetime:
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"

        parsed = datetime.fromisoformat(timestamp)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _find_column(
        dataframe: pd.DataFrame,
        candidates: List[str],
    ) -> str:
        """
        Find a column using case-insensitive matching.
        """

        lookup = {
            column.lower(): column
            for column in dataframe.columns
        }

        for candidate in candidates:
            if candidate.lower() in lookup:
                return lookup[candidate.lower()]

        raise ValueError(
            f"Could not find any of these columns: {candidates}"
        )

    @staticmethod
    def _distance_km(
        latitude_1: float,
        longitude_1: float,
        latitude_2: float,
        longitude_2: float,
    ) -> float:
        """
        Haversine distance in kilometres.
        """

        import math

        earth_radius_km = 6371.0

        lat1 = math.radians(latitude_1)
        lat2 = math.radians(latitude_2)

        delta_lat = math.radians(
            latitude_2 - latitude_1
        )

        delta_lon = math.radians(
            longitude_2 - longitude_1
        )

        a = (
            math.sin(delta_lat / 2.0) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2.0) ** 2
        )

        c = 2.0 * math.atan2(
            math.sqrt(a),
            math.sqrt(1.0 - a),
        )

        return earth_radius_km * c

    def match_vessels(
        self,
        dataframe: pd.DataFrame,
        source_zone: Dict[str, object],
        estimated_source_time: str,
    ) -> List[Dict[str, object]]:
        """
        Find AIS positions falling inside the probable source zone
        and close to the estimated source time.
        """

        latitude_column = self._find_column(
            dataframe,
            [
                "latitude",
                "lat",
                "LAT",
            ],
        )

        longitude_column = self._find_column(
            dataframe,
            [
                "longitude",
                "lon",
                "lng",
                "LON",
            ],
        )

        vessel_column = self._find_column(
            dataframe,
            [
                "mmsi",
                "MMSI",
                "vessel_id",
                "ship_id",
            ],
        )

        time_column = self._find_column(
            dataframe,
            [
                "timestamp",
                "datetime",
                "time",
                "BaseDateTime",
                "base_datetime",
                "base_date_time",
            ],
        )

        source_time = self._parse_timestamp(
            estimated_source_time
        )

        tolerance = timedelta(
            hours=self.time_tolerance_hours
        )

        start_time = source_time - tolerance
        end_time = source_time + tolerance

        working = dataframe.copy()

        working["_parsed_time"] = pd.to_datetime(
            working[time_column],
            utc=True,
            errors="coerce",
        )

        working[latitude_column] = pd.to_numeric(
            working[latitude_column],
            errors="coerce",
        )

        working[longitude_column] = pd.to_numeric(
            working[longitude_column],
            errors="coerce",
        )

        working = working.dropna(
            subset=[
                "_parsed_time",
                latitude_column,
                longitude_column,
            ]
        )

        working = working[
            (working["_parsed_time"] >= start_time)
            & (working["_parsed_time"] <= end_time)
        ]

        bounds = source_zone["bounds"]

        min_latitude = float(
            bounds["min_latitude"]
        )

        max_latitude = float(
            bounds["max_latitude"]
        )

        min_longitude = float(
            bounds["min_longitude"]
        )

        max_longitude = float(
            bounds["max_longitude"]
        )

        working = working[
            (working[latitude_column] >= min_latitude)
            & (working[latitude_column] <= max_latitude)
            & (working[longitude_column] >= min_longitude)
            & (working[longitude_column] <= max_longitude)
        ]

        if working.empty:
            return []

        center = source_zone["center"]

        center_latitude = float(
            center["latitude"]
        )

        center_longitude = float(
            center["longitude"]
        )

        candidates = []

        for _, row in working.iterrows():

            latitude = float(
                row[latitude_column]
            )

            longitude = float(
                row[longitude_column]
            )

            distance = self._distance_km(
                latitude,
                longitude,
                center_latitude,
                center_longitude,
            )

            time_difference = abs(
                (
                    row["_parsed_time"].to_pydatetime()
                    - source_time
                ).total_seconds()
            ) / 3600.0

            candidates.append(
                {
                    "vessel_id": str(
                        row[vessel_column]
                    ),
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": row[
                        "_parsed_time"
                    ].isoformat(),
                    "distance_to_source_km": distance,
                    "time_difference_hours": time_difference,
                }
            )

        candidates.sort(
            key=lambda item: (
                item["distance_to_source_km"],
                item["time_difference_hours"],
            )
        )

        best_by_vessel = {}

        for candidate in candidates:
            vessel_id = candidate["vessel_id"]

            if vessel_id not in best_by_vessel:
                best_by_vessel[vessel_id] = candidate

        results = list(
            best_by_vessel.values()
        )

        for rank, candidate in enumerate(
            results,
            start=1,
        ):
            candidate["rank"] = rank

        return results


if __name__ == "__main__":
    print("\n===== PHASE B AIS SOURCE MATCHING TEST =====")

    test_data = pd.DataFrame(
        [
            {
                "MMSI": "SIM030012",
                "LAT": -19.719000,
                "LON": 115.387000,
                "BaseDateTime": "2021-06-14T21:20:00Z",
            },
            {
                "MMSI": "SIM030013",
                "LAT": -19.720000,
                "LON": 115.388000,
                "BaseDateTime": "2021-06-14T21:15:00Z",
            },
            {
                "MMSI": "SIM030014",
                "LAT": -19.800000,
                "LON": 115.500000,
                "BaseDateTime": "2021-06-14T21:20:00Z",
            },
        ]
    )

    source_zone = {
        "center": {
            "latitude": -19.719071,
            "longitude": 115.387077,
        },
        "bounds": {
            "min_latitude": -19.723571,
            "max_latitude": -19.714571,
            "min_longitude": 115.382577,
            "max_longitude": 115.391577,
        },
    }

    service = AISSourceMatchingService(
        time_tolerance_hours=1.0
    )

    results = service.match_vessels(
        dataframe=test_data,
        source_zone=source_zone,
        estimated_source_time="2021-06-14T21:20:00Z",
    )

    print("\nEstimated source time:")
    print("  2021-06-14T21:20:00Z")

    print("\nMatched vessels:")

    for candidate in results:
        print(
            f"  Rank {candidate['rank']}: "
            f"{candidate['vessel_id']}"
        )

        print(
            f"    Position : "
            f"{candidate['latitude']:.6f}, "
            f"{candidate['longitude']:.6f}"
        )

        print(
            f"    Distance : "
            f"{candidate['distance_to_source_km']:.3f} km"
        )

        print(
            f"    Time diff: "
            f"{candidate['time_difference_hours']:.2f} hours"
        )

    print(
        f"\nTotal matched vessels: "
        f"{len(results)}"
    )

    print(
        "\n===== AIS SOURCE MATCHING TEST COMPLETE ====="
    )