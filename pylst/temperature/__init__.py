# pylst/temperature/__init__.py
from __future__ import annotations

# Core LST & Brightness Temperature
from .brightness_temperature import BrightnessTemperatureCalculator

# If you want, alias for Landsat usage (instead of a separate class)
BrightnessTemperatureLandsat = BrightnessTemperatureCalculator

# LST runner / registry
from .lst_registry import lst_runner, LSTRunner

# Algorithms
from .algorithms.mono_window import MonoWindowLST
from .algorithms.split_window import (
    SplitWindowSobrino1993LST,
    SplitWindowJiminezMunozLST,
    SplitWindowKerrLST,
    SplitWindowMcMillinLST,
    SplitWindowPriceLST,
)

# Default algorithms dictionary
default_algorithms = {
    "single_window": MonoWindowLST,
    "split_window": {
        "sobrino-1993": SplitWindowSobrino1993LST,
        "jiminez-munoz": SplitWindowJiminezMunozLST,
        "kerr": SplitWindowKerrLST,
        "mcmillin": SplitWindowMcMillinLST,
        "price": SplitWindowPriceLST,
    },
}

__all__ = [
    "BrightnessTemperatureCalculator",
    "BrightnessTemperatureLandsat",
    "lst_runner",
    "LSTRunner",
    "MonoWindowLST",
    "SplitWindowSobrino1993LST",
    "SplitWindowJiminezMunozLST",
    "SplitWindowKerrLST",
    "SplitWindowMcMillinLST",
    "SplitWindowPriceLST",
    "default_algorithms",
]
