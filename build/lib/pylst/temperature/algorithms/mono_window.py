import numpy as np
from pylst.exceptions import assert_required_keywords_provided

# Credit to the original author: Oladimeji Mudele (pylandtemp)
# Original source: https://github.com/pylandtemp/pylandtemp

class MonoWindowLST:
    def __init__(self):
        """
        Method reference:
        Avdan, Ugur, and Gordana Jovanovska. "Algorithm for automated mapping of land surface
        temperature using LANDSAT 8 satellite data." Journal of sensors 2016 (2016).

        Initializes the Mono-window Land Surface Temperature (LST) computation algorithm.

        Attributes:
            max_earth_temp (float): Maximum possible Earth temperature in Kelvin.
        """
        self.max_earth_temp = 273.15 + 56.7

    def __call__(self, **kwargs) -> np.ndarray:
        """
        Compute land surface temperature using the Mono-window algorithm.

        Args:
            emissivity_10 (np.ndarray): Emissivity image obtained for band 10
            brightness_temperature_10 (np.ndarray): Brightness temperature image obtained for band 10
            mask (np.ndarray[bool]): Mask image. Output will have NaN value where mask is True.

        Returns:
            np.ndarray: Land surface temperature image
        """
        self._validate_inputs(**kwargs)
        return self._compute_lst_mono_window(**kwargs)

    def _validate_inputs(self, **kwargs):
        """
        Validate input parameters for the Mono-window LST computation.

        Args:
            **kwargs: Keyword arguments containing necessary input images.

        Raises:
            ValueError: If input images have different sizes.
        """
        
        required_keywords = ["brightness_temperature_10", "emissivity_10", "mask"]
        assert_required_keywords_provided(required_keywords, **kwargs)
        temperature_band = kwargs["brightness_temperature_10"]
        emissivity = kwargs["emissivity_10"]
        mask = kwargs["mask"]

        if not (mask.shape == temperature_band.shape == emissivity.shape):
            raise ValueError("Input images must be of the same size/shape")

    def _compute_lst_mono_window(self, **kwargs) -> np.ndarray:
        """
        Compute land surface temperature using the Mono-window algorithm.

        Args:
            **kwargs: Keyword arguments containing necessary input images.

        Returns:
            np.ndarray: Land surface temperature image.
        """
        temperature_band = kwargs["brightness_temperature_10"]
        emissivity = kwargs["emissivity_10"]
        mask = kwargs["mask"]

        land_surface_temp = temperature_band / (
            1 + (((0.0000115 * temperature_band) / 14380) * np.log(emissivity))
        )
        land_surface_temp[mask] = np.nan
        land_surface_temp[land_surface_temp > self.max_earth_temp] = np.nan
        return land_surface_temp
