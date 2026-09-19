from dataclasses import dataclass
from datetime import datetime
from math import atan2, degrees, sqrt

import xarray as xr


KNOTS_PER_MPS = 1.9438444924406


@dataclass
class ERA5Wind:
    latitude: float
    longitude: float
    timestamp: str
    u10_mps: float
    v10_mps: float
    speed_mps: float
    speed_knots: float
    direction_deg: float

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "u10_mps": self.u10_mps,
            "v10_mps": self.v10_mps,
            "speed_mps": self.speed_mps,
            "speed_knots": self.speed_knots,
            "direction_deg": self.direction_deg,
        }


class ERA5Service:
    """
    Reads ERA5 NetCDF data and extracts 10 m wind conditions.

    ERA5 u10/v10 are vector components:
        u10 = eastward wind component
        v10 = northward wind component

    direction_deg uses the meteorological "from" convention:
        0°   = from north
        90°  = from east
        180° = from south
        270° = from west
    """

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

    def _calculate_wind(
        self,
        u10_mps: float,
        v10_mps: float,
    ):
        speed_mps = sqrt(
            u10_mps ** 2 +
            v10_mps ** 2
        )

        direction_deg = (
            degrees(
                atan2(
                    -u10_mps,
                    -v10_mps,
                )
            )
            + 360.0
        ) % 360.0

        speed_knots = speed_mps * KNOTS_PER_MPS

        return speed_mps, speed_knots, direction_deg

    def get_wind(
        self,
        latitude: float,
        longitude: float,
        timestamp: str,
    ) -> ERA5Wind:

        requested_time = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        requested_time = requested_time.replace(tzinfo=None)

        with xr.open_dataset(self.dataset_path) as dataset:

            selected = dataset.sel(
                latitude=latitude,
                longitude=longitude,
                valid_time=requested_time,
                method="nearest",
            )

            u10_mps = float(
                selected["u10"].values
            )

            v10_mps = float(
                selected["v10"].values
            )

            speed_mps, speed_knots, direction_deg = (
                self._calculate_wind(
                    u10_mps,
                    v10_mps,
                )
            )

            selected_time = selected["valid_time"].values

            return ERA5Wind(
                latitude=float(selected.latitude),
                longitude=float(selected.longitude),
                timestamp=str(selected_time),
                u10_mps=u10_mps,
                v10_mps=v10_mps,
                speed_mps=speed_mps,
                speed_knots=speed_knots,
                direction_deg=direction_deg,
            )


if __name__ == "__main__":

    service = ERA5Service("era5_test.nc")

    wind = service.get_wind(
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:00:00",
    )

    print("\n===== ERA5 WIND SERVICE TEST =====")

    print(
        f"Nearest ERA5 grid point:"
        f" {wind.latitude:.6f}, {wind.longitude:.6f}"
    )

    print(
        f"Timestamp:"
        f" {wind.timestamp}"
    )

    print(
        f"u10:"
        f" {wind.u10_mps:.4f} m/s"
    )

    print(
        f"v10:"
        f" {wind.v10_mps:.4f} m/s"
    )

    print(
        f"Wind speed:"
        f" {wind.speed_mps:.4f} m/s"
    )

    print(
        f"Wind speed:"
        f" {wind.speed_knots:.4f} knots"
    )

    print(
        f"Wind direction:"
        f" {wind.direction_deg:.2f}°"
    )