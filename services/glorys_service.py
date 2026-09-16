from dataclasses import dataclass
from datetime import datetime
from math import atan2, degrees, sqrt

import xarray as xr


KNOTS_PER_MPS = 1.9438444924406


@dataclass
class GLORYSCurrent:
    latitude: float
    longitude: float
    timestamp: str

    uo_mps: float
    vo_mps: float

    speed_mps: float
    speed_knots: float

    direction_deg: float

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "ocean_current": {
                "uo_mps": self.uo_mps,
                "vo_mps": self.vo_mps,
                "speed_mps": self.speed_mps,
                "speed_knots": self.speed_knots,
                "direction_deg": self.direction_deg,
            },
        }


class GLORYSService:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

    def _calculate_current(
        self,
        uo_mps: float,
        vo_mps: float,
    ):
        """
        Calculate current speed and TOWARD direction.

        uo:
            Eastward current component.

        vo:
            Northward current component.

        Direction convention:
            0°   = North
            90°  = East
            180° = South
            270° = West

        Ocean-current vectors describe the direction
        the water is moving TOWARD.
        """

        speed_mps = sqrt(
            uo_mps ** 2 +
            vo_mps ** 2
        )

        direction_deg = (
            degrees(
                atan2(
                    uo_mps,
                    vo_mps,
                )
            )
            + 360.0
        ) % 360.0

        speed_knots = (
            speed_mps *
            KNOTS_PER_MPS
        )

        return (
            speed_mps,
            speed_knots,
            direction_deg,
        )

    def get_current(
        self,
        latitude: float,
        longitude: float,
        timestamp: str,
    ) -> GLORYSCurrent:

        requested_time = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        requested_time = requested_time.replace(
            tzinfo=None
        )

        with xr.open_dataset(
            self.dataset_path
        ) as dataset:

            selected = dataset.sel(
                latitude=latitude,
                longitude=longitude,
                time=requested_time,
                method="nearest",
            )

            # Select the shallowest available ocean layer.
            selected = selected.isel(
                depth=0
            )

            uo_mps = float(
                selected["uo"].values.item()
            )

            vo_mps = float(
                selected["vo"].values.item()
            )

            (
                speed_mps,
                speed_knots,
                direction_deg,
            ) = self._calculate_current(
                uo_mps,
                vo_mps,
            )

            selected_time = selected["time"].values

            return GLORYSCurrent(
                latitude=float(
                    selected.latitude
                ),
                longitude=float(
                    selected.longitude
                ),
                timestamp=str(
                    selected_time
                ),
                uo_mps=uo_mps,
                vo_mps=vo_mps,
                speed_mps=speed_mps,
                speed_knots=speed_knots,
                direction_deg=direction_deg,
            )


if __name__ == "__main__":

    service = GLORYSService(
        "data/ocean_currents/glorys_test.nc"
    )

    current = service.get_current(
        latitude=-19.673594,
        longitude=115.564515,
        timestamp="2021-06-15T03:00:00",
    )

    print()
    print(
        "============================================================"
    )
    print(
        " GLORYS OCEAN CURRENT SERVICE TEST"
    )
    print(
        "============================================================"
    )

    print()
    print("REAL GLORYS DATA")
    print("----------------------------")

    print(
        f"Nearest grid point:"
        f" {current.latitude:.6f},"
        f" {current.longitude:.6f}"
    )

    print(
        f"Timestamp        :"
        f" {current.timestamp}"
    )

    print(
        f"uo               :"
        f" {current.uo_mps:.6f} m/s"
    )

    print(
        f"vo               :"
        f" {current.vo_mps:.6f} m/s"
    )

    print(
        f"Current speed    :"
        f" {current.speed_mps:.6f} m/s"
    )

    print(
        f"Current speed    :"
        f" {current.speed_knots:.6f} knots"
    )

    print(
        f"Current direction:"
        f" {current.direction_deg:.2f}° TOWARD"
    )

    print()
    print("Serialized:")
    print(current.to_dict())

    print()
    print(
        "============================================================"
    )
    print(
        " GLORYS CURRENT SERVICE TEST COMPLETE"
    )
    print(
        "============================================================"
    )