from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np
from numpy.typing import NDArray


SensorType = Literal["landsat5", "landsat7", "landsat8", "landsat9"]


@dataclass(frozen=True)
class ThermalConstants:
    """Container for thermal band calibration constants (Planck equation)."""
    k1: float
    k2: float


@dataclass
class BrightnessTemperatureCalculator:
    """
    Calculator for at-sensor brightness temperature (Kelvin) from Landsat thermal bands.

    Supports Landsat 5 (TM), 7 (ETM+), 8 & 9 (TIRS) Collection 2 Level-1 data.

    For maximum accuracy:
    - Use scene-specific values from the MTL.txt file (via custom_constants)
    - Landsat 8/9 use multiplicative/additive scaling
    - Landsat 5/7 use LMIN/LMAX scaling (older convention)

    References / origins:
    - USGS Landsat Collection 2 Level-1 documentation
    - pylandtemp (original inspiration): https://github.com/pylandtemp/pylandtemp
    """

    sensor: SensorType = "landsat8"
    gain: Literal["low", "high"] | None = None  # Landsat 7 only
    custom_constants: Optional[dict] = None

    def __post_init__(self):
        self.sensor = self.sensor.lower()
        if self.sensor not in {"landsat5", "landsat7", "landsat8", "landsat9"}:
            raise ValueError(
                f"Unsupported sensor: {self.sensor!r}. "
                "Supported: 'landsat5', 'landsat7', 'landsat8', 'landsat9'"
            )

        if self.sensor == "landsat7":
            if self.gain not in {"low", "high", None}:
                raise ValueError("For Landsat 7, gain must be 'low' or 'high'")
            self.gain = self.gain or "low"  # default to low gain

        # Set constants
        if self.custom_constants is not None:
            self.constants = self.custom_constants
            self.scaling_method = "custom"
        else:
            self.constants = self._get_default_constants()
            self.scaling_method = "mult_add" if self.sensor in {"landsat8", "landsat9"} else "lmin_lmax"

    def _get_default_constants(self) -> dict:
        """Default constants from USGS Collection 2 documentation."""
        if self.sensor in {"landsat8", "landsat9"}:
            return {
                "mult_factor": 3.3420e-4,
                "add_factor": 0.1,
                "band10": ThermalConstants(k1=774.8853, k2=1321.0789),
                "band11": ThermalConstants(k1=480.8883, k2=1201.1442),
            }
        elif self.sensor == "landsat7":
            if self.gain == "low":
                return {"lmin": 0.0, "lmax": 17.04, "k1": 666.09, "k2": 1282.71}
            else:  # high gain
                return {"lmin": 3.2, "lmax": 12.65, "k1": 671.62, "k2": 1284.30}
        elif self.sensor == "landsat5":
            return {"lmin": 1.182, "lmax": 15.303, "k1": 607.76, "k2": 1260.56}
        else:
            raise ValueError(f"No default constants for {self.sensor}")

    def __call__(
        self,
        primary: NDArray[np.number],
        secondary: Optional[NDArray[np.number]] = None,
        nodata_mask: Optional[NDArray[np.bool_]] = None,
        nodata_value: Optional[float] = None,
    ) -> tuple[NDArray[np.float32], Optional[NDArray[np.float32]]]:
        """
        Compute brightness temperature(s) in Kelvin.

        Args:
            primary: Primary thermal band DN values
                     (Band 10 for L8/9, Band 6 for L5/7)
            secondary: Optional secondary band (Band 11 for L8/9 only)
            nodata_mask: Boolean mask where True = invalid → set to NaN
            nodata_value: Single nodata value to mask (alternative to mask array)

        Returns:
            (tb_primary, tb_secondary or None)
        """
        primary = primary.astype(np.float64)

        if secondary is not None:
            if self.sensor not in {"landsat8", "landsat9"}:
                raise ValueError(f"Secondary band only supported for Landsat 8/9, got {self.sensor}")
            secondary = secondary.astype(np.float64)
            if primary.shape != secondary.shape:
                raise ValueError("Primary and secondary bands must have the same shape")

        # Create combined invalid mask
        invalid = ~np.isfinite(primary) | (primary <= 0)
        if nodata_value is not None:
            invalid |= (primary == nodata_value)
        if nodata_mask is not None:
            if nodata_mask.shape != primary.shape:
                raise ValueError("nodata_mask shape must match primary band")
            invalid |= nodata_mask

        # Compute radiance first
        if self.scaling_method == "mult_add":
            radiance_primary = (
                self.constants["mult_factor"] * primary
                + self.constants["add_factor"]
            )
            radiance_primary[invalid] = np.nan

            if secondary is not None:
                radiance_secondary = (
                    self.constants["mult_factor"] * secondary
                    + self.constants["add_factor"]
                )
                radiance_secondary[invalid] = np.nan
            else:
                radiance_secondary = None

            tb_primary = self._radiance_to_tb(
                radiance_primary,
                self.constants["band10"].k1,
                self.constants["band10"].k2,
            )

            tb_secondary = (
                self._radiance_to_tb(
                    radiance_secondary,
                    self.constants["band11"].k1,
                    self.constants["band11"].k2,
                )
                if radiance_secondary is not None
                else None
            )

        else:  # lmin_lmax (L5/L7)
            if secondary is not None:
                raise ValueError("Secondary band not supported for Landsat 5/7")

            lmin = self.constants["lmin"]
            lmax = self.constants["lmax"]
            # Assume DN is 0–255 if not scaled
            radiance = lmin + (lmax - lmin) * (primary / 255.0)
            radiance[invalid] = np.nan

            tb_primary = self._radiance_to_tb(radiance, self.constants["k1"], self.constants["k2"])
            tb_secondary = None

        # Final dtype & shape consistency
        return (
            tb_primary.astype(np.float32),
            tb_secondary.astype(np.float32) if tb_secondary is not None else None,
        )

    @staticmethod
    def _radiance_to_tb(
        radiance: NDArray[np.float64],
        k1: float,
        k2: float,
    ) -> NDArray[np.float32]:
        """Convert spectral radiance to brightness temperature using Planck's law."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            tb = k2 / np.log(k1 / radiance + 1.0)
        tb[~np.isfinite(tb)] = np.nan
        return tb.astype(np.float32)