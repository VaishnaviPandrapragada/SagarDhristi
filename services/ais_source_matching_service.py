from datetime import datetime, timedelta, timezone
from typing import Dict, List

import math
import pandas as pd


class AISSourceMatchingService:
    """
    Matches historical AIS vessel positions against a probable
    oil-spill source zone and estimated source time.
    """

    def __init__(
        self,
        time_tolerance_hours: float = 1.0,
        spatial_radius_km: float = 25.0,
    ):
        if time_tolerance_hours < 0:
            raise ValueError(
                "time_tolerance_hours cannot be negative"
            )

        if spatial_radius_km <= 0:
            raise ValueError(
                "spatial_radius_km must be greater than zero"
            )

        self.time_tolerance_hours = time_tolerance_hours
        self.spatial_radius_km = spatial_radius_km

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
        lookup = {column.lower(): column for column in dataframe.columns}

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
        earth_radius_km = 6371.0

        lat1 = math.radians(latitude_1)
        lon1 = math.radians(longitude_1)
        lat2 = math.radians(latitude_2)
        lon2 = math.radians(longitude_2)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        return 2 * earth_radius_km * math.asin(math.sqrt(a))

    def match_vessels(
        self,
        dataframe: pd.DataFrame,
        source_zone: Dict[str, object],
        estimated_source_time: str,
    ) -> List[Dict[str, object]]:

        if dataframe.empty:
            return []

        latitude_column = self._find_column(
            dataframe,
            ["latitude", "lat", "LAT"],
        )

        longitude_column = self._find_column(
            dataframe,
            ["longitude", "lon", "lng", "LON"],
        )

        vessel_column = self._find_column(
            dataframe,
            ["mmsi", "MMSI", "vessel_id", "ship_id"],
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

        # ---------------------------------------------------------
        # STEP 1: Temporal filtering
        # ---------------------------------------------------------

        working = working[
            (working["_parsed_time"] >= start_time)
            & (working["_parsed_time"] <= end_time)
        ]

        if working.empty:
            return []

        # ---------------------------------------------------------
        # STEP 2: Spatial filtering
        #
        # Use distance from the source-zone CENTER rather than
        # requiring AIS observations to fall inside the rectangular
        # visualization bounds.
        # ---------------------------------------------------------

        center = source_zone["center"]

        center_latitude = float(
            center["latitude"]
        )

        center_longitude = float(
            center["longitude"]
        )

        working["_distance_to_source_km"] = working.apply(
            lambda row: self._distance_km(
                float(row[latitude_column]),
                float(row[longitude_column]),
                center_latitude,
                center_longitude,
            ),
            axis=1,
        )

        working = working[
            working["_distance_to_source_km"]
            <= self.spatial_radius_km
        ]

        if working.empty:
            return []

        # ---------------------------------------------------------
        # STEP 3: Build candidate observations
        # ---------------------------------------------------------

        results = []

        for _, row in working.iterrows():

            timestamp = row["_parsed_time"]

            time_difference_hours = abs(
                (timestamp - source_time).total_seconds()
            ) / 3600.0

            results.append(
                {
                    "vessel_id": str(
                        row[vessel_column]
                    ),
                    "latitude": float(
                        row[latitude_column]
                    ),
                    "longitude": float(
                        row[longitude_column]
                    ),
                    "timestamp": timestamp.isoformat(),
                    "distance_to_source_km": float(
                        row["_distance_to_source_km"]
                    ),
                    "time_difference_hours": float(
                        time_difference_hours
                    ),
                }
            )

        # ---------------------------------------------------------
        # STEP 4: Rank by spatial + temporal relevance
        # ---------------------------------------------------------

        results.sort(
            key=lambda item: (
                item["distance_to_source_km"],
                item["time_difference_hours"],
            )
        )

        # ---------------------------------------------------------
        # STEP 5: Keep the closest observation per vessel
        # ---------------------------------------------------------

        deduplicated = {}

        for result in results:

            vessel_id = result["vessel_id"]

            if vessel_id not in deduplicated:
                deduplicated[vessel_id] = result

        final_results = list(
            deduplicated.values()
        )

        # ---------------------------------------------------------
        # STEP 6: Assign rank
        # ---------------------------------------------------------

        for rank, result in enumerate(
            final_results,
            start=1,
        ):
            result["rank"] = rank

        return final_results


if __name__ == "__main__":

    # Small local sanity test
    dataframe = pd.DataFrame(
        [
            {
                "MMSI": "SIM030012",
                "LAT": 13.45862,
                "LON": 144.66887,
                "BaseDateTime": "2022-03-04T00:30:00Z",
            },
            {
                "MMSI": "SIM030013",
                "LAT": 13.45833,
                "LON": 144.66667,
                "BaseDateTime": "2022-03-04T00:40:00Z",
            },
        ]
    )

    source_zone = {
        "center": {
            "latitude": 13.476756645778078,
            "longitude": 144.72374415911764,
        },
        "bounds": {
            "min_latitude": 13.426756,
            "max_latitude": 13.526756,
            "min_longitude": 144.673757,
            "max_longitude": 144.773730,
        },
    }

    service = AISSourceMatchingService()

    candidates = service.match_vessels(
        dataframe=dataframe,
        source_zone=source_zone,
        estimated_source_time="2022-03-04T00:30:27Z",
    )

    for candidate in candidates:
        print(candidate)