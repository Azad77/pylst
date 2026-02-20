from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from pylst.exceptions import MissingRequiredArgumentError, assert_required_keywords_provided


class MonoWindowLST:
    """
    Mono-window algorithm for Land Surface Temperature (LST) retrieval from a single TIR band.

    This implementation follows the practical method described in:

    Avdan, U., & Jovanovska, G. (2016).
    "Algorithm for automated mapping of land surface temperature using LANDSAT 8 satellite data."
    Journal of Sensors, 2016, 1–8. https://doi.org/10.1155/2016/1480307

    Core equation:

        LST = BT / (1 + (λ × BT / ρ) × ln(ε))

    Where:
        BT   = brightness temperature (K)
        λ    = central/effective wavelength (~10.895 μm for Landsat 8 Band 10)
        ρ    = h × c / k ≈ 14388 μm·K
        ε    = land surface emissivity (0–1)

    Notes:
        - This simplified form is widely used for Landsat 8 Band 10.
        - It assumes moderate atmospheric conditions (no explicit τ or T_a correction).
        - LST is typically higher than BT when ε < 1 (which is physically expected).
    """

    # Physical / realistic bounds for LST (Kelvin)
    MIN_EARTH_TEMP: float = 200.0                # ~ -73°C
    MAX_EARTH_TEMP: float = 273.15 + 70.0        # 343.15 K (~70°C)

    def __init__(
        self,
        wavelength: float = 10.895,              # μm – Landsat 8 Band 10 effective wavelength
        rho: float = 14388.0,                    # μm·K (h c / k)
        max_lst: Optional[float] = None,
    ):
        """
        Args:
            wavelength: Central/effective wavelength of the thermal band (μm)
            rho: Precomputed constant ρ = h c / k (μm·K)
            max_lst: Optional custom maximum realistic LST value (K)
        """
        self.wavelength = wavelength
        self.rho = rho
        self.max_lst = max_lst or self.MAX_EARTH_TEMP

    def compute(
        self,
        *,
        brightness_temperature_10: NDArray[np.floating],
        emissivity_10: NDArray[np.floating],
        mask: Optional[NDArray[np.bool_]] = None,
        **kwargs,
    ) -> NDArray[np.float32]:
        """
        Compute Land Surface Temperature using the mono-window algorithm.
        This is the main public method expected by unit tests.

        Args:
            brightness_temperature_10: Brightness temperature image – Band 10 (Kelvin)
            emissivity_10: Land surface emissivity image (0–1)
            mask: Optional boolean mask where True = **valid** pixel (keep value),
                  False = invalid/masked → set to NaN

        Returns:
            LST image in Kelvin (float32)
        """
        return self(
            brightness_temperature_10=brightness_temperature_10,
            emissivity_10=emissivity_10,
            mask=mask,
            **kwargs
        )

    def __call__(
        self,
        *,
        brightness_temperature_10: NDArray[np.floating],
        emissivity_10: NDArray[np.floating],
        mask: Optional[NDArray[np.bool_]] = None,
        **kwargs,
    ) -> NDArray[np.float32]:
        """
        Callable interface – same behavior as .compute().
        Useful when treating the instance as a function.
        """
        required = {"brightness_temperature_10", "emissivity_10"}
        # ensure the values passed as explicit parameters are included in the
        # validation step; compute() forwards them as positional/keyword
        # parameters so they won't appear in **kwargs otherwise.
        kwargs = {**kwargs, "brightness_temperature_10": brightness_temperature_10, "emissivity_10": emissivity_10}
        assert_required_keywords_provided(required, **kwargs)

        bt = brightness_temperature_10.astype(np.float64, copy=False)
        eps = emissivity_10.astype(np.float64, copy=False)

        if bt.shape != eps.shape:
            raise ValueError(
                f"Shape mismatch: brightness_temperature_10 {bt.shape} ≠ emissivity_10 {eps.shape}"
            )

        # Clamp emissivity to physically valid range
        if np.any(eps < 0) or np.any(eps > 1):
            warnings.warn(
                "Emissivity values outside [0, 1] detected – clamping to valid range",
                UserWarning,
                stacklevel=2,
            )
            eps = np.clip(eps, 0.0, 1.0)

        # Prevent log(0) or very small values causing extreme correction / overflow
        eps_safe = np.clip(eps, 1e-4, 1.0)   # slightly more conservative than 0.001

        # Core mono-window equation (Avdan 2016 style – simplified form)
        correction = (self.wavelength * bt / self.rho) * np.log(eps_safe)
        lst = bt / (1.0 + correction)

        # Apply optional mask: True = keep value, False = NaN
        if mask is not None:
            if mask.shape != lst.shape:
                raise ValueError("mask shape must match input arrays")
            lst = np.where(mask, lst, np.nan)

        # Clip to physically realistic range → set outliers to NaN
        invalid = (lst < self.MIN_EARTH_TEMP) | (lst > self.max_lst)
        if np.any(invalid):
            warnings.warn(
                f"{np.sum(invalid)} pixels had unrealistic LST values → set to NaN",
                UserWarning,
                stacklevel=2,
            )
            lst[invalid] = np.nan

        return lst.astype(np.float32, copy=False)


# Default instance using Avdan (2016) / Landsat 8 Band 10 defaults
mono_window_lst = MonoWindowLST(
    wavelength=10.895,
    rho=14388.0,
)