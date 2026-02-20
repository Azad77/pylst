from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from pylst.exceptions import MissingRequiredArgumentError, assert_required_keywords_provided
from pylst.utils import fractional_vegetation_cover


class SplitWindowParentLST:
    """
    Base class for split-window Land Surface Temperature (LST) algorithms.

    All subclasses implement the _compute_lst method.
    Common post-processing (masking, clipping) is handled here.
    """

    # Realistic LST bounds (Kelvin) — can be overridden in subclasses
    MIN_LST = 200.0          # ≈ -73 °C (polar/extreme cold)
    # For the split-window family we use a somewhat lower upper bound
    # than mono-window. Historically the original implementation defined
    # `max_earth_temp = 273.15 + 56.7` so we match that here.
    MAX_LST = 273.15 + 56.7  # ~56.7 °C (very hot surfaces)

    @property
    def max_earth_temp(self) -> float:
        """Legacy compatibility property used in tests and older code.

        Returns the upper temperature bound used when clipping results.
        """
        return self.MAX_LST

    def __call__(
        self,
        brightness_temperature_10: NDArray[np.floating],
        brightness_temperature_11: NDArray[np.floating],
        mask: Optional[NDArray[np.bool_]] = None,
        **kwargs,
    ) -> NDArray[np.float32]:
        """
        Compute LST using the specific split-window algorithm.

        Args:
            brightness_temperature_10: BT image from Landsat Band 10 (Kelvin)
            brightness_temperature_11: BT image from Landsat Band 11 (Kelvin)
            mask: Optional boolean mask (True = invalid → set LST to NaN)
            **kwargs: Algorithm-specific parameters (e.g. emissivity, NDVI)

        Returns:
            LST array in Kelvin (float32)
        """
        # Basic shape validation
        if brightness_temperature_10.shape != brightness_temperature_11.shape:
            raise ValueError(
                "brightness_temperature_10 and _11 must have the same shape"
            )

        bt10 = brightness_temperature_10.astype(np.float64, copy=False)
        bt11 = brightness_temperature_11.astype(np.float64, copy=False)

        lst = self._compute_lst(bt10=bt10, bt11=bt11, mask=mask, **kwargs)

        # Apply mask if provided
        if mask is not None:
            if mask.shape != lst.shape:
                raise ValueError("mask shape must match BT arrays")
            lst[mask] = np.nan

        # Clip to physically realistic range
        invalid = (lst < self.MIN_LST) | (lst > self.MAX_LST)
        if np.any(invalid):
            warnings.warn(
                f"{np.sum(invalid)} pixels had unrealistic LST values → set to NaN",
                UserWarning,
                stacklevel=2,
            )
            lst[invalid] = np.nan

        return lst.astype(np.float32, copy=False)

    def _compute_lst(
        self,
        bt10: NDArray[np.float64],
        bt11: NDArray[np.float64],
        mask: Optional[NDArray[np.bool_]],
        **kwargs,
    ) -> NDArray[np.float64]:
        """Abstract method – implement in subclasses."""
        raise NotImplementedError("Must be implemented by subclass")


class SplitWindowJiminezMunozLST(SplitWindowParentLST):
    """
    Jiménez-Muñoz & Sobrino (2008) split-window algorithm variant.

    Reference:
    Jiménez-Muñoz, J. C., & Sobrino, J. A. (2008).
    Split-window coefficients for land surface temperature retrieval
    from low-resolution thermal infrared sensors. IEEE Geoscience and Remote Sensing Letters.
    """

    cwv = 0.013  # column water vapor content (default assumption)

    def _compute_lst(
        self,
        bt10: NDArray[np.float64],
        bt11: NDArray[np.float64],
        mask: Optional[NDArray[np.bool_]],
        emissivity_10: NDArray[np.floating],
        emissivity_11: NDArray[np.floating],
    ) -> NDArray[np.float64]:
        required = ["emissivity_10", "emissivity_11"]
        assert_required_keywords_provided(required, emissivity_10=emissivity_10, emissivity_11=emissivity_11)

        mean_e = (emissivity_10 + emissivity_11) / 2
        diff_e = emissivity_10 - emissivity_11
        diff_tb = bt10 - bt11

        lst = (
            bt10
            + 1.387 * diff_tb
            + 0.183 * (diff_tb ** 2)
            - 0.268
            + (54.3 - 2.238 * self.cwv) * (1 - mean_e)
            + (-129.2 + 16.4 * self.cwv) * diff_e
        )

        return lst


