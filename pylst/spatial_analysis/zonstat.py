# pylst/spatial_analysis/zonstat.py
"""
Zonal statistics tools for pylst – summarize raster values (LST, NDVI, emissivity, etc.)
within vector zones (polygons from shapefile/GeoJSON).

Main function:
- calculate_zs(): Compute statistics inside zones and return as pandas DataFrame.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Literal, Optional, Union

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterstats import zonal_stats


ValidStats = Literal[
    "count", "min", "max", "mean", "median", "std", "sum", "range",
    "var", "percentile", "majority", "minority", "unique", "nodata"
]


def calculate_zs(
    zones: str | Path | gpd.GeoDataFrame,
    raster: str | Path | rasterio.io.DatasetReader,
    stats: list[ValidStats] | str = "mean",
    band: int = 1,
    nodata: Optional[float] = None,
    prefix: str = "zonal_",
    all_touched: bool = False,
    categorical: bool = False,
    output_csv: Optional[str | Path] = None,
) -> pd.DataFrame:
    """
    Compute zonal statistics between vector zones and a raster layer.

    Args:
        zones: Path to shapefile/GeoJSON or GeoDataFrame with polygons
        raster: Path to GeoTIFF or open rasterio dataset
        stats: Statistics to compute (string or list). Examples:
               "mean", ["min", "max", "mean", "std"], "all"
        band: Band number to use (default 1)
        nodata: Override/force nodata value
        prefix: Prefix added to output column names (default "zonal_")
        all_touched: If True, all pixels touched by polygon are included
        categorical: Treat raster values as categories (e.g. land cover classes)
        output_csv: Optional path to save results as CSV

    Returns:
        pandas DataFrame with one row per zone and columns for each statistic

    Raises:
        FileNotFoundError, ValueError, rasterio.errors.RasterioIOError
    """
    # Normalize inputs
    if isinstance(zones, (str, Path)):
        zones = Path(zones)
        if not zones.is_file():
            raise FileNotFoundError(f"Zones file not found: {zones}")
        zones_gdf = gpd.read_file(zones)
    elif isinstance(zones, gpd.GeoDataFrame):
        zones_gdf = zones.copy()
    else:
        raise TypeError("zones must be path or GeoDataFrame")

    if isinstance(raster, (str, Path)):
        raster = Path(raster)
        if not raster.is_file():
            raise FileNotFoundError(f"Raster file not found: {raster}")
    elif not isinstance(raster, rasterio.io.DatasetReader):
        raise TypeError("raster must be path or rasterio DatasetReader")

    # Prepare stats
    if stats == "all":
        stats = ["count", "min", "max", "mean", "median", "std", "sum", "range"]
    elif isinstance(stats, str):
        stats = [stats]

    # Run zonal_stats
    try:
        zs_results = zonal_stats(
            zones_gdf,
            raster,
            stats=stats,
            band=band,
            nodata=nodata,
            affine=raster.transform if hasattr(raster, "transform") else None,
            all_touched=all_touched,
            categorical=categorical,
            geojson_out=False,
        )
    except Exception as e:
        raise RuntimeError(f"zonal_stats failed: {e}") from e

    # Convert to DataFrame
    df = pd.DataFrame(zs_results)

    # Add prefix to statistic columns
    stat_cols = [col for col in df.columns if col in stats or col.startswith("cat_")]
    rename_dict = {col: f"{prefix}{col}" for col in stat_cols}
    df = df.rename(columns=rename_dict)

    # Optionally join back to original zones (e.g. keep zone IDs/names)
    if "id" in zones_gdf.columns or zones_gdf.index.name:
        df = zones_gdf.reset_index().join(df)

    # Save to CSV if requested
    if output_csv is not None:
        output_csv = Path(output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv, index=False)
        print(f"Zonal statistics saved to: {output_csv}")

    return df