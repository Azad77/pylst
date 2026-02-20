# using_lst_runner.py
"""Example showing the high-level lst_runner API and split-window algorithms.

This script is intended as a quick-start for users who just want to pass
arrays to the common runner interface instead of instantiating algorithm
classes directly.  It also demonstrates switching sensors and normalizing
results.

Dependencies:
    pip install pylst numpy
    (optional: install geopandas/rasterstats for spatial_analysis examples)
"""

import numpy as np
from pylst.temperature import lst_runner
from pylst.normalization import nrs

# synthetic Landsat 8/9 brightness temperatures
bt10 = np.random.uniform(290, 310, size=(5, 5)).astype(np.float32)
bt11 = bt10 - np.random.uniform(0, 2, size=bt10.shape).astype(np.float32)
emm10 = np.full(bt10.shape, 0.96, dtype=np.float32)
emm11 = np.full(bt10.shape, 0.95, dtype=np.float32)
ndvi_arr = np.random.uniform(0.1, 0.8, size=bt10.shape).astype(np.float32)

# Example 1: Kerr algorithm (NDVI-based)
print("=== Kerr Algorithm (NDVI-based) ===")
lst_kerr = lst_runner.run(
    method="kerr",
    brightness_temperature_10=bt10,
    brightness_temperature_11=bt11,
    ndvi=ndvi_arr,  # Kerr requires NDVI
)
print("  LST mean:", np.nanmean(lst_kerr))

# Example 2: Sobrino-1993 algorithm (emissivity-based, default)
print("\n=== Sobrino-1993 Algorithm (emissivity-based) ===")
lst_sobrino = lst_runner.run(
    method="sobrino-1993",
    brightness_temperature_10=bt10,
    brightness_temperature_11=bt11,
    emissivity_10=emm10,  # Sobrino requires emissivity
    emissivity_11=emm11,
)
print("  LST mean:", np.nanmean(lst_sobrino))

# Example 3: McMillin algorithm (simple, no extra inputs needed)
print("\n=== McMillin Algorithm (simplest) ===")
lst_mcmillin = lst_runner.run(
    method="mcmillin",
    brightness_temperature_10=bt10,
    brightness_temperature_11=bt11,
)
print("  LST mean:", np.nanmean(lst_mcmillin))

# Normalize the Sobrino result for multi-temporal comparison
lst_norm = nrs(lst_sobrino)
print("\n=== Normalization Example ===")
print("  Original mean:", np.nanmean(lst_sobrino))
print("  Normalized mean:", np.nanmean(lst_norm))

# Display quick stats
print("\n=== Summary Stats ===")
for name, arr in [("kerr", lst_kerr), ("sobrino", lst_sobrino), ("mcmillin", lst_mcmillin)]:
    print(f"  {name:12} min={np.nanmin(arr):6.1f}, max={np.nanmax(arr):6.1f}, mean={np.nanmean(arr):6.1f}")

# Show available methods
print("\n=== Available Methods ===")
print("  Available:", lst_runner.available_methods())
print("  Default:", lst_runner.default_method)

