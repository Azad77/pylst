# pylst/open/landsat_downloader.py
"""
Google Earth Engine Landsat image downloader for pylst.

Downloads Landsat surface reflectance (Collection 2 Level-2) images,
filtered by date, cloud cover, and region of interest, and exports to Google Drive.

Requires:
- Google Earth Engine account + authenticated session (ee.Authenticate() once)
- pip install earthengine-api

Main function:
- download_images(): Start export tasks to Drive
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# Earth Engine is an optional dependency used by download_images.
# Guard the import so that the package can be imported even when the
# earthengine-api is not installed (e.g. during unit testing).
try:
    import ee
except Exception:  # pragma: no cover - dependency missing or incompatible
    ee = None


def download_images(
    start_date: str,
    end_date: str,
    max_cloud_cover: float = 20.0,
    region: Optional[Union[dict, "ee.Geometry", str]] = None,
    collection: str = "LANDSAT/LC08/C02/T1_L2",  # Surface reflectance, Landsat 8/9
    folder: str = "pylst_exports",
    scale: int = 30,
    max_images: int = 50,
    description_prefix: str = "pylst_landsat",
) -> list["ee.batch.Task"]:
    # confirm the earthengine-api was imported successfully
    if ee is None:
        raise ImportError(
            "earthengine-api is required to use download_images(). install "
            "it with `pip install earthengine-api` or skip invoking this "
            "function while running tests."
        )
    """
    Start export tasks for Landsat images to Google Drive.

    Args:
        start_date: Start date ('YYYY-MM-DD')
        end_date: End date ('YYYY-MM-DD')
        max_cloud_cover: Maximum cloud cover percentage (0–100)
        region: Optional region of interest:
                - dict: GeoJSON geometry
                - ee.Geometry object
                - str: path to GeoJSON file
        collection: EE collection ID
                    - "LANDSAT/LC08/C02/T1_L2" → Landsat 8 SR (default)
                    - "LANDSAT/LC09/C02/T1_L2" → Landsat 9 SR
                    - "LANDSAT/LE07/C02/T1_L2" → Landsat 7 SR
                    - "LANDSAT/LT05/C02/T1_L2" → Landsat 5 SR
        folder: Google Drive folder to save exports
        scale: Pixel scale in meters (default 30 m)
        max_images: Maximum number of images to export
        description_prefix: Prefix for task & file names

    Returns:
        List of started ee.batch.Task objects (can be used to monitor status)

    Example:
        tasks = download_images(
            "2024-01-01", "2024-12-31",
            max_cloud_cover=10,
            region={"type": "Polygon", "coordinates": [[[43.9, 36.5], ...]]},
            collection="LANDSAT/LC09/C02/T1_L2",
            folder="Erbil_LST_2024"
        )
    """
    # Initialize Earth Engine (will prompt for auth if needed)
    try:
        ee.Initialize()
    except Exception as e:
        raise RuntimeError(
            "Earth Engine initialization failed. Run `ee.Authenticate()` first."
        ) from e

    # Validate dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start >= end:
            raise ValueError("start_date must be before end_date")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}") from e

    # Load collection
    col = ee.ImageCollection(collection).filterDate(start, end)

    # Cloud cover filter
    if max_cloud_cover is not None:
        col = col.filter(ee.Filter.lt("CLOUD_COVER", max_cloud_cover))

    # Region filter
    if region is not None:
        if isinstance(region, dict):
            region = ee.Geometry(region)
        elif isinstance(region, str):
            with open(region) as f:
                geojson = json.load(f)
            region = ee.Geometry(geojson["features"][0]["geometry"])
        if not isinstance(region, ee.Geometry):
            raise TypeError("region must be dict, GeoJSON path, or ee.Geometry")
        col = col.filterBounds(region)

    # Limit number of images
    col = col.limit(max_images)

    # determine how many images are available before converting to a list
    count = col.size().getInfo()
    print(f"Found {count} images matching criteria.")

    if count == 0:
        # nothing to export; return an empty list and avoid calling toList(0)
        return []

    # Get list of images (safe now that count > 0)
    image_list = col.toList(count)

    tasks = []

    for i in range(count):
        image = ee.Image(image_list.get(i))

        # Get useful properties for filename
        date = image.date().format("YYYY-MM-dd").getInfo()
        id_short = image.id().getInfo().split("/")[-1]

        desc = f"{description_prefix}_{date}_{id_short}"

        export_params = {
            "image": image,
            "description": desc,
            "folder": folder,
            "fileNamePrefix": desc,
            "scale": scale,
            "region": region,
            "maxPixels": 1e13,
        }

        task = ee.batch.Export.image.toDrive(**export_params)
        task.start()

        print(f"Task {i+1}/{count} started: {desc} (ID: {task.id})")
        tasks.append(task)

    return tasks