from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
from numpy.typing import NDArray


def generate_mask(
    image: NDArray[np.number],
    /,
) -> NDArray[np.bool_]:
    """
    Create a valid-data mask (True = valid pixel, False = mask out / invalid).

    Masks out exact zero values and NaN — the two most common nodata representations
    in Landsat Level-1/Level-2 products.

    Parameters
    ----------
    image : ndarray
        Any numeric single-band array (reflectance, radiance, temperature, etc.).

    Returns
    -------
    ndarray[bool]
        Boolean mask with same shape as input (True = keep this pixel).
    """
    return (image != 0) & ~np.isnan(image)


def compute_ndvi(
    nir: NDArray[np.floating],
    red: NDArray[np.floating],
    *,
    eps: float = 1e-10,
    mask: Optional[NDArray[np.bool_]] = None,
    clip_range: bool = True,
) -> NDArray[np.float32]:
    """
    Compute Normalized Difference Vegetation Index (NDVI).

    NDVI = (NIR − Red) / (NIR + Red)

    Parameters
    ----------
    nir : ndarray[float]
        Near-infrared band
    red : ndarray[float]
        Red band
    eps : float, optional
        Small value added to denominator to avoid division by zero
    mask : ndarray[bool], optional
        Additional mask where True = invalid → set NDVI to NaN
    clip_range : bool, default True
        Whether to enforce physical range [-1, 1] by setting out-of-range values to NaN

    Returns
    -------
    ndarray[float32]
        NDVI array (same shape as inputs)
    """
    if nir.shape != red.shape:
        raise ValueError(f"Band shapes do not match: NIR {nir.shape}, Red {red.shape}")

    denominator = nir + red
    ndvi = np.divide(
        nir - red,
        denominator,
        out=np.full_like(denominator, np.nan, dtype=np.float32),
        where=denominator != 0,
    )

    # Avoid tiny negative zeros turning into -0.0
    ndvi = np.nan_to_num(ndvi, nan=np.nan, posinf=np.nan, neginf=np.nan)

    if clip_range:
        ndvi[(ndvi < -1) | (ndvi > 1)] = np.nan

    if mask is not None:
        if mask.shape != ndvi.shape:
            raise ValueError(f"Mask shape {mask.shape} does not match NDVI shape {ndvi.shape}")
        ndvi[mask] = np.nan

    return ndvi


def fractional_vegetation_cover(
    ndvi: NDArray[np.floating],
    ndvi_soil: float = 0.2,
    ndvi_veg: float = 0.5,
    clip: bool = True,
) -> NDArray[np.float32]:
    """
    Estimate fractional vegetation cover (FVC) from NDVI.

    Classic parameterization widely used in LST literature:
        FVC = [(NDVI − NDVI_soil) / (NDVI_veg − NDVI_soil)]²

    Parameters
    ----------
    ndvi : ndarray
        NDVI values (typically in [-1, 1])
    ndvi_soil : float, optional
        NDVI value for bare soil (default 0.2)
    ndvi_veg : float, optional
        NDVI value for dense vegetation (default 0.5)
    clip : bool, default True
        Whether to force result into [0, 1]

    Returns
    -------
    ndarray[float32]
        Fractional vegetation cover [0, 1] or NaN
    """
    if ndvi.ndim != 2:
        raise ValueError(f"NDVI must be 2D, got shape {ndvi.shape}")

    if ndvi_veg <= ndvi_soil:
        raise ValueError("ndvi_veg must be > ndvi_soil")

    diff = ndvi_veg - ndvi_soil
    fvc = ((ndvi - ndvi_soil) / diff) ** 2

    fvc = np.where(np.isfinite(fvc), fvc, np.nan).astype(np.float32)

    if clip:
        fvc = np.clip(fvc, 0.0, 1.0)

    return fvc


def cavity_effect(
    emissivity_veg: float,
    emissivity_soil: float,
    fvc: NDArray[np.floating],
    geom_factor: float = 0.55,
) -> NDArray[np.float32]:
    """
    Compute cavity correction term for effective emissivity (NDVI-based method).

        ε_cavity = (1 − ε_soil) × ε_veg × geom_factor × (1 − FVC)

    Parameters
    ----------
    emissivity_veg : float
        Vegetation emissivity (typical range 0.98–0.99)
    emissivity_soil : float
        Soil/background emissivity (typical range 0.92–0.96)
    fvc : ndarray
        Fractional vegetation cover [0, 1]
    geom_factor : float, optional
        Geometric configuration factor (0.55 is common isotropic assumption)

    Returns
    -------
    ndarray[float32]
        Cavity effect correction term (same shape as fvc)
    """
    if not (0 <= fvc.min() <= fvc.max() <= 1):
        warnings.warn(
            "Some FVC values are outside [0, 1]. Results may be unreliable.",
            UserWarning,
            stacklevel=2,
        )

    cavity = (1 - emissivity_soil) * emissivity_veg * geom_factor * (1 - fvc)
    return cavity.astype(np.float32)


def rescale_band(
    image: NDArray[np.number],
    scale: float = 2.0e-5,
    offset: float = 0.1,
) -> NDArray[np.float32]:
    """
    Apply Landsat Collection 2 surface reflectance / TOA scaling.

    reflectance = image × scale + offset

    Parameters
    ----------
    image : ndarray
        Raw pixel values (usually uint16 or int16)
    scale : float, optional
        Multiplicative factor (Collection 2 SR default = 2.0e-5)
    offset : float, optional
        Additive offset (Collection 2 SR default = 0.1)

    Returns
    -------
    ndarray[float32]
        Scaled reflectance values (typically ~[0, 1])
    """
    return (image.astype(np.float32) * scale) + offset