class SplitWindowKerrLST(SplitWindowParentLST):
    """
    Kerr et al. (2004) split-window algorithm (NDVI-based).

    Reference:
    Kerr, Y., et al. (2004). Land surface temperature retrieval techniques and applications:
    case of the AVHRR. In Thermal Remote Sensing in Land Surface Processing.
    """

    def _compute_lst(
        self,
        bt10: NDArray[np.float64],
        bt11: NDArray[np.float64],
        mask: Optional[NDArray[np.bool_]],
        ndvi: NDArray[np.floating],
    ) -> NDArray[np.float64]:
        required = ["ndvi"]
        assert_required_keywords_provided(required, ndvi=ndvi)

        pv = fractional_vegetation_cover(ndvi)

        lst = (
            bt10 * (0.5 * pv + 3.1)
            + bt11 * (-0.5 * pv - 2.1)
            - (5.5 * pv + 3.1)
        )

        return lst


class SplitWindowMcMillinLST(SplitWindowParentLST):
    """
    McMillin (1975) split-window algorithm (simple linear form).

    Reference:
    McMillin, L. M. (1975). Estimation of sea surface temperatures from two
    infrared window measurements with different absorption.
    Journal of Geophysical Research, 80(36), 5113–5117.
    """

    def _compute_lst(
        self,
        bt10: NDArray[np.float64],
        bt11: NDArray[np.float64],
        mask: Optional[NDArray[np.bool_]],
    ) -> NDArray[np.float64]:
        lst = 1.035 * bt10 + 3.046 * (bt10 - bt11) - 10.93
        return lst


class SplitWindowPriceLST(SplitWindowParentLST):
    """
    Price (1984) split-window algorithm.

    Reference:
    Price, J. C. (1984). Land surface temperature measurements from the split window
    channels of the NOAA advanced very high-resolution radiometer.
    Journal of Geophysical Research, 89(D5), 7231–7237.
    """

    def _compute_lst(
        self,
        bt10: NDArray[np.float64],
        bt11: NDArray[np.float64],
        mask: Optional[NDArray[np.bool_]],
        emissivity_10: NDArray[np.floating],
        emissivity_11: NDArray[np.floating],
    ) -> NDArray[np.float64]:
        required = ["emissivity_10", "emissivity_11"]
        assert_required_keywords_provided(required, emissivity_10=emissivity_10, emissivity_11=emissivity_11)

        lst = (
            (bt10 + 3.33 * (bt10 - bt11)) * ((5.5 - emissivity_10) / 4.5)
            + 0.75 * bt11 * (emissivity_10 - emissivity_11)
        )

        return lst


class SplitWindowSobrino1993LST(SplitWindowParentLST):
    """
    Sobrino et al. (1993) split-window algorithm.

    Reference:
    Sobrino, J. A., Caselles, V., & Coll, C. (1993).
    Theoretical split window algorithms for determining the actual surface temperature.
    Il Nuovo Cimento C, 16(2), 219–236.
    """

    def _compute_lst(
        self,
        bt10: NDArray[np.float64],
        bt11: NDArray[np.float64],
        mask: Optional[NDArray[np.bool_]],
        emissivity_10: NDArray[np.floating],
        emissivity_11: NDArray[np.floating],
    ) -> NDArray[np.float64]:
        required = ["emissivity_10", "emissivity_11"]
        assert_required_keywords_provided(required, emissivity_10=emissivity_10, emissivity_11=emissivity_11)

        diff_tb = bt10 - bt11
        diff_e = emissivity_10 - emissivity_11

        lst = (
            bt10
            + 1.06 * diff_tb
            + 0.46 * (diff_tb ** 2)
            + 53 * (1 - emissivity_10)
            - 53 * diff_e
        )

        return lst