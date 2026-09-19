from services.era5_service import ERA5Service
from services.glorys_service import GLORYSService
from services.environment_service import EnvironmentalConditions
from services.hindcast_service import HindcastService


ERA5_FILE = "era5_test.nc"
GLORYS_FILE = "data/ocean_currents/glorys_test.nc"

SPILL_LATITUDE = -19.673594
SPILL_LONGITUDE = 115.564515
SPILL_TIMESTAMP = "2021-06-15T03:00:00"


era5_service = ERA5Service(
    ERA5_FILE
)

glorys_service = GLORYSService(
    GLORYS_FILE
)


# ------------------------------------------------------------
# REAL ERA5 WIND
# ------------------------------------------------------------

era5_wind = era5_service.get_wind(
    latitude=SPILL_LATITUDE,
    longitude=SPILL_LONGITUDE,
    timestamp=SPILL_TIMESTAMP,
)


# ERA5 direction is meteorological FROM direction.
# Existing HindcastService expects TOWARD bearing.
wind_toward_bearing = (
    era5_wind.direction_deg + 180.0
) % 360.0


# ------------------------------------------------------------
# REAL GLORYS OCEAN CURRENT
# ------------------------------------------------------------

glorys_current = glorys_service.get_current(
    latitude=SPILL_LATITUDE,
    longitude=SPILL_LONGITUDE,
    timestamp=SPILL_TIMESTAMP,
)


# ------------------------------------------------------------
# COMBINED ENVIRONMENT
# ------------------------------------------------------------

environment = EnvironmentalConditions(
    latitude=SPILL_LATITUDE,
    longitude=SPILL_LONGITUDE,
    timestamp=SPILL_TIMESTAMP + "Z",

    wind_speed_knots=era5_wind.speed_knots,
    wind_direction_deg=wind_toward_bearing,

    current_speed_knots=glorys_current.speed_knots,
    current_direction_deg=glorys_current.direction_deg,
)


# ------------------------------------------------------------
# EXISTING HINDCAST SERVICE
# ------------------------------------------------------------

hindcast_service = HindcastService(
    particle_count=100,
    wind_factor=0.03,
)


result = hindcast_service.backward_hindcast(
    spill_latitude=SPILL_LATITUDE,
    spill_longitude=SPILL_LONGITUDE,
    environment=environment,
    lookback_hours=6.0,
    time_step_hours=1.0,
)


# ------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------

print()
print(
    "============================================================"
)
print(
    " REAL ERA5 + GLORYS → HINDCAST TEST"
)
print(
    "============================================================"
)


print()
print("REAL ERA5 WIND")
print("----------------------------")

print(
    f"Grid point       : "
    f"{era5_wind.latitude:.6f}, "
    f"{era5_wind.longitude:.6f}"
)

print(
    f"Timestamp        : "
    f"{era5_wind.timestamp}"
)

print(
    f"u10              : "
    f"{era5_wind.u10_mps:.4f} m/s"
)

print(
    f"v10              : "
    f"{era5_wind.v10_mps:.4f} m/s"
)

print(
    f"Wind speed       : "
    f"{era5_wind.speed_knots:.4f} knots"
)

print(
    f"ERA5 FROM        : "
    f"{era5_wind.direction_deg:.2f}°"
)

print(
    f"Hindcast TOWARD  : "
    f"{wind_toward_bearing:.2f}°"
)


print()
print("REAL GLORYS OCEAN CURRENT")
print("----------------------------")

print(
    f"Grid point       : "
    f"{glorys_current.latitude:.6f}, "
    f"{glorys_current.longitude:.6f}"
)

print(
    f"Timestamp        : "
    f"{glorys_current.timestamp}"
)

print(
    f"uo               : "
    f"{glorys_current.uo_mps:.6f} m/s"
)

print(
    f"vo               : "
    f"{glorys_current.vo_mps:.6f} m/s"
)

print(
    f"Current speed    : "
    f"{glorys_current.speed_knots:.6f} knots"
)

print(
    f"Current TOWARD   : "
    f"{glorys_current.direction_deg:.2f}°"
)


print()
print("COMBINED ENVIRONMENT")
print("----------------------------")

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
print("HINDCAST RESULT")
print("----------------------------")

print(
    f"Drift speed      : "
    f"{result['drift']['speed_knots']:.6f} knots"
)

print(
    f"Forward bearing  : "
    f"{result['drift']['bearing_deg']:.2f}°"
)

print(
    f"Backward bearing : "
    f"{result['drift']['backward_bearing_deg']:.2f}°"
)

print(
    f"Source particles : "
    f"{len(result['source_particles'])}"
)

source_estimate = result.get(
    "source_estimate"
)

if source_estimate:
    print(
        f"Source estimate  : "
        f"{source_estimate}"
    )


print()
print(
    "============================================================"
)
print(
    " REAL ENVIRONMENT HINDCAST TEST COMPLETE"
)
print(
    "============================================================"
)