from models.unet.predict import predict


def predict_with_unet(image_path):
    """
    Run U-Net inference on a single image.
    """

    result = predict(image_path)

    return {
        "class": result["class"],
        "oil_spill_detected": result["oil_spill_detected"]
    }