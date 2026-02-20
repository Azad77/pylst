"""
Quick verification script to confirm pylst is properly installed.
Run this after reinstalling: python verify_install.py
"""

import numpy as np
from pylst.temperature import lst_runner

print("=" * 60)
print("PYLST INSTALLATION VERIFICATION")
print("=" * 60)

# Create synthetic test data
bt10 = np.random.uniform(290, 310, size=(5, 5)).astype(np.float32)
bt11 = bt10 - np.random.uniform(0, 2, size=bt10.shape).astype(np.float32)
emm10 = np.full(bt10.shape, 0.96, dtype=np.float32)
emm11 = np.full(bt10.shape, 0.95, dtype=np.float32)
ndvi_arr = np.random.uniform(0.1, 0.8, size=bt10.shape).astype(np.float32)

# Test each algorithm
algorithms_to_test = [
    {
        "name": "kerr",
        "method": "kerr",
        "kwargs": {
            "brightness_temperature_10": bt10,
            "brightness_temperature_11": bt11,
            "ndvi": ndvi_arr,
        }
    },
    {
        "name": "sobrino-1993",
        "method": "sobrino-1993",
        "kwargs": {
            "brightness_temperature_10": bt10,
            "brightness_temperature_11": bt11,
            "emissivity_10": emm10,
            "emissivity_11": emm11,
        }
    },
    {
        "name": "mcmillin",
        "method": "mcmillin",
        "kwargs": {
            "brightness_temperature_10": bt10,
            "brightness_temperature_11": bt11,
        }
    },
]

all_passed = True

for test in algorithms_to_test:
    try:
        result = lst_runner.run(method=test["method"], **test["kwargs"])
        mean_lst = np.nanmean(result)
        print(f"✓ {test['name']:20} PASSED (mean LST: {mean_lst:.1f} K)")
    except Exception as e:
        print(f"✗ {test['name']:20} FAILED: {type(e).__name__}: {e}")
        all_passed = False

print("=" * 60)
if all_passed:
    print("✓ ALL TESTS PASSED - Package is correctly installed!")
else:
    print("✗ SOME TESTS FAILED - There may be an import issue")
    print("\nTroubleshooting steps:")
    print("1. Make sure you completed the reinstall commands")
    print("2. Restart your Python/Jupyter kernel")
    print("3. Make sure build/ directory was deleted")
print("=" * 60)
