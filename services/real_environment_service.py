from services.era5_service import ERA5Service
from services.glorys_service import GLORYSService
from services.environment_service import EnvironmentalConditions


class RealEnvironmentService:
    """
    Combines real ERA5 wind data and real GLORYS ocean-current data
    into the existing EnvironmentalConditions structure.
    """

    def __init__(
        self,
        era5_dataset_path: str,
        glorys_dataset_path: str,
    ):
        self.era5_service = ERA5Service(
            era5_dataset_path
        )

        self.glorys_service = GLORYSService(
            glorys_dataset_path
        )

    def get_environment(
        self,
        latitude: float,
        longitude: float,
        timestamp: str,
    ) -> EnvironmentalConditions:
        """
        Retrieve real environmental conditions for a location
        and timestamp.
        """

        era5_wind = self.era5_service.get_wind(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )

        glorys_current = self.glorys_service.get_current(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )

        # ERA5 reports meteorological wind direction as FROM.
        # Existing HindcastService expects movement TOWARD bearing.
        wind_toward_bearing = (
            era5_wind.direction_deg + 180.0
        ) % 360.0

        return EnvironmentalConditions(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,

            wind_speed_knots=era5_wind.speed_knots,
            wind_direction_deg=wind_toward_bearing,

            current_speed_knots=glorys_current.speed_knots,
            current_direction_deg=glorys_current.direction_deg,
        )


if __name__ == "__main__":

    service = RealEnvironmentService(
        era5_dataset_path="era5_test.nc",
        glorys_dataset_path="data/ocean_currents/glorys_test.nc",
    )

    environment = service.get_environment(
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:00:00",
    )

    print()
    print(
        "============================================================"
    )
    print(
        " REAL ENVIRONMENT SERVICE TEST"
    )
    print(
        "============================================================"
    )

    print()
    print("COMBINED REAL ENVIRONMENT")
    print("----------------------------")

    print(
        f"Location         : "
        f"{environment.latitude:.6f}, "
        f"{environment.longitude:.6f}"
    )

    print(
        f"Timestamp        : "
        f"{environment.timestamp}"
    )

    print()
    print(
        f"Wind speed       : "
        f"{environment.wind_speed_knots:.6f} knots"
    )

    print(
        f"Wind TOWARD      : "
        f"{environment.wind_direction_deg:.2f}°"
    )

    print(
        f"Current speed    : "
        f"{environment.current_speed_knots:.6f} knots"
    )

    print(
        f"Current TOWARD   : "
        f"{environment.current_direction_deg:.2f}°"
    )

    print()
    print("Serialized:")
    print(environment.to_dict())

    print()
    print(
        "============================================================"
    )
    print(
        " REAL ENVIRONMENT SERVICE TEST COMPLETE"
    )
    print(
        "============================================================"
    )