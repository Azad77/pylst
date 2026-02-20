from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
from numpy.typing import NDArray


def compute_brightness_temperature(
    dn: NDArray[np.number],
    mult_factor: float,
    add_factor: float,
    k1: float,
    k2: float,
    *,
    mask: Optional[NDArray[np.bool_]] = None,
    nodata_value: Optional[float] = None,
    dtype: type = np.float32,
) -> NDArray[np.float32]:
    """
    Convert Landsat thermal band digital numbers (DN) to at-sensor brightness temperature (Kelvin).

    This function implements the standard USGS Landsat Collection 2 Level-1 thermal radiance
    to brightness temperature conversion:

        1. Radiance = mult_factor × DN + add_factor
        2. Brightness Temperature = K2 / ln(K1 / Radiance + 1)

    Args:
        dn: Array of Level-1 quantized and calibrated scaled digital numbers (DN)
            (typically uint16 for Landsat 8/9 Collection 2 Band 10 or 11).
        mult_factor: Band-specific multiplicative rescaling factor
                     (RADIANCE_MULT_BAND_x from MTL metadata).
        add_factor: Band-specific additive rescaling factor
                    (RADIANCE_ADD_BAND_x from MTL metadata).
        k1: Band-specific thermal constant K1 (K1_CONSTANT_BAND_x from MTL).
        k2: Band-specific thermal constant K2 (K2_CONSTANT_BAND_x from MTL).
        mask: Optional boolean mask where True = invalid pixels → set to NaN.
        nodata_value: Optional single value representing no-data in the input DN array.
        dtype: Output data type (default float32 to save memory; use float64 if needed).

    Returns:
        Brightness temperature array in Kelvin (same shape as input dn).

    Notes:
        - For Landsat 8/9 Collection 2 Level-1 thermal bands, typical values are:
            mult_factor ≈ 3.3420E-04
            add_factor  ≈ 0.10000
        - K1 and K2 are band-specific (different for band 10 and 11).
        - Invalid radiance values (≤ 0) or log-domain errors are automatically set to NaN.
    """
    # Ensure input is floating point for calculations
    dn = dn.astype(np.float64, copy=False)

    # Create invalid mask
    invalid = ~np.isfinite(dn) | (dn <= 0)

    if nodata_value is not None:
        invalid |= (dn == nodata_value)

    if mask is not None:
        if mask.shape != dn.shape:
            raise ValueError("mask shape must match input dn shape")
        if mask.dtype != np.bool_:
            warnings.warn("mask was not boolean → converting", UserWarning, stacklevel=2)
            mask = mask.astype(bool, copy=False)
        invalid |= mask

    # Compute top-of-atmosphere spectral radiance
    radiance = mult_factor * dn + add_factor

    # Protect against log(0) or negative radiance
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        brightness_temp = k2 / np.log(k1 / radiance + 1.0)

    # Apply invalid mask
    brightness_temp[invalid] = np.nan

    # Final type cast
    return brightness_temp.astype(dtype, copy=False)


def compute_brightness_temperature_l8_l9(
    band10: NDArray[np.number],
    band11: Optional[NDArray[np.number]] = None,
    *,
    mult_factor: float = 3.3420e-4,
    add_factor: float = 0.1,
    k1_band10: float = 774.8853,
    k2_band10: float = 1321.0789,
    k1_band11: float = 480.8883,
    k2_band11: float = 1201.1442,
    mask: Optional[NDArray[np.bool_]] = None,
    nodata_value: Optional[float] = None,
) -> tuple[NDArray[np.float32], Optional[NDArray[np.float32]]]:
    """
    Convenience function for Landsat 8 & 9 TIRS bands (10 & 11).

    Uses Collection 2 default constants when no custom values are provided.

    Returns:
        (brightness_temp_band10, brightness_temp_band11 or None)
    """
    tb10 = compute_brightness_temperature(
        dn=band10,
        mult_factor=mult_factor,
        add_factor=add_factor,
        k1=k1_band10,
        k2=k2_band10,
        mask=mask,
        nodata_value=nodata_value,
    )

    if band11 is not None:
        tb11 = compute_brightness_temperature(
            dn=band11,
            mult_factor=mult_factor,
            add_factor=add_factor,
            k1=k1_band11,
            k2=k2_band11,
            mask=mask,
            nodata_value=nodata_value,
        )
        return tb10, tb11

    return tb10, None