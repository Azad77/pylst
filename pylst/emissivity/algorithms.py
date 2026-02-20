import numpy as np
from numpy.typing import NDArray
from typing import Optional, Tuple

from ..utils import rescale_band, cavity_effect, fractional_vegetation_cover

# Credit to the original author: Oladimeji Mudele (pylandtemp)
# Original source: https://github.com/pylandtemp/pylandtemp


class Emissivity:
    """
    Parent class for all emissivity estimation methods.
    Provides common utilities for NDVI classification and FVC computation.
    """

    def __init__(self):
        self.ndvi_min = -1.0
        self.ndvi_max = 1.0
        self.baresoil_ndvi_max = 0.2
        self.vegetation_ndvi_min = 0.5   # fixed typo

    def __call__(self, **kwargs) -> Tuple[Optional[NDArray[np.float32]], Optional[NDArray[np.float32]]]:
        """
        Main entry point to compute emissivity.

        Required:
            ndvi (np.ndarray): NDVI image

        Optional:
            red_band (np.ndarray): Red band (required only for some methods)
            mask (np.ndarray[bool]): Mask where True = invalid pixels → set to NaN

        Returns:
            Tuple of (emissivity band 10, emissivity band 11)
            Second value may be None for single-band methods
        """
        if "ndvi" not in kwargs:
            raise ValueError("NDVI image is required")

        self.ndvi = kwargs["ndvi"].astype(np.float32)
        self.red_band = kwargs.get("red_band")
        self.mask = kwargs.get("mask")

        if self.red_band is not None:
            self.red_band = self.red_band.astype(np.float32)
            if self.ndvi.shape != self.red_band.shape:
                raise ValueError("NDVI and red_band must have the same shape")

        if self.mask is not None:
            if self.mask.shape != self.ndvi.shape:
                raise ValueError("Mask shape must match NDVI shape")

        emm_10, emm_11 = self._compute_emissivity()

        # Apply common post-processing
        emm_10 = np.where(emm_10 == 0, np.nan, emm_10)

        if emm_11 is not None:
            emm_11 = np.where(emm_11 == 0, np.nan, emm_11)

        if self.mask is not None:
            emm_10[self.mask] = np.nan
            if emm_11 is not None:
                emm_11[self.mask] = np.nan

        return emm_10, emm_11

    def _compute_emissivity(self) -> Tuple[NDArray[np.float32], Optional[NDArray[np.float32]]]:
        """Abstract method – must be implemented by subclasses"""
        raise NotImplementedError("No concrete implementation of emissivity method yet")

    def _get_land_surface_mask(self) -> dict[str, NDArray[np.bool_]]:
        """Return boolean masks for bare soil, vegetation, and mixed pixels"""
        mask_baresoil = (self.ndvi >= self.ndvi_min) & (self.ndvi < self.baresoil_ndvi_max)
        mask_vegetation = (self.ndvi >= self.vegetation_ndvi_min) & (self.ndvi <= self.ndvi_max)
        mask_mixed = (self.ndvi >= self.baresoil_ndvi_max) & (self.ndvi < self.vegetation_ndvi_min)

        return {
            "baresoil": mask_baresoil,
            "vegetation": mask_vegetation,
            "mixed": mask_mixed,
        }

    def _get_landcover_mask_indices(self) -> dict[str, tuple[NDArray[np.int_], NDArray[np.int_]]]:
        """Return indices (row, col) for each land cover class"""
        masks = self._get_land_surface_mask()
        return {
            "baresoil": np.where(masks["baresoil"]),
            "vegetation": np.where(masks["vegetation"]),
            "mixed": np.where(masks["mixed"]),
        }

    def _compute_fvc(self) -> NDArray[np.float32]:
        """Compute fractional vegetation cover from NDVI"""
        return fractional_vegetation_cover(self.ndvi)


class ComputeMonoWindowEmissivity(Emissivity):
    """
    Mono-window NDVI-based emissivity (Avdan & Jovanovska, 2016 style)
    """

    emissivity_soil_10 = 0.97
    emissivity_veg_10 = 0.99
    emissivity_soil_11 = None
    emissivity_veg_11 = None

    def _compute_emissivity(self) -> Tuple[NDArray[np.float32], None]:
        emm = np.full_like(self.ndvi, np.nan, dtype=np.float32)
        indices = self._get_landcover_mask_indices()

        # Bare soil
        emm[indices["baresoil"]] = self.emissivity_soil_10

        # Vegetation
        emm[indices["vegetation"]] = self.emissivity_veg_10

        # Mixed
        mixed = indices["mixed"]
        if len(mixed[0]) > 0:
            fvc_mixed = ((self.ndvi[mixed] - 0.2) / (0.5 - 0.2)) ** 2
            emm[mixed] = 0.004 * fvc_mixed + 0.986

        return emm, None


