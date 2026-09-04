from models.transunet.predict import predict


def predict_with_transunet(image_path):
    result = predict(image_path)

    return {
        "class": result["class"],
        "oil_spill_detected": result["oil_spill_detected"],
        "confidence": result["confidence"]
    }