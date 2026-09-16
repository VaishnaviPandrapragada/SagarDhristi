import numpy as np


def calculate_spill_geometry(mask):
    """
    Calculate basic geometric properties from a binary oil-spill mask.

    Parameters
    ----------
    mask : numpy.ndarray
        Binary mask where:
        0 = background
        1 = oil spill

    Returns
    -------
    dict
        Spill geometry and statistics.
    """

    mask = np.asarray(mask)

    if mask.ndim == 3:
        mask = np.squeeze(mask)

    binary_mask = mask > 0.5

    total_pixels = binary_mask.size
    spill_pixels = int(binary_mask.sum())

    if spill_pixels == 0:

        return {
            "spill_present": False,
            "area_pixels": 0,
            "coverage_ratio": 0.0,
            "bounding_box": None,
            "centroid": None
        }

    ys, xs = np.where(binary_mask)

    x_min = int(xs.min())
    x_max = int(xs.max())
    y_min = int(ys.min())
    y_max = int(ys.max())

    centroid_x = float(xs.mean())
    centroid_y = float(ys.mean())

    coverage_ratio = spill_pixels / total_pixels

    return {
        "spill_present": True,

        "area_pixels": spill_pixels,

        "coverage_ratio": round(
            float(coverage_ratio),
            6
        ),

        "bounding_box": {
            "x_min": x_min,
            "y_min": y_min,
            "x_max": x_max,
            "y_max": y_max,
            "width": x_max - x_min + 1,
            "height": y_max - y_min + 1
        },

        "centroid": {
            "x": round(centroid_x, 2),
            "y": round(centroid_y, 2)
        }
    }


if __name__ == "__main__":

    print("=" * 60)
    print("TESTING SPILL GEOMETRY")
    print("=" * 60)

    test_mask = np.zeros(
        (256, 256),
        dtype=np.float32
    )

    test_mask[80:150, 100:180] = 1

    result = calculate_spill_geometry(test_mask)

    print("Spill present :", result["spill_present"])
    print("Area pixels   :", result["area_pixels"])
    print("Coverage      :", result["coverage_ratio"])
    print("Bounding box  :", result["bounding_box"])
    print("Centroid      :", result["centroid"])

    print()
    print("Geometry test completed successfully!")