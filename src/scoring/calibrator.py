def get_calibration_state(sample_count: int) -> str:
    if sample_count < 30:
        return "UNCALIBRATED"
    elif sample_count < 100:
        return "LOW SAMPLE"
    else:
        return "CALIBRATED"
