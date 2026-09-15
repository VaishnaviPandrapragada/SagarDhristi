from typing import Dict, List

from services.environment_service import EnvironmentalConditions


EARTH_RADIUS_KM = 6371.0
KNOT_TO_KMH = 1.852


class ForwardDriftService:
    """
    Predicts the forward movement of oil from a probable
    source position using wind and ocean-current forcing.

    The physics intentionally matches the Phase-B hindcast model.
    """

    def __init__(self, particle_count: int = 100, wind_factor: float = 0.03):
        if particle_count <= 0:
            raise ValueError("particle_count must be positive")

        if wind_factor < 0:
            raise ValueError("wind_factor cannot be negative")

        self.particle_count = particle_count
        self.wind_factor = wind_factor

    @staticmethod
    def _vector_from_speed_bearing(
        speed_knots: float,
        bearing_deg: float,
    ) -> tuple[float, float]:
        """
        Convert speed and bearing into east/north components.

        Bearing convention:
            0°   = North
            90°  = East
            180° = South
            270° = West
        """

        import math

        bearing_rad = math.radians(bearing_deg)

        east = speed_knots * math.sin(bearing_rad)
        north = speed_knots * math.cos(bearing_rad)

        return east, north

    @staticmethod
    def _move_position(
        latitude: float,
        longitude: float,
        distance_km: float,
        bearing_deg: float,
    ) -> tuple[float, float]:
        """
        Move a geographic position along a spherical Earth.
        """

        import math

        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        bearing = math.radians(bearing_deg)

        angular_distance = distance_km / EARTH_RADIUS_KM

        lat2 = math.asin(
            math.sin(lat1) * math.cos(angular_distance)
            + math.cos(lat1)
            * math.sin(angular_distance)
            * math.cos(bearing)
        )

        lon2 = lon1 + math.atan2(
            math.sin(bearing)
            * math.sin(angular_distance)
            * math.cos(lat1),
            math.cos(angular_distance)
            - math.sin(lat1) * math.sin(lat2),
        )

        latitude_out = math.degrees(lat2)
        longitude_out = math.degrees(lon2)

        longitude_out = (longitude_out + 180.0) % 360.0 - 180.0

        return latitude_out, longitude_out

    def _calculate_drift(
        self,
        environment: EnvironmentalConditions,
    ) -> Dict[str, float]:
        """
        Combine wind-driven and ocean-current movement.
        """

        wind_east, wind_north = self._vector_from_speed_bearing(
            environment.wind_speed_knots * self.wind_factor,
            environment.wind_direction_deg,
        )

        current_east, current_north = self._vector_from_speed_bearing(
            environment.current_speed_knots,
            environment.current_direction_deg,
        )

        total_east = wind_east + current_east
        total_north = wind_north + current_north

        import math

        speed = math.sqrt(
            total_east ** 2 + total_north ** 2
        )

        bearing = math.degrees(
            math.atan2(total_east, total_north)
        )

        bearing = (bearing + 360.0) % 360.0

        return {
            "speed_knots": speed,
            "bearing_deg": bearing,
            "east_component_knots": total_east,
            "north_component_knots": total_north,
        }

    @staticmethod
    def _particle_offsets(
        particle_count: int,
    ) -> List[tuple[float, float]]:
        """
        Create deterministic small offsets around the source position.

        This provides a simple particle cloud for development and
        testing without introducing random/non-reproducible results.
        """

        offsets = []

        grid_size = int(particle_count ** 0.5)

        if grid_size * grid_size < particle_count:
            grid_size += 1

        spacing = 0.01

        for index in range(particle_count):
            row = index // grid_size
            column = index % grid_size

            latitude_offset = (
                (row - (grid_size - 1) / 2.0) * spacing
            )

            longitude_offset = (
                (column - (grid_size - 1) / 2.0) * spacing
            )

            offsets.append(
                (
                    latitude_offset,
                    longitude_offset,
                )
            )

        return offsets

    def forward_drift(
        self,
        source_latitude: float,
        source_longitude: float,
        environment: EnvironmentalConditions,
        forecast_hours: float = 6.0,
        time_step_hours: float = 1.0,
    ) -> Dict[str, object]:
        """
        Simulate forward oil movement from the estimated source.

        Returns a trajectory for every particle.
        """

        if not -90.0 <= source_latitude <= 90.0:
            raise ValueError("Invalid source latitude")

        if not -180.0 <= source_longitude <= 180.0:
            raise ValueError("Invalid source longitude")

        if forecast_hours <= 0:
            raise ValueError("forecast_hours must be positive")

        if time_step_hours <= 0:
            raise ValueError("time_step_hours must be positive")

        drift = self._calculate_drift(environment)

        speed_knots = drift["speed_knots"]
        bearing_deg = drift["bearing_deg"]

        offsets = self._particle_offsets(
            self.particle_count
        )

        tracks = []

        number_of_steps = int(
            forecast_hours / time_step_hours
        )

        distance_per_step_km = (
            speed_knots
            * KNOT_TO_KMH
            * time_step_hours
        )

        for particle_id, (
            latitude_offset,
            longitude_offset,
        ) in enumerate(offsets):

            latitude = source_latitude + latitude_offset
            longitude = source_longitude + longitude_offset

            track = [
                {
                    "hour": 0.0,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            ]

            for step in range(1, number_of_steps + 1):

                latitude, longitude = self._move_position(
                    latitude=latitude,
                    longitude=longitude,
                    distance_km=distance_per_step_km,
                    bearing_deg=bearing_deg,
                )

                track.append(
                    {
                        "hour": step * time_step_hours,
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                )

            tracks.append(
                {
                    "particle_id": particle_id,
                    "track": track,
                    "final_position": track[-1],
                }
            )

        return {
            "source": {
                "latitude": source_latitude,
                "longitude": source_longitude,
            },
            "environment": environment.to_dict(),
            "particle_count": self.particle_count,
            "forecast_hours": forecast_hours,
            "time_step_hours": time_step_hours,
            "drift": drift,
            "tracks": tracks,
        }


if __name__ == "__main__":
    print("\n===== PHASE B FORWARD DRIFT TEST =====")

    environment = EnvironmentalConditions(
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:20:00Z",
        wind_speed_knots=20.0,
        wind_direction_deg=90.0,
        current_speed_knots=1.5,
        current_direction_deg=90.0,
    )

    service = ForwardDriftService(
        particle_count=100,
        wind_factor=0.03,
    )

    result = service.forward_drift(
        source_latitude=-19.673571,
        source_longitude=115.341647,
        environment=environment,
        forecast_hours=6.0,
        time_step_hours=1.0,
    )

    drift = result["drift"]

    print("\nSource position:")
    print(
        f"  Latitude : "
        f"{result['source']['latitude']:.6f}"
    )
    print(
        f"  Longitude: "
        f"{result['source']['longitude']:.6f}"
    )

    print("\nParticle simulation:")
    print(
        f"  Particles : {result['particle_count']}"
    )
    print(
        f"  Forecast  : {result['forecast_hours']:.1f} hours"
    )
    print(
        f"  Time step : {result['time_step_hours']:.1f} hour"
    )

    print("\nEstimated drift:")
    print(
        f"  Speed   : "
        f"{drift['speed_knots']:.3f} knots"
    )
    print(
        f"  Bearing : "
        f"{drift['bearing_deg']:.2f}°"
    )

    first_track = result["tracks"][0]["track"]

    print("\nFirst particle track:")

    for point in first_track:
        print(
            f"  +{point['hour']:.0f}h : "
            f"{point['latitude']:.6f}, "
            f"{point['longitude']:.6f}"
        )

    final_position = result["tracks"][0]["final_position"]

    print("\nFinal predicted position:")
    print(
        f"  Latitude : "
        f"{final_position['latitude']:.6f}"
    )
    print(
        f"  Longitude: "
        f"{final_position['longitude']:.6f}"
    )

    print(
        f"\nTotal predicted particles: "
        f"{len(result['tracks'])}"
    )

    print("\n===== FORWARD DRIFT TEST COMPLETE =====")