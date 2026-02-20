import ee

# Re-init if needed
ee.Initialize()

# Your region (from earlier)
erbil_point = ee.Geometry.Point([44.009196, 36.191108])
search_region = erbil_point.buffer(5000)

# Find the same image (or any recent low-cloud one)
collection = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
    .filterDate("2024-06-01", "2024-07-01") \
    .filterBounds(search_region) \
    .filter(ee.Filter.lt('CLOUD_COVER', 20)) \
    .limit(1)

img = collection.first()

# Critical: select ONLY UInt16 bands (or cast QA if needed)
img_to_export = img.select(['SR_B4', 'SR_B5', 'ST_B10'])
# If you want QA_PIXEL: .addBands(img.select('QA_PIXEL').uint16())

task = ee.batch.Export.image.toDrive(
    image=img_to_export,
    description='erbil_l9_202406_fix',
    folder='pylst_erbil_l9_c2_fixed',
    fileNamePrefix='LC09_176029_20240606_fixed',
    region=search_region,
    scale=30,
    maxPixels=1e10,
    crs='EPSG:4326'
)

task.start()
print("Fixed export task started:", task.id)
print("Check Tasks tab – this should succeed.")

import rasterio
import numpy as np

with rasterio.open(local_tif) as src:
    print("File info:")
    print(f"  CRS: {src.crs}")
    print(f"  Width x Height: {src.width} x {src.height}")
    print(f"  Number of bands: {src.count}")
    print(f"  Band descriptions: {src.descriptions}")
    print(f"  Band indexes: {src.indexes}")
    print(f"  Data type: {src.dtypes[0]}")  # should be 'uint16'
    print(f"  Transform (affine): {src.transform}")

    # Optional: show min/max per band to confirm data exists
    for i in range(1, src.count + 1):
        data = src.read(i)
        print(f"  Band {i} ({src.descriptions[i-1] if src.descriptions else 'unnamed'}): "
              f"min={data.min()}, max={data.max()}, mean={data.mean():.1f}")
        
 print("\nRunning emissivity estimation (gopinadh method)...")
emm_return = emissivity_runner.run(method="gopinadh", ndvi=ndvi)

# Handle both single array and tuple return styles
if isinstance(emm_return, tuple) and len(emm_return) == 2:
    emm10, emm11 = emm_return
    emm_used = emm10  # or (emm10 + emm11)/2
    print("Emissivity returned as tuple → using emm10 for mono-window")
else:
    emm_used = emm_return
    print("Emissivity returned as single array")

print("Emissivity used statistics:")
print(f"  min: {np.nanmin(emm_used):.3f}")
print(f"  mean: {np.nanmean(emm_used):.3f}")
print(f"  max: {np.nanmax(emm_used):.3f}")

print("\nRunning custom mono-window LST...")
lst_custom = lst_runner.run(
    method="mono-window",
    brightness_temperature_10 = lst_k,     # Kelvin
    emissivity_10             = emm_used
)

print("Custom LST statistics (°C):")
print(f"  min: {np.nanmin(lst_custom)-273.15:.1f}")
print(f"  mean: {np.nanmean(lst_custom)-273.15:.1f}")
print(f"  max: {np.nanmax(lst_custom)-273.15:.1f}")

out_path = r"C:\Users\Azad\Documents\erbil_mono_window_lst_20240606.tif"

with rasterio.open(local_tif) as src:
    meta = src.meta.copy()
    meta.update(dtype=rasterio.float32, count=1, nodata=np.nan)

with rasterio.open(out_path, 'w', **meta) as dst:
    dst.write((lst_custom).astype(np.float32), 1)

print("Saved:", out_path)