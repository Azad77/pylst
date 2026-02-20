# basic_lst_workflow.py
"""Basic LST processing workflow using pylst

This script demonstrates a minimal in‑memory example of converting
synthetic Landsat thermal band DN values to brightness temperature,
estimated emissivity, and finally land surface temperature using the
mono-window algorithm.  Users can adapt the code to their own data
arrays or files.

Requirements:
    pip install pylst numpy

Run in a notebook by copying the cells below.
"""

import numpy as np
from pylst.temperature import BrightnessTemperatureLandsat, MonoWindowLST
from pylst.emissivity import emissivity_runner

# --- synthetic data (5x5) --------------------------------------------------
# pretend these are digital numbers from a Landsat 8/9 scene
band10_dn = np.full((5, 5), 1500, dtype=np.float32)
ndvi = np.random.uniform(-0.1, 0.8, size=(5, 5)).astype(np.float32)
mask = ndvi < 0  # some invalid pixels

# --- brightness temperature ------------------------------------------------
bt_calc = BrightnessTemperatureLandsat(sensor="landsat8")
bt10, _ = bt_calc(band10_dn, nodata_mask=mask)

# --- emissivity estimate --------------------------------------------------
# use the Gopinadh algorithm via the emissivity runner
emm10, emm11 = emissivity_runner.run(method="gopinadh", ndvi=ndvi)

# --- monocwindow LST -------------------------------------------------------
mono = MonoWindowLST()          # defaults to Landsat 8/9 wavelength
lst = mono.compute(
    brightness_temperature_10=bt10,
    emissivity_10=emm10,
    mask=mask,
)

print("brightness temperature shape", bt10.shape)
print("LST sample", lst[0, :3])

# optionally plot if you have matplotlib
try:
    import matplotlib.pyplot as plt
    plt.imshow(lst, cmap="inferno")
    plt.colorbar(label="Kelvin")
    plt.title("Mono-window LST example")
    plt.show()
except ImportError:
    pass
