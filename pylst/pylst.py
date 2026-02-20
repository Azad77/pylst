# pylst/pylst.py
import numpy as np

from .temperature import default_algorithms as temperature_algorithms
from .emissivity import emissivity_runner, EmissivityRunner
from .utils import compute_ndvi
from .exceptions import InputShapesMismatchError, InvalidMaskError


def split_window(
    landsat_band_10: np.ndarray,
    landsat_band_11: np.ndarray,
    landsat_band_4: np.ndarray,
    landsat_band_5: np.ndarray,
    lst_method: str,
    emissivity_method: str,
    unit: str = "kelvin",
) -> np.ndarray:
    """Compute Land Surface Temperature using split window method."""
    
    if not (
        landsat_band_10.shape
        == landsat_band_11.shape
        == landsat_band_5.shape
        == landsat_band_4.shape
    ):
        raise InputShapesNotEqual(
            f"Shapes of input images should be equal: {landsat_band_10.shape}, "
            f"{landsat_band_11.shape}, {landsat_band_4.shape}, {landsat_band_5.shape}"
        )

    mask = landsat_band_10 == 0
    ndvi_image = compute_ndvi(landsat_band_5, landsat_band_4, mask)

    brightness_temp_10, brightness_temp_11 = Runner(algorithms=temperature_algorithms["split_window"])(
        lst_method, landsat_band_10=landsat_band_10, landsat_band_11=landsat_band_11, mask=mask
    )

    emissivity_10, emissivity_11 = emissivity_runner.run(
        method=emissivity_method, ndvi=ndvi_image, red_band=landsat_band_4
    )

    lst_image = Runner(algorithms=temperature_algorithms["split_window"])(
        lst_method,
        emissivity_10=emissivity_10,
        emissivity_11=emissivity_11,
        brightness_temperature_10=brightness_temp_10,
        brightness_temperature_11=brightness_temp_11,
        mask=mask,
        ndvi=ndvi_image,
    )

    return lst_image


def single_window(
    landsat_band_10: np.ndarray,
    landsat_band_4: np.ndarray,
    landsat_band_5: np.ndarray,
    lst_method: str = "mono-window",
    emissivity_method: str = "avdan",
    unit: str = "kelvin",
) -> np.ndarray:
    """Compute LST using single window (mono-window) method."""

    if not landsat_band_10.shape == landsat_band_5.shape == landsat_band_4.shape:
        raise InputShapesNotEqual(
            f"Shapes of input images should be equal: {landsat_band_10.shape}, "
            f"{landsat_band_4.shape}, {landsat_band_5.shape}"
        )

    mask = landsat_band_10 == 0
    ndvi_image = compute_ndvi(landsat_band_5, landsat_band_4, mask)

    brightness_temp_10, _ = Runner(algorithms=temperature_algorithms["single_window"])(
        lst_method, landsat_band_10=landsat_band_10, mask=mask
    )

    emissivity_10, _ = emissivity_runner.run(
        method=emissivity_method, ndvi=ndvi_image, red_band=landsat_band_4
    )

    lst_image = Runner(algorithms=temperature_algorithms["single_window"])(
        lst_method,
        emissivity_10=emissivity_10,
        brightness_temperature_10=brightness_temp_10,
        mask=mask,
        ndvi=ndvi_image,
    )

    return lst_image


def emissivity(ndvi_image: np.ndarray, landsat_band_4: np.ndarray = None, emissivity_method: str = "avdan"):
    """Compute emissivity for given NDVI and optional red band."""
    if landsat_band_4 is not None and ndvi_image.shape != landsat_band_4.shape:
        raise InputShapesMismatchError(
            f"Shapes of input images should be equal: {ndvi_image.shape}, {landsat_band_4.shape}"
        )


    emissivity_10, emissivity_11 = emissivity_runner.run(
        method=emissivity_method, ndvi=ndvi_image, red_band=landsat_band_4
    )
    return emissivity_10, emissivity_11


def ndvi(landsat_band_5: np.ndarray, landsat_band_4: np.ndarray, mask: np.ndarray):
    """Compute NDVI."""
    if not landsat_band_5.shape == landsat_band_4.shape:
        raise InputShapesNotEqual(
            f"Shapes of input images should be equal: {landsat_band_5.shape}, {landsat_band_4.shape}"
        )

    if mask.dtype != "bool":
        raise InvalidMaskError("Mask must be a boolean array")

    return compute_ndvi(landsat_band_5, landsat_band_4, mask)


def brightness_temperature(
    landsat_band_10: np.ndarray,
    landsat_band_11: np.ndarray = None,
    mask: np.ndarray = None,
):
    """Compute brightness temperature from Landsat bands."""
    from .temperature import BrightnessTemperatureLandsat

    if landsat_band_11 is not None and landsat_band_10.shape != landsat_band_11.shape:
        raise InputShapesNotEqual(
            f"Shapes of input images should be equal: {landsat_band_10.shape}, {landsat_band_11.shape}"
        )

    if mask is not None and mask.dtype != "bool":
        raise InvalidMaskError("Mask must be a boolean array")

    brightness_temp_10, brightness_temp_11 = BrightnessTemperatureLandsat()(
        landsat_band_10, landsat_band_11, mask=mask
    )
    return brightness_temp_10, brightness_temp_11
