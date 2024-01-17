import numpy as np
from pylst.exceptions import assert_required_keywords_provided
from pylst.utils import fractional_vegetation_cover

# Credit to the original author: Oladimeji Mudele (pylandtemp)
# Original source: https://github.com/pylandtemp/pylandtemp

class SplitWindowParentLST:
    def __init__(self):
        # Maximum Earth temperature for clipping the calculated LST
        self.max_earth_temp = 273.15 + 56.7

    def __call__(self, **kwargs) -> np.ndarray:
        # Calculate LST and clip values exceeding the maximum Earth temperature
        lst = self._compute_lst(**kwargs)
        lst[lst > self.max_earth_temp] = np.nan
        return lst

    def _compute_lst(self, **kwargs):
        # Abstract method for computing LST, to be implemented in derived classes
        raise NotImplementedError("Concrete method yet to be implemented")


class SplitWindowJiminezMunozLST(SplitWindowParentLST):
    cwv = 0.013

    def _compute_lst(self, **kwargs) -> np.ndarray:
        # Concrete implementation for Jiminez-Munoz method
        required_keywords = [
            "emissivity_10",
            "emissivity_11",
            "brightness_temperature_10",
            "brightness_temperature_11",
            "mask",
        ]
        assert_required_keywords_provided(required_keywords, **kwargs)
        
        # Extracting required input parameters
        tb_10 = kwargs["brightness_temperature_10"]
        tb_11 = kwargs["brightness_temperature_11"]
        emissivity_10 = kwargs["emissivity_10"]
        emissivity_11 = kwargs["emissivity_11"]
        mask = kwargs["mask"]
        
        # Computing LST using Jiminez-Munoz method
        mean_e = (emissivity_10 + emissivity_11) / 2
        diff_e = emissivity_10 - emissivity_11
        diff_tb = tb_10 - tb_11

        lst = (
            tb_10
            + (1.387 * diff_tb)
            + (0.183 * (diff_tb ** 2))
            - 0.268
            + ((54.3 - (2.238 * self.cwv)) * (1 - mean_e))
            + ((-129.2 + (16.4 * self.cwv)) * diff_e)
        )
        lst[mask] = np.nan
        return lst


class SplitWindowKerrLST(SplitWindowParentLST):
    """
    Method reference:

    Kerr Y, Lagouarde J, Nerry F, Ottlé C (2004) Land surface temperature
    retrieval techniques and applications: case of the AVHRR. Thermal remote
    sensing in land surface processing. CRC Press, New York, pp 55–131
    """

    def _compute_lst(self, **kwargs) -> np.ndarray:
        """
        Computes the Land Surface Temperature (LST) using the Split Window method based on Kerr et al. (2004).

        Args:
            brightness_temperature_10 (np.ndarray): Brightness temperature image obtained for band 10
            brightness_temperature_11 (np.ndarray): Brightness temperature image obtained for band 11
            ndvi (np.ndarray): NDVI image
            mask (np.ndarray[bool]): Mask image. Output will have NaN value where the mask is True.

        Returns:
            np.ndarray: Land surface temperature image
        """
        # Ensure that required keyword arguments are provided
        required_keywords = [
            "brightness_temperature_10",
            "brightness_temperature_11",
            "ndvi",
            "mask",
        ]
        assert_required_keywords_provided(required_keywords, **kwargs)
        
        # Retrieve required input data
        tb_10 = kwargs["brightness_temperature_10"]
        tb_11 = kwargs["brightness_temperature_11"]
        ndvi = kwargs["ndvi"]
        mask = kwargs["mask"]
        
        # Calculate fractional vegetation cover (pv) using NDVI
        pv = fractional_vegetation_cover(ndvi)

        # Compute Land Surface Temperature (LST) using the Kerr et al. (2004) formula
        lst = (
            (tb_10 * ((0.5 * pv) + 3.1))
            + (tb_11 * ((-0.5 * pv) - 2.1))
            - ((5.5 * pv) + 3.1)
        )
        
        # Mask out invalid values based on the provided mask
        lst[mask] = np.nan
        
        return lst


class SplitWindowMcMillinLST(SplitWindowParentLST):
    """
    Method reference:
    McMillin LM (1975) Estimation of sea surface temperatures
    from two infrared window measurements with different absorption.
    J Geophys Res 80(36):5113–5117. https://doi.org/10.1029/JC080i036p05113
    """

    def _compute_lst(self, **kwargs) -> np.ndarray:
        """
        Computes the land surface temperature using McMillin's method.

        Args:
            **brightness_temperature_10 (np.ndarray): Brightness temperature image obtained for band 10
            **brightness_temperature_11 (np.ndarray): Brightness temperature image obtained for band 11
            **mask (np.ndarray[bool]): Mask image. Output will have NaN values where the mask is True.

        Returns:
            np.ndarray: Land surface temperature image
        """
        # Check if required keywords are provided
        required_keywords = [
            "brightness_temperature_10",
            "brightness_temperature_11",
            "mask",
        ]
        assert_required_keywords_provided(required_keywords, **kwargs)

        # Extracting input variables
        tb_10 = kwargs["brightness_temperature_10"]
        tb_11 = kwargs["brightness_temperature_11"]
        mask = kwargs["mask"]

        # McMillin's land surface temperature computation
        lst = (1.035 * tb_10) + (3.046 * (tb_10 - tb_11)) - 10.93

        # Masking areas where the mask is True
        lst[mask] = np.nan

        return lst



class SplitWindowPriceLST(SplitWindowParentLST):
    """
    Method reference:
    Price JC (1984) Land surface temperature measurements from the split window
    channels of the NOAA advanced very high-resolution radiometer. J Geophys Res 89:7231–7237.
    https://doi.org/10.1029/JD089iD05p07231
    """

    def _compute_lst(self, **kwargs) -> np.ndarray:
        """
        Computes Land Surface Temperature (LST) using the split window Price method.

        Args:
            **kwargs (dict): Keyword arguments containing necessary input arrays.
                             Required keywords: "emissivity_10", "emissivity_11",
                             "brightness_temperature_10", "brightness_temperature_11", "mask".

        Returns:
            np.ndarray: Land Surface Temperature (LST) array.
        """
        required_keywords = [
            "emissivity_10",
            "emissivity_11",
            "brightness_temperature_10",
            "brightness_temperature_11",
            "mask",
        ]
        assert_required_keywords_provided(required_keywords, **kwargs)

        # Extracting required arrays from kwargs
        tb_10 = kwargs["brightness_temperature_10"]
        tb_11 = kwargs["brightness_temperature_11"]
        emm_10 = kwargs["emissivity_10"]
        emm_11 = kwargs["emissivity_11"]
        mask = kwargs["mask"]

        # Computing LST using the Price method formula
        lst = (tb_10 + 3.33 * (tb_10 - tb_11)) * ((5.5 - emm_10) / 4.5) + (
            0.75 * tb_11 * (emm_10 - emm_11)
        )
        
        # Masking invalid values in the result array
        lst[mask] = np.nan
        return lst



class SplitWindowSobrino1993LST(SplitWindowParentLST):
    """
    Method reference:

    Sobrino JA, Caselles V, Coll C (1993) Theoretical split window algorithms
    for determining the actual surface temperature. I1Nuovo Cimento 16:219–236.
    https://doi.org/10.1007/BF02524225

    This class implements the Split Window algorithm based on the Sobrino 1993 method.
    The algorithm computes the land surface temperature (LST) using brightness temperatures
    and emissivity values for Landsat 8 bands 10 and 11.
    """

    def _compute_lst(self, **kwargs) -> np.ndarray:
        # Define the required keywords for the algorithm
        required_keywords = [
            "emissivity_10",
            "emissivity_11",
            "brightness_temperature_10",
            "brightness_temperature_11",
            "mask",
        ]
        # Ensure that all required keywords are provided
        assert_required_keywords_provided(required_keywords, **kwargs)

        # Retrieve necessary data from the provided keyword arguments
        tb_10 = kwargs["brightness_temperature_10"]
        tb_11 = kwargs["brightness_temperature_11"]
        emm_10 = kwargs["emissivity_10"]
        emm_11 = kwargs["emissivity_11"]
        mask = kwargs["mask"]

        # Calculate the temperature difference between tb_10 and tb_11
        diff_tb = tb_10 - tb_11
        # Calculate the emissivity difference between emm_10 and emm_11
        diff_e = emm_10 - emm_11

        # Compute the land surface temperature (LST) using the Sobrino 1993 formula
        lst = (
            tb_10
            + (1.06 * diff_tb)
            + (0.46 * diff_tb ** 2)
            + (53 * (1 - emm_10))
            - (53 * diff_e)
        )
        # Mask invalid pixels based on the provided mask, setting their values to NaN
        lst[mask] = np.nan
        return lst


