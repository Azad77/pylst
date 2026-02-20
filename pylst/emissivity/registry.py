# pylst/emissivity/registry.py
"""
Registry of available land surface emissivity (LSE) estimation methods
for pylst.emissivity.

This file defines the mapping from method names (strings) to concrete
algorithm classes. It also provides a pre-configured runner instance.

Usage examples:
    from pylst.emissivity import emissivity_runner

    # Default method
    emm_10, emm_11 = emissivity_runner.run(ndvi=ndvi_array)

    # Explicit method
    emm_10, emm_11 = emissivity_runner.run("ndvi_threshold", ndvi=ndvi_array)

    # See all options
    print(emissivity_runner.available_methods())
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .algorithms import (
    ComputeMonoWindowEmissivity,
    ComputeEmissivityNBEM,
    ComputeEmissivityGopinadh,
    ComputeNDVIThresholdEmissivity,   # ← your new common method
)


class EmissivityRunner:
    """
    Simple dispatcher for emissivity estimation methods.

    Forwards calls to the selected algorithm class.
    """

    def __init__(
        self,
        methods: Dict[str, type],
        default_method: Optional[str] = "ndvi_threshold",
    ):
        self.methods = methods.copy()
        self.default_method = default_method

    def run(
        self,
        method: Optional[str] = None,
        /,
        **kwargs: Any,
    ) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Compute emissivity using the selected (or default) method.

        Parameters
        ----------
        method : str, optional
            One of: {list(self.methods.keys())}
        **kwargs
            Passed to the algorithm (ndvi is required, red_band optional, etc.)

        Returns
        -------
        tuple (emm_10, emm_11)
            Emissivity for Landsat TIRS band 10 and 11 (second may be None)
        """
        selected = method or self.default_method

        if selected is None:
            raise ValueError(
                f"No method specified and no default is set.\n"
                f"Available methods: {', '.join(sorted(self.methods))}"
            )

        if selected not in self.methods:
            raise ValueError(
                f"Unknown emissivity method '{selected}'.\n"
                f"Available: {', '.join(sorted(self.methods))}"
            )

        AlgorithmClass = self.methods[selected]
        algorithm = AlgorithmClass()
        return algorithm(**kwargs)

    def available_methods(self) -> list[str]:
        """List all registered method names."""
        return sorted(self.methods.keys())

    def __repr__(self) -> str:
        methods = ", ".join(f"'{m}'" for m in self.available_methods())
        default = f" (default: '{self.default_method}')" if self.default_method else ""
        return f"EmissivityRunner[{methods}]{default}"


# ─── Public instance ─────────────────────────────────────────────────────
emissivity_runner = EmissivityRunner(
    methods={
        "avdan": ComputeMonoWindowEmissivity,           # Avdan & Jovanovska 2016
        "xiaolei": ComputeEmissivityNBEM,               # Yu et al. 2014 (NBEM)
        "gopinadh": ComputeEmissivityGopinadh,          # Rongali et al. 2018
        "ndvi_threshold": ComputeNDVIThresholdEmissivity,  # Sobrino-style (most common)
    },
    default_method="ndvi_threshold",   # ← changed to most standard method
)