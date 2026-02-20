"""
Land Surface Temperature Analysis for Erbil City, Iraq using Landsat 9

This tutorial demonstrates:
1. Creating synthetic Landsat 9 TIRS data for Erbil region
2. Computing brightness temperature from raw thermal data
3. Estimating land surface emissivity using NDVI
4. Calculating LST using multiple algorithms (Kerr, Sobrino, McMillin)
5. Normalizing results for temporal comparison
6. Analyzing urban heat island effect

Real-world usage would require either:
- Google Earth Engine credentials (for automated download)
- Pre-downloaded Landsat 9 GeoTIFF files from USGS Earth Explorer

Location: Erbil City, Iraq
Coordinates: 36.1912° N, 44.0055° E
Landsat 9 TIRS bands:
  - Band 10: ~10.9 μm (Long-wave infrared, used for LST)
  - Band 11: ~12.0 μm (Long-wave infrared, used for LST)

Dependencies:
    pip install pylst numpy
    (optional: matplotlib for visualization, rasterio for reading GeoTIFF files)
"""

import numpy as np
from datetime import datetime

# Import pylst components
from pylst.temperature import BrightnessTemperatureCalculator, lst_runner
from pylst.emissivity import emissivity_runner
from pylst.normalization import nrs

# ============================================================================
# STEP 1: Setup Erbil Region Parameters
# ============================================================================

print("=" * 70)
print("LAND SURFACE TEMPERATURE ANALYSIS FOR ERBIL CITY, IRAQ")
print("=" * 70)

# Erbil City metadata
erbil_lat = 36.1912
erbil_lon = 44.0055
analysis_date = "2024-06-15"  # Summer day (realistic for heat analysis)
sensor = "landsat9"

print(f"\nLocation: Erbil City, Iraq")
print(f"Coordinates: {erbil_lat}°N, {erbil_lon}°E")
print(f"Analysis Date: {analysis_date}")
print(f"Sensor: Landsat 9 TIRS")

# ============================================================================
# STEP 2: Create Synthetic Landsat 9 TIRS Data
# ============================================================================
# In practice, you would read real GeoTIFF files from USGS
# For this tutorial, we simulate realistic thermal data for an urban area

print("\n" + "=" * 70)
print("STEP 1: SIMULATING LANDSAT 9 TIRS DATA")
print("=" * 70)

# Create a 100x100 pixel grid representing a ~30km x 30km area
# (Landsat has 30m resolution)
grid_size = 100
pixel_resolution = 30  # meters
area_size_km = (grid_size * pixel_resolution) / 1000

print(f"Grid size: {grid_size} x {grid_size} pixels")
print(f"Pixel resolution: {pixel_resolution}m")
print(f"Total area: ~{area_size_km}km x {area_size_km}km")

# Simulate thermal radiance for Band 10 (10.9 μm)
# Typical brightness temperatures for Erbil in summer: 300-315 K
# Core urban areas can reach 320+ K, vegetation ~290 K
np.random.seed(42)  # For reproducibility

# Create spatial variation: hot urban core, cooler edges
x = np.linspace(-1, 1, grid_size)
y = np.linspace(-1, 1, grid_size)
xx, yy = np.meshgrid(x, y)
distance_from_center = np.sqrt(xx**2 + yy**2)

# Base temperature gradient
base_bt10 = 305 - 10 * distance_from_center  # 295-315 K range
# Add noise for realism
noise = np.random.normal(0, 1.5, (grid_size, grid_size))
bt10_raw = base_bt10 + noise

# Band 11 is typically 1-3 K cooler than Band 10
bt11_raw = bt10_raw - np.random.uniform(1, 3, (grid_size, grid_size))

# Add vegetation/water features (cooler areas)
vegetation_mask = distance_from_center > 0.6
bt10_raw[vegetation_mask] -= 8  # Cooler vegetation
bt11_raw[vegetation_mask] -= 8

# Convert to float32 (standard for Landsat processing)
bt10 = bt10_raw.astype(np.float32)
bt11 = bt11_raw.astype(np.float32)

print(f"\nBand 10 (10.9 μm) Temperature Range: {np.min(bt10):.1f} - {np.max(bt10):.1f} K")
print(f"Band 11 (12.0 μm) Temperature Range: {np.min(bt11):.1f} - {np.max(bt11):.1f} K")
print(f"Band 10 Mean: {np.mean(bt10):.1f} K")

# ============================================================================
# STEP 3: Create NDVI Map (from NIR and Red bands)
# ============================================================================
# NDVI = (NIR - RED) / (NIR + RED), typically ranges from -1 to 1
# Urban areas: -0.1 to 0.2
# Vegetation: 0.3 to 0.8
# Water: < 0 (negative)

print("\n" + "=" * 70)
print("STEP 2: SIMULATING NDVI MAP")
print("=" * 70)

# Create NDVI with spatial variation
ndvi_urban = np.random.uniform(-0.1, 0.1, (grid_size, grid_size)).astype(np.float32)
ndvi_vegetation = np.random.uniform(0.4, 0.7, (grid_size, grid_size)).astype(np.float32)
ndvi = np.where(vegetation_mask, ndvi_vegetation, ndvi_urban)

print(f"NDVI Range: {np.min(ndvi):.2f} - {np.max(ndvi):.2f}")
print(f"Urban NDVI (core): -0.1 to +0.1")
print(f"Vegetation NDVI (edges): +0.4 to +0.7")

# ============================================================================
# STEP 4: Estimate Land Surface Emissivity
# ============================================================================

print("\n" + "=" * 70)
print("STEP 3: ESTIMATING LAND SURFACE EMISSIVITY")
print("=" * 70)

# Use Gopinadh formula: emissivity = 0.004 * Pv + 0.986
# where Pv is fractional vegetation cover
# Note: emissivity_runner.run() returns a tuple (emm10, emm11)
emm10, emm11 = emissivity_runner.run(method="gopinadh", ndvi=ndvi)

print(f"Emissivity Band 10 Range: {np.min(emm10):.3f} - {np.max(emm10):.3f}")
print(f"Emissivity Band 11 Range: {np.min(emm11):.3f} - {np.max(emm11):.3f}")

# ============================================================================
# STEP 5: Calculate LST using Multiple Algorithms
# ============================================================================

print("\n" + "=" * 70)print(f"  Minimum:  {np.nanmin(lst_sobrino):.1f} K "
      f"({np.nanmin(lst_sobrino)-273.15:.1f}°C)")
print(f"  Maximum:  {np.nanmax(lst_sobrino):.1f} K "
      f"({np.nanmax(lst_sobrino)-273.15:.1f}°C)")
print(f"  Mean:     {np.nanmean(lst_sobrino):.1f} K "
      f"({np.nanmean(lst_sobrino)-273.15:.1f}°C)")
print(f"  Std Dev:  {np.nanstd(lst_sobrino):.1f} K")
print(f"  Median:   {np.nanmedian(lst_sobrino):.1f} K "
      f"({np.nanmedian(lst_sobrino)-273.15:.1f}°C)")
print("STEP 4: CALCULATING LAND SURFACE TEMPERATURE")
print("=" * 70)

# Algorithm 1: Kerr et al. (NDVI-based)
print("\n1. Kerr Algorithm (NDVI-based)...")
lst_kerr = lst_runner.run(
    method="kerr",
    brightness_temperature_10=bt10,
    brightness_temperature_11=bt11,
    ndvi=ndvi,
)
print(f"   Range: {np.nanmin(lst_kerr):.1f} - {np.nanmax(lst_kerr):.1f} K")
print(f"   Mean:  {np.nanmean(lst_kerr):.1f} K (~{np.nanmean(lst_kerr)-273.15:.1f}°C)")

# Algorithm 2: Sobrino 1993 (emissivity-based, most accurate)
print("\n2. Sobrino 1993 Algorithm (emissivity-based, recommended)...")
lst_sobrino = lst_runner.run(
    method="sobrino-1993",
    brightness_temperature_10=bt10,
    brightness_temperature_11=bt11,
    emissivity_10=emm10,
    emissivity_11=emm11,
)
print(f"   Range: {np.nanmin(lst_sobrino):.1f} - {np.nanmax(lst_sobrino):.1f} K")
print(f"   Mean:  {np.nanmean(lst_sobrino):.1f} K (~{np.nanmean(lst_sobrino)-273.15:.1f}°C)")

# Algorithm 3: McMillin (simplest, fastest)
print("\n3. McMillin Algorithm (simple linear form)...")
lst_mcmillin = lst_runner.run(
    method="mcmillin",
    brightness_temperature_10=bt10,
    brightness_temperature_11=bt11,
)
print(f"   Range: {np.nanmin(lst_mcmillin):.1f} - {np.nanmax(lst_mcmillin):.1f} K")
print(f"   Mean:  {np.nanmean(lst_mcmillin):.1f} K (~{np.nanmean(lst_mcmillin)-273.15:.1f}°C)")

# ============================================================================
# STEP 6: Normalization for Temporal Comparison
# ============================================================================
# NRS (Normalized Relative Slope) standardizes LST to 0-1 range
# Useful for comparing multiple dates or locations

print("\n" + "=" * 70)
print("STEP 5: NORMALIZING FOR TEMPORAL COMPARISON")
print("=" * 70)

lst_sobrino_norm = nrs(lst_sobrino)
print(f"Original LST mean: {np.nanmean(lst_sobrino):.1f} K")
print(f"Normalized LST mean: {np.nanmean(lst_sobrino_norm):.4f}")
print("(Normalized range: 0.0 - 1.0)")

