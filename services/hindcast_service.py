from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Dict, List

from services.environment_service import EnvironmentalConditions


EARTH_RADIUS_KM = 6371.0
KNOT_TO_KMH = 1.852


@dataclass
class ParticlePosition:
    particle_id: int
    hour_before_event: float
    latitude: float
    longitude: float


class HindcastService:
    """
    Lightweight backward particle hindcast engine.

    The model starts particles at the detected spill location and
    propagates them backward in time using wind and ocean-current
    forcing.

    Wind contribution:
        3% of wind speed

    Ocean current contribution:
        100% of current speed
    """

    def __init__(
        self,
        particle_count: int = 100,
        wind_factor: float = 0.03,
    ):
        if particle_count <= 0:
            raise ValueError("particle_count must be greater than zero")

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

        bearing_rad = radians(bearing_deg)

        east = speed_knots * sin(bearing_rad)
        north = speed_knots * cos(bearing_rad)

        return east, north

    @staticmethod
    def _move_position(
        latitude: float,
        longitude: float,
        distance_km: float,
        bearing_deg: float,
    ) -> tuple[float, float]:
        """
        Move a geographic coordinate along a great-circle path.
        """

        lat1 = radians(latitude)
        lon1 = radians(longitude)
        bearing = radians(bearing_deg)

        angular_distance = distance_km / EARTH_RADIUS_KM

        lat2 = __import__("math").asin(
            sin(lat1) * cos(angular_distance)
            + cos(lat1)
            * sin(angular_distance)
            * cos(bearing)
        )

        lon2 = lon1 + atan2(
            sin(bearing) * sin(angular_distance) * cos(lat1),
            cos(angular_distance) - sin(lat1) * sin(lat2),
        )

        latitude_out = __import__("math").degrees(lat2)
        longitude_out = (
            __import__("math").degrees(lon2) + 540
        ) % 360 - 180

        return latitude_out, longitude_out

    def _calculate_drift(
        self,
        environment: EnvironmentalConditions,
    ) -> tuple[float, float]:
        """
        Calculate the combined forward drift speed and bearing.
        """

        wind_effective_speed = (
            environment.wind_speed_knots * self.wind_factor
        )

        wind_east, wind_north = self._vector_from_speed_bearing(
            wind_effective_speed,
            environment.wind_direction_deg,
        )

        current_east, current_north = self._vector_from_speed_bearing(
            environment.current_speed_knots,
            environment.current_direction_deg,
        )

        total_east = wind_east + current_east
        total_north = wind_north + current_north

        drift_speed = sqrt(
            total_east**2 + total_north**2
        )

        if drift_speed == 0:
            return 0.0, 0.0

        drift_bearing = (
            __import__("math").degrees(
                atan2(total_east, total_north)
            )
            + 360
        ) % 360

        return drift_speed, drift_bearing

    def _particle_offsets(self) -> List[tuple[float, float]]:
        """
        Generate deterministic particle offsets.

        The offsets introduce a small spatial uncertainty around
        the central drift trajectory.
        """

        offsets = []

        if self.particle_count == 1:
            return [(0.0, 0.0)]

        for particle_id in range(self.particle_count):
            normalized = (
                particle_id / (self.particle_count - 1)
            )

            # Spread approximately ±0.05 degrees.
            latitude_offset = (
                normalized - 0.5
            ) * 0.10

            longitude_offset = (
                0.5 - normalized
            ) * 0.10

            offsets.append(
                (
                    latitude_offset,
                    longitude_offset,
                )
            )

        return offsets

    def backward_hindcast(
        self,
        spill_latitude: float,
        spill_longitude: float,
        environment: EnvironmentalConditions,
        lookback_hours: float = 6.0,
        time_step_hours: float = 1.0,
    ) -> Dict[str, object]:
        """
        Run a backward particle hindcast.

        Returns:
            - spill location
            - drift speed and bearing
            - particle tracks
            - final source-zone particles
        """

        if not -90.0 <= spill_latitude <= 90.0:
            raise ValueError(
                "spill_latitude must be between -90 and 90 degrees"
            )

        if not -180.0 <= spill_longitude <= 180.0:
            raise ValueError(
                "spill_longitude must be between -180 and 180 degrees"
            )

        if lookback_hours <= 0:
            raise ValueError(
                "lookback_hours must be greater than zero"
            )

        if time_step_hours <= 0:
            raise ValueError(
                "time_step_hours must be greater than zero"
            )

        drift_speed_knots, drift_bearing_deg = self._calculate_drift(
            environment
        )

        offsets = self._particle_offsets()

        number_of_steps = int(
            lookback_hours / time_step_hours
        )

        tracks: List[List[Dict[str, object]]] = []

        for particle_id, (
            initial_lat_offset,
            initial_lon_offset,
        ) in enumerate(offsets):

            current_latitude = (
                spill_latitude + initial_lat_offset
            )

            current_longitude = (
                spill_longitude + initial_lon_offset
            )

            particle_track = []

            particle_track.append(
                {
                    "particle_id": particle_id,
                    "hour_before_event": 0.0,
                    "latitude": current_latitude,
                    "longitude": current_longitude,
                }
            )

            for step in range(
                1,
                number_of_steps + 1,
            ):
                elapsed_hours = (
                    step * time_step_hours
                )

                # Backward trajectory uses the opposite
                # direction of the forward drift.
                backward_bearing = (
                    drift_bearing_deg + 180.0
                ) % 360.0

                distance_km = (
                    drift_speed_knots
                    * KNOT_TO_KMH
                    * time_step_hours
                )

                current_latitude, current_longitude = (
                    self._move_position(
                        current_latitude,
                        current_longitude,
                        distance_km,
                        backward_bearing,
                    )
                )

                particle_track.append(
                    {
                        "particle_id": particle_id,
                        "hour_before_event": elapsed_hours,
                        "latitude": current_latitude,
                        "longitude": current_longitude,
                    }
                )

            tracks.append(particle_track)

        source_particles = [
            track[-1]
            for track in tracks
        ]

        return {
            "spill_location": {
                "latitude": spill_latitude,
                "longitude": spill_longitude,
            },
            "environment": environment.to_dict(),
            "particle_count": self.particle_count,
            "lookback_hours": lookback_hours,
            "time_step_hours": time_step_hours,
            "drift": {
                "speed_knots": drift_speed_knots,
                "bearing_deg": drift_bearing_deg,
                "backward_bearing_deg": (
                    drift_bearing_deg + 180.0
                ) % 360.0,
            },
            "tracks": tracks,
            "source_particles": source_particles,
        }


if __name__ == "__main__":
    environment = EnvironmentalConditions(
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:20:00Z",
        wind_speed_knots=20.0,
        wind_direction_deg=90.0,
        current_speed_knots=1.5,
        current_direction_deg=90.0,
    )

    service = HindcastService(
        particle_count=100,
        wind_factor=0.03,
    )

    result = service.backward_hindcast(
        spill_latitude=-19.673594,
        spill_longitude=115.564515,
        environment=environment,
        lookback_hours=6.0,
        time_step_hours=1.0,
    )

    print("\n===== PHASE B BACKWARD HINDCAST TEST =====\n")

    print("Spill location:")
    print(
        f"  Latitude : "
        f"{result['spill_location']['latitude']:.6f}"
    )
    print(
        f"  Longitude: "
        f"{result['spill_location']['longitude']:.6f}"
    )

    print("\nParticle simulation:")
    print(
        f"  Particles       : "
        f"{result['particle_count']}"
    )
    print(
        f"  Lookback        : "
        f"{result['lookback_hours']:.1f} hours"
    )
    print(
        f"  Time step       : "
        f"{result['time_step_hours']:.1f} hour"
    )

    print("\nEstimated drift:")
    print(
        f"  Speed           : "
        f"{result['drift']['speed_knots']:.3f} knots"
    )
    print(
        f"  Forward bearing : "
        f"{result['drift']['bearing_deg']:.2f}°"
    )
    print(
        f"  Backward bearing: "
        f"{result['drift']['backward_bearing_deg']:.2f}°"
    )

    print("\nFirst particle track:")

    for point in result["tracks"][0]:
        print(
            f"  -{point['hour_before_event']:.0f}h : "
            f"{point['latitude']:.6f}, "
            f"{point['longitude']:.6f}"
        )

    print("\nSource-zone sample:")

    for particle in result["source_particles"][:5]:
        print(
            f"  Particle {particle['particle_id']:03d}: "
            f"{particle['latitude']:.6f}, "
            f"{particle['longitude']:.6f}"
        )

    print(
        f"\nTotal source particles: "
        f"{len(result['source_particles'])}"
    )

    print("\n===== HINDCAST TEST COMPLETE =====")