class ComputeEmissivityNBEM(Emissivity):
    """
    NDVI-based emissivity with red-band regression for bare soil (NBEM style)
    References:
    - Li & Meng (2018), Landscape and Urban Planning
    - Yu et al. (2014), Remote Sensing
    """

    emissivity_soil_10 = 0.9668
    emissivity_veg_10 = 0.9863
    emissivity_soil_11 = 0.9747
    emissivity_veg_11 = 0.9896

    def _compute_emissivity(self) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
        if self.red_band is None:
            raise ValueError("Red band is required for NBEM method")

        self.red_band = rescale_band(self.red_band)
        indices = self._get_landcover_mask_indices()
        fvc = self._compute_fvc()

        def calc_emissivity(
            emissivity_veg: float,
            emissivity_soil: float,
            red_a: float,
            red_b: float,
        ) -> NDArray[np.float32]:
            emm = np.full_like(self.ndvi, np.nan, dtype=np.float32)

            # Bare soil: red-band regression
            emm[indices["baresoil"]] = red_a - (red_b * self.red_band[indices["baresoil"]])

            # Mixed: weighted + cavity
            mixed = indices["mixed"]
            emm[mixed] = (
                emissivity_veg * fvc[mixed]
                + emissivity_soil * (1 - fvc[mixed])
                + cavity_effect(emissivity_veg, emissivity_soil, fvc[mixed])
            )

            # Vegetation
            emm[indices["vegetation"]] = emissivity_veg + cavity_effect(
                emissivity_veg, emissivity_soil, fvc[indices["vegetation"]]
            )

            return emm

        emm_10 = calc_emissivity(
            self.emissivity_veg_10, self.emissivity_soil_10, 0.973, 0.047
        )
        emm_11 = calc_emissivity(
            self.emissivity_veg_11, self.emissivity_soil_11, 0.984, 0.026
        )

        return emm_10, emm_11


class ComputeEmissivityGopinadh(Emissivity):
    """
    Simple NDVI-based linear mixing (Rongali et al., 2018)
    """

    emissivity_soil_10 = 0.971
    emissivity_veg_10 = 0.987
    emissivity_soil_11 = 0.977
    emissivity_veg_11 = 0.989

    def _compute_emissivity(self) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
        fvc = self._compute_fvc()
        indices = self._get_landcover_mask_indices()

        def calc_emissivity(
            emissivity_veg: float, emissivity_soil: float
        ) -> NDArray[np.float32]:
            emm = emissivity_soil * (1 - fvc) + emissivity_veg * fvc
            return emm

        emm_10 = calc_emissivity(self.emissivity_veg_10, self.emissivity_soil_10)
        emm_11 = calc_emissivity(self.emissivity_veg_11, self.emissivity_soil_11)

        return emm_10, emm_11


class ComputeNDVIThresholdEmissivity(Emissivity):
    """
    Classic NDVI Threshold Method (most common/standard for Landsat LST)

    Widely used when no external emissivity data is available.

    References:
    - Sobrino et al. (2004, 2008) – Landsat thermal retrieval
    - Valor & Caselles (1996) – vegetation fraction basis
    - Many recent Landsat 8/9 studies (2020–2026)

    Typical values:
    - ε_soil ≈ 0.97–0.98
    - ε_veg  ≈ 0.987–0.99
    - Cavity correction ≈ 0.004–0.01
    """

    def __init__(
        self,
        epsilon_soil_10: float = 0.971,
        epsilon_veg_10: float = 0.987,
        epsilon_soil_11: float = 0.977,
        epsilon_veg_11: float = 0.989,
        ndvi_soil: float = 0.2,
        ndvi_veg: float = 0.5,
        cavity_factor: float = 0.004,
    ):
        super().__init__()
        self.baresoil_ndvi_max = ndvi_soil
        self.vegetation_ndvi_min = ndvi_veg

        self.emissivity_soil_10 = epsilon_soil_10
        self.emissivity_veg_10 = epsilon_veg_10
        self.emissivity_soil_11 = epsilon_soil_11
        self.emissivity_veg_11 = epsilon_veg_11
        self.cavity_factor = cavity_factor

    def _compute_emissivity(self) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
        fvc = self._compute_fvc()
        masks = self._get_land_surface_mask()

        emm_10 = np.full_like(self.ndvi, np.nan, dtype=np.float32)
        emm_11 = np.full_like(self.ndvi, np.nan, dtype=np.float32)

        # Bare soil
        emm_10[masks["baresoil"]] = self.emissivity_soil_10
        emm_11[masks["baresoil"]] = self.emissivity_soil_11

        # Vegetation
        emm_10[masks["vegetation"]] = self.emissivity_veg_10
        emm_11[masks["vegetation"]] = self.emissivity_veg_11

        # Mixed pixels
        mixed = masks["mixed"]
        if np.any(mixed):
            pv = fvc[mixed]
            emm_10[mixed] = (
                self.emissivity_veg_10 * pv
                + self.emissivity_soil_10 * (1 - pv)
                + self.cavity_factor * pv * (1 - pv)
            )
            emm_11[mixed] = (
                self.emissivity_veg_11 * pv
                + self.emissivity_soil_11 * (1 - pv)
                + self.cavity_factor * pv * (1 - pv)
            )

        return emm_10, emm_11