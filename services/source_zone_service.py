from typing import Dict, List


class SourceZoneService:
    """
    Converts backward-hindcast particle endpoints into
    a geographic probable source zone.
    """

    def __init__(self, containment_percent: float = 90.0):
        if not 0.0 < containment_percent <= 100.0:
            raise ValueError("containment_percent must be > 0 and <= 100")

        self.containment_percent = containment_percent

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """
        Calculate a percentile using linear interpolation.
        """
        if not values:
            raise ValueError("Cannot calculate percentile of empty list")

        sorted_values = sorted(values)

        if len(sorted_values) == 1:
            return sorted_values[0]

        position = (len(sorted_values) - 1) * percentile / 100.0

        lower_index = int(position)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)

        fraction = position - lower_index

        return (
            sorted_values[lower_index]
            + fraction
            * (sorted_values[upper_index] - sorted_values[lower_index])
        )

    def calculate_source_zone(
        self,
        source_particles: List[Dict[str, float]],
    ) -> Dict[str, object]:
        """
        Calculate the probable source zone from particle endpoints.

        Each particle must contain:
            latitude
            longitude
        """

        if not source_particles:
            raise ValueError("source_particles cannot be empty")

        latitudes = []
        longitudes = []

        for particle in source_particles:
            if "latitude" not in particle or "longitude" not in particle:
                raise ValueError(
                    "Each source particle must contain latitude and longitude"
                )

            latitudes.append(float(particle["latitude"]))
            longitudes.append(float(particle["longitude"]))

        # Mean source position
        center_latitude = sum(latitudes) / len(latitudes)
        center_longitude = sum(longitudes) / len(longitudes)

        # Full particle bounds
        min_latitude = min(latitudes)
        max_latitude = max(latitudes)
        min_longitude = min(longitudes)
        max_longitude = max(longitudes)

        # Containment bounds.
        #
        # For 90% containment, the lower 5th percentile and
        # upper 95th percentile are used.
        excluded_percent = (100.0 - self.containment_percent) / 2.0

        lower_percentile = excluded_percent
        upper_percentile = 100.0 - excluded_percent

        containment_min_latitude = self._percentile(
            latitudes,
            lower_percentile,
        )

        containment_max_latitude = self._percentile(
            latitudes,
            upper_percentile,
        )

        containment_min_longitude = self._percentile(
            longitudes,
            lower_percentile,
        )

        containment_max_longitude = self._percentile(
            longitudes,
            upper_percentile,
        )

        # Approximate geographic spread.
        latitude_spread_km = (
            containment_max_latitude - containment_min_latitude
        ) * 111.0

        longitude_scale = max(
            0.01,
            abs(center_latitude),
        )

        # Approximate longitude distance using latitude.
        import math

        longitude_km_per_degree = (
            111.0
            * math.cos(math.radians(center_latitude))
        )

        longitude_spread_km = (
            containment_max_longitude
            - containment_min_longitude
        ) * longitude_km_per_degree

        return {
            "center": {
                "latitude": center_latitude,
                "longitude": center_longitude,
            },
            "bounds": {
                "min_latitude": min_latitude,
                "max_latitude": max_latitude,
                "min_longitude": min_longitude,
                "max_longitude": max_longitude,
            },
            "containment": {
                "percentage": self.containment_percent,
                "min_latitude": containment_min_latitude,
                "max_latitude": containment_max_latitude,
                "min_longitude": containment_min_longitude,
                "max_longitude": containment_max_longitude,
            },
            "spread_km": {
                "latitude": latitude_spread_km,
                "longitude": longitude_spread_km,
            },
            "particle_count": len(source_particles),
        }


def _build_test_particles() -> List[Dict[str, float]]:
    """
    Build a deterministic test source zone.

    These particles reproduce the approximate source-particle
    pattern produced by the Phase B hindcast test.
    """

    particles = []

    base_latitude = -19.723571
    base_longitude = 115.391577

    for index in range(100):
        row = index // 10
        column = index % 10

        latitude = base_latitude + row * 0.001
        longitude = base_longitude - column * 0.001

        particles.append(
            {
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    return particles


if __name__ == "__main__":
    print("\n===== PHASE B SOURCE ZONE TEST =====")

    particles = _build_test_particles()

    service = SourceZoneService(
        containment_percent=90.0
    )

    source_zone = service.calculate_source_zone(
        source_particles=particles
    )

    center = source_zone["center"]
    bounds = source_zone["bounds"]
    containment = source_zone["containment"]
    spread = source_zone["spread_km"]

    print("\nSource-zone center:")
    print(
        f"  Latitude : {center['latitude']:.6f}"
    )
    print(
        f"  Longitude: {center['longitude']:.6f}"
    )

    print("\nFull particle bounds:")
    print(
        f"  Latitude : "
        f"{bounds['min_latitude']:.6f}"
        f" to "
        f"{bounds['max_latitude']:.6f}"
    )
    print(
        f"  Longitude: "
        f"{bounds['min_longitude']:.6f}"
        f" to "
        f"{bounds['max_longitude']:.6f}"
    )

    print("\n90% containment zone:")
    print(
        f"  Latitude : "
        f"{containment['min_latitude']:.6f}"
        f" to "
        f"{containment['max_latitude']:.6f}"
    )
    print(
        f"  Longitude: "
        f"{containment['min_longitude']:.6f}"
        f" to "
        f"{containment['max_longitude']:.6f}"
    )

    print("\nApproximate spread:")
    print(
        f"  Latitude spread : "
        f"{spread['latitude']:.3f} km"
    )
    print(
        f"  Longitude spread: "
        f"{spread['longitude']:.3f} km"
    )

    print(
        f"\nTotal source particles: "
        f"{source_zone['particle_count']}"
    )

    print("\n===== SOURCE ZONE TEST COMPLETE =====")