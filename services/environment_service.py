from dataclasses import dataclass
from typing import Dict


@dataclass
class EnvironmentalConditions:
    latitude: float
    longitude: float
    timestamp: str

    wind_speed_knots: float
    wind_direction_deg: float

    current_speed_knots: float
    current_direction_deg: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "wind": {
                "speed_knots": self.wind_speed_knots,
                "direction_deg": self.wind_direction_deg,
            },
            "ocean_current": {
                "speed_knots": self.current_speed_knots,
                "direction_deg": self.current_direction_deg,
            },
        }


def create_environment(
    latitude: float,
    longitude: float,
    timestamp: str,
    wind_speed_knots: float,
    wind_direction_deg: float,
    current_speed_knots: float,
    current_direction_deg: float,
) -> EnvironmentalConditions:
    """
    Create and validate environmental conditions for hindcast processing.
    """

    if not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude must be between -90 and 90 degrees")

    if not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude must be between -180 and 180 degrees")

    if wind_speed_knots < 0:
        raise ValueError("wind_speed_knots cannot be negative")

    if current_speed_knots < 0:
        raise ValueError("current_speed_knots cannot be negative")

    if not 0.0 <= wind_direction_deg < 360.0:
        raise ValueError("wind_direction_deg must be between 0 and 360 degrees")

    if not 0.0 <= current_direction_deg < 360.0:
        raise ValueError(
            "current_direction_deg must be between 0 and 360 degrees"
        )

    return EnvironmentalConditions(
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
        wind_speed_knots=wind_speed_knots,
        wind_direction_deg=wind_direction_deg,
        current_speed_knots=current_speed_knots,
        current_direction_deg=current_direction_deg,
    )


if __name__ == "__main__":
    environment = create_environment(
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:20:00Z",
        wind_speed_knots=20.0,
        wind_direction_deg=90.0,
        current_speed_knots=1.5,
        current_direction_deg=90.0,
    )

    print("\n===== PHASE B ENVIRONMENT SERVICE TEST =====")
    print()
    print(f"Location : {environment.latitude:.6f}, {environment.longitude:.6f}")
    print(f"Timestamp: {environment.timestamp}")
    print()
    print(
        f"Wind    : {environment.wind_speed_knots:.2f} knots "
        f"@ {environment.wind_direction_deg:.2f}°"
    )
    print(
        f"Current : {environment.current_speed_knots:.2f} knots "
        f"@ {environment.current_direction_deg:.2f}°"
    )
    print()
    print("Serialized:")
    print(environment.to_dict())