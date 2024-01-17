import numpy as np
from .utils import compute_brightness_temperature

# Credit to the original author: Oladimeji Mudele (pylandtemp)
# Original source: https://github.com/pylandtemp/pylandtemp

class BrightnessTemperatureLandsat:
    def __init__(self):
        # Constants for brightness temperature calculation
        self.constants = {
            "band_10": {"k1": 774.89, "k2": 1321.08},
            "band_11": {"k1": 480.89, "k2": 1201.14},
            "mult_factor": 0.0003342,
            "add_factor": 0.1,
        }

    def __call__(self, band_10: np.ndarray, band_11: np.ndarray = None, mask=None) -> np.ndarray:
        """
        Calculate brightness temperature for Landsat bands 10 and 11.

        Args:
            band_10 (np.ndarray): Level 1 quantized and calibrated scaled Digital Numbers (DN) TIR band data for Band 10 landsat 8 data.
            band_11 (np.ndarray): Level 1 quantized and calibrated scaled Digital Numbers (DN) TIR band data for Band 11 landsat 8 data.
            mask (bool): Mask zero or NaN values. Defaults to True.

        Returns:
            Tuple(np.ndarray, np.ndarray): Band 10 brightness temperature, Band 11 brightness temperature.
        """
        # Compute brightness temperature for Band 10
        tb_band_10 = self._compute_brightness_temp(band_10, "band_10", mask)
        tb_band_11 = None

        if band_11 is not None:
            # Compute brightness temperature for band 11 if available
            tb_band_11 = self._compute_brightness_temp(band_11, "band_11", mask)

        return tb_band_10, tb_band_11

    def _compute_brightness_temp(self, image: np.ndarray, band: str, mask: np.ndarray) -> np.ndarray:
        """Converts image raw digital numbers to brightness temperature.

        Args:
            image (np.ndarray): Band image data.
            band (str): Band identifier.
            mask (n.ndarray[bool]): True for pixels to mask out.

        Returns:
            np.ndarray: Brightness temperature corrected image.
        """
        k1 = self.constants[band]["k1"]
        k2 = self.constants[band]["k2"]
        mult_factor = self.constants["mult_factor"]
        add_factor = self.constants["add_factor"]
        
        # Use utility function to compute brightness temperature
        return compute_brightness_temperature(image, mult_factor, add_factor, k1, k2, mask)
