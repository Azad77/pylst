# pylst/algorithms/lst_registry.py   ← recommended new name/location
"""
Registry and dispatcher for Land Surface Temperature (LST) retrieval algorithms
from Landsat TIRS data (Landsat 8/9).

Supports:
- Single-channel / Mono-window algorithms (use one TIR band)
- Split-window algorithms (use both TIR bands 10 & 11)

All methods typically require:
- Brightness temperature(s)
- Land surface emissivity (from pylst.emissivity)
- Atmospheric parameters (water vapor, transmittance, etc.)

Usage (recommended):
    from pylst import lst_runner

    lst = lst_runner.run(
        method="sobrino-1993",
        bt10=bt10_array,
        bt11=bt11_array,
        emissivity_10=emm10,
        emissivity_11=emm11,
        # other kwargs specific to the algorithm
    )
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type

import numpy as np

from .algorithms.mono_window import MonoWindowLST
from .algorithms.split_window import (
    SplitWindowJiminezMunozLST,
    SplitWindowKerrLST,
    SplitWindowMcMillinLST,
    SplitWindowPriceLST,
    SplitWindowSobrino1993LST,
)



class LSTRunner:
    """
    Dispatcher for different LST retrieval algorithms.

    Provides a unified .run() interface regardless of algorithm type.
    """

    def __init__(
        self,
        algorithms: Dict[str, Type],
        default_method: Optional[str] = "sobrino-1993",  # most common & accurate SW
    ):
        self.algorithms = algorithms.copy()
        self.default_method = default_method

    def run(
        self,
        method: Optional[str] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """
        Compute LST using the selected (or default) algorithm.

        Parameters
        ----------
        method : str, optional
            Algorithm name (e.g. "sobrino-1993", "jiminez-munoz", "mono-window").
            If None → uses default.
        **kwargs
            Algorithm-specific arguments:
            - Single-channel: brightness_temp, emissivity, ...
            - Split-window: bt10, bt11, emissivity_10, emissivity_11, water_vapor, ...

        Returns
        -------
        ndarray
            Land surface temperature array (Kelvin)

        Raises
        ------
        ValueError
            Unknown method or missing required arguments
        TypeError
            Algorithm instantiation/call failed
        """
        selected = method or self.default_method

        if selected is None:
            raise ValueError(
                "No method provided and no default set.\n"
                f"Available: {', '.join(sorted(self.algorithms))}"
            )

        if selected not in self.algorithms:
            raise ValueError(
                f"Unknown LST method '{selected}'.\n"
                f"Available methods: {', '.join(sorted(self.algorithms))}"
            )

        AlgoClass = self.algorithms[selected]
        algo_instance = AlgoClass()

        # Ensure 'method' is not passed to the algorithm since it's only for
        # selecting which algorithm to use, not for configuring it.
        algo_kwargs = {k: v for k, v in kwargs.items() if k != "method"}

        try:
            return algo_instance(**algo_kwargs)
        except TypeError as exc:
            raise TypeError(
                f"Failed calling '{selected}' — check required arguments.\n"
                f"Original error: {exc}"
            ) from exc

    def available_methods(self) -> list[str]:
        """Sorted list of all registered LST algorithm names."""
        return sorted(self.algorithms.keys())

    def __repr__(self) -> str:
        methods = ", ".join(f"'{m}'" for m in self.available_methods())
        default = f" (default: '{self.default_method}')" if self.default_method else ""
        return f"LSTRunner[{methods}]{default}"


# Pre-configured public runner instance (preferred way to use)
lst_runner = LSTRunner(
    algorithms={
        "mono-window": MonoWindowLST,
        # Split-window methods (most recommended for Landsat 8/9 TIRS)
        "jiminez-munoz": SplitWindowJiminezMunozLST,
        "kerr": SplitWindowKerrLST,
        "mcmillin": SplitWindowMcMillinLST,
        "price": SplitWindowPriceLST,
        "sobrino-1993": SplitWindowSobrino1993LST,
    },
    default_method="sobrino-1993",  # Widely validated, good balance of accuracy/simplicity
)