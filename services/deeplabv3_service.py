from models.deeplabv3.predict import predict


def predict_with_deeplab(image_path):
    """
    Run DeepLabV3+ prediction on an image.

    Parameters
    ----------
    image_path : str
        Path to the input image.

    Returns
    -------
    dict
        DeepLabV3+ prediction result.
    """

    result = predict(image_path)

    return {
        "class": result["class"],
        "oil_spill_detected": result["oil_spill_detected"],
        "confidence": result["confidence"]
    }