import numpy as np

def compute_brightness_temperature(
    image: np.ndarray, M: float, A: float, k1: float, k2: float, mask: np.ndarray = None
) -> np.ndarray:
    """Converts Landsat thermal band Digital Numbers (DN) to brightness temperature.

    Args:
        image (np.ndarray): Level 1 quantized and calibrated scaled Digital Numbers
                            (DN) TIR band data (e.g Band 10 landsat 8 data).
        M (float): Band-specific multiplicative rescaling factor from the image
                   folder metadata (RADIANCE_MULT_BAND_x, where x is the band number).
        A (float): Band-specific additive rescaling factor from the image
                   folder metadata (RADIANCE_ADD_BAND_x, where x is the band number).
        k1 (float): Band-specific thermal conversion constant from the image
                    folder metadata (K1_CONSTANT_BAND_x, where x is the thermal band number).
        k2 (float): Band-specific thermal conversion constant from the image
                    folder metadata (K2_CONSTANT_BAND_x, where x is the thermal band number).
        mask (np.ndarray, optional): Boolean mask to identify NaN or irregular values
                                     for masking purposes.

    Returns:
        np.ndarray: Brightness temperature-corrected Landsat image.
    """
    
    # Convert raw digital numbers to top-of-atmoshere radiance
    toa_radiance = (M * image) + A
    
    #  Compute brightness temperature using the Plank radiation law
    brightness_temp = k2 / np.log((k1 / toa_radiance) + 1)
    
    
    # Apply optional mask to handle NaN or irregular values
    if mask is not None:
        brightness_temp[mask] = np.nan

    return brightness_temp