# ============================================================================
# STEP 7: Statistical Analysis
# ============================================================================

print("\n" + "=" * 70)
print("STEP 6: STATISTICAL ANALYSIS")
print("=" * 70)

print("\nOverall LST Statistics (Sobrino 1993 - recommended):")
print(f"  Minimum:  {np.nanmin(lst_sobrino):.1f} K ({np.nanmin(lst_sobrino)-273.15:.1f}°C)")
print(f"  Maximum:  {np.nanmax(lst_sobrino):.1f} K ({np.nanmax(lst_sobrino)-273.15:.1f}°C)")
print(f"  Mean:     {np.nanmean(lst_sobrino):.1f} K ({np.nanmean(lst_sobrino)-273.15:.1f}°C)")
print(f"  Std Dev:  {np.nanstd(lst_sobrino):.1f} K")
print(f"  Median:   {np.nanmedian(lst_sobrino):.1f} K ({np.nanmedian(lst_sobrino)-273.15:.1f}°C)")

# Urban Hot Island Effect Analysis
urban_lst = lst_sobrino[~vegetation_mask]
veg_lst = lst_sobrino[vegetation_mask]
uhi = np.nanmean(urban_lst) - np.nanmean(veg_lst)

print(f"\nUrban Heat Island Effect:")
print(f"  Urban core mean LST: {np.nanmean(urban_lst):.1f} K ({np.nanmean(urban_lst)-273.15:.1f}°C)")
print(f"  Vegetation edge LST: {np.nanmean(veg_lst):.1f} K ({np.nanmean(veg_lst)-273.15:.1f}°C)")
print(f"  UHI Magnitude: {uhi:.1f} K (~{uhi:.1f}°C warmer in urban areas)")

# ============================================================================
# STEP 8: Visualization
# ============================================================================

print("\n" + "=" * 70)
print("STEP 7: CREATING VISUALIZATIONS")
print("=" * 70)

print("\n" + "=" * 70)
print("STEP 7: VISUALIZATION (Skipped)")
print("=" * 70)
print("\nMatplotlib visualization requires NumPy <2.0")
print("Data computed successfully. To generate plots, downgrade NumPy:")
print("  pip install 'numpy<2'")

# ============================================================================
# STEP 8: Algorithm Comparison  
# ============================================================================
print("=" * 70)

comparison_data = {
    'Kerr (NDVI)': lst_kerr,
    'Sobrino 1993 (Emissivity)': lst_sobrino,
    'McMillin (Linear)': lst_mcmillin,
}

print(f"\n{'Algorithm':<25} {'Min (K)':>10} {'Max (K)':>10} {'Mean (K)':>10} {'Std (K)':>10}")
print("─" * 60)

for name, lst in comparison_data.items():
    print(f"{name:<25} {np.nanmin(lst):>10.1f} {np.nanmax(lst):>10.1f} "
          f"{np.nanmean(lst):>10.1f} {np.nanstd(lst):>10.1f}")

# ============================================================================
# STEP 10: Output Summary
# ============================================================================

print("\n" + "=" * 70)
print("ANALYSIS SUMMARY")
print("=" * 70)

summary = f"""
Location: Erbil City, Iraq (36.19°N, 44.01°E)
Date: June 15, 2024
Sensor: Landsat 9 TIRS
Grid Size: 100x100 pixels (~30km x 30km area)

KEY FINDINGS:
1. Urban Core Mean LST: {np.nanmean(lst_sobrino):.1f} K ({np.nanmean(lst_sobrino)-273.15:.1f}°C)
2. Urban Heat Island Effect: +{uhi:.1f}°C (urban vs. vegetated areas)
3. LST Range: {np.nanmin(lst_sobrino):.1f} - {np.nanmax(lst_sobrino):.1f} K
4. Hottest pixels reach {np.nanmax(lst_sobrino)-273.15:.1f}°C (typical for summer)

RECOMMENDATIONS:
• Use Sobrino 1993 algorithm for highest accuracy
• For real data, download from USGS Earth Explorer or Google Earth Engine
• Compare with multi-temporal analysis for trend detection
• Use normalized LST (NRS) for comparing different dates/locations

FILES CREATED:
(none - visualization skipped due to NumPy 2.x compatibility)

NEXT STEPS:
1. Download real Landsat 9 data from USGS Earth Explorer
2. Process actual thermal bands instead of synthetic data
3. Integrate with GIS for enhanced spatial analysis
4. Create time-series analysis (multiple dates)
5. Cross-validate with ground-truth temperature measurements
"""

print(summary)

print("=" * 70)
print("Analysis complete! Package ready for v0.0.3 release.")
print("=" * 70)
