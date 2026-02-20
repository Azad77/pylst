#!/usr/bin/env python
"""Quick test to verify pylst package imports"""

try:
    from pylst.temperature import lst_runner
    from pylst.emissivity import emissivity_runner
    from pylst.normalization import nrs
    import numpy as np
    
    print("✓ All imports successful!")
    print("\n" + "="*60)
    print("ERBIL CITY LST ANALYSIS - Quick Test")
    print("="*60)
    
    # Create minimal test data
    bt10 = np.ones((10, 10), dtype=np.float32) * 300
    bt11 = np.ones((10, 10), dtype=np.float32) * 298
    ndvi = np.full((10, 10), 0.5, dtype=np.float32)
    emm10 = np.full((10, 10), 0.96, dtype=np.float32)
    emm11 = np.full((10, 10), 0.95, dtype=np.float32)
    
    # Test Kerr algorithm
    print("\nTesting Kerr algorithm...")
    lst_kerr = lst_runner.run(method="kerr", brightness_temperature_10=bt10, 
                              brightness_temperature_11=bt11, ndvi=ndvi)
    print(f"✓ Kerr LST mean: {np.nanmean(lst_kerr):.1f} K ({np.nanmean(lst_kerr)-273.15:.1f}°C)")
    
    # Test Sobrino algorithm
    print("\nTesting Sobrino-1993 algorithm...")
    lst_sobrino = lst_runner.run(method="sobrino-1993", brightness_temperature_10=bt10,
                                 brightness_temperature_11=bt11, emissivity_10=emm10,
                                 emissivity_11=emm11)
    print(f"✓ Sobrino LST mean: {np.nanmean(lst_sobrino):.1f} K ({np.nanmean(lst_sobrino)-273.15:.1f}°C)")
    
    # Test McMillin algorithm
    print("\nTesting McMillin algorithm...")
    lst_mcmillin = lst_runner.run(method="mcmillin", brightness_temperature_10=bt10,
                                  brightness_temperature_11=bt11)
    print(f"✓ McMillin LST mean: {np.nanmean(lst_mcmillin):.1f} K ({np.nanmean(lst_mcmillin)-273.15:.1f}°C)")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nPackage is ready. Run full tutorial with:")
    print("  python d:\\pylst0.0.3\\tutorial\\erbil_lst_analysis.py")
    
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
