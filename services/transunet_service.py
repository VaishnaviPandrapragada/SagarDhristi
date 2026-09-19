from models.transunet.predict import predict

def predict_with_transunet(image_path):
    result=predict(image_path)
    return {"model":"TransUNet","class":result["class"],"oil_spill_detected":result["oil_spill_detected"],
            "confidence":result["confidence"],"mask":result["mask"],"mask_shape":result["mask_shape"],
            "spill_pixels":result["spill_pixels"],"coverage_ratio":result["coverage_ratio"],
            "mask_image":result["mask_image"],"original_image_size":result["original_image_size"],
            "model_input_size":result["model_input_size"]}
