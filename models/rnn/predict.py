"""
Standalone RNN trajectory prediction entry point.

The actual model inference is handled by RNNService.
This file provides a simple interface for predicting
the next vessel position.
"""

from services.rnn_service import get_rnn_service


def predict_next_position(
    sequence,
    current_latitude,
    current_longitude
):
    """
    Predict the next geographic position of a vessel.

    Parameters
    ----------
    sequence : array-like
        12 historical AIS observations × 7 features.

    current_latitude : float
        Vessel's current latitude.

    current_longitude : float
        Vessel's current longitude.

    Returns
    -------
    dict
        Predicted vessel position and movement information.
    """

    rnn_service = get_rnn_service()

    result = rnn_service.predict_position(
        sequence=sequence,
        current_latitude=current_latitude,
        current_longitude=current_longitude
    )

    return result


if __name__ == "__main__":

    print("=" * 60)
    print("RNN TRAJECTORY PREDICTION")
    print("=" * 60)

    print()
    print("This module uses RNNService for trajectory prediction.")
    print("Expected input: 12 AIS observations × 7 features")
    print()
    print("Use predict_next_position() from your application")
    print("or from another Python module.")