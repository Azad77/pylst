# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
# pylst/open/landsat_downloader.py

import ee
from datetime import datetime

def download_images(start_date, end_date, max_cloud_cover=20, region=None):
    """
    Download Landsat images from Google Earth Engine and export to Google Drive.

    Parameters:
    - start_date: Start date (formatted as 'YYYY-MM-DD').
    - end_date: End date (formatted as 'YYYY-MM-DD').
    - max_cloud_cover: Maximum allowed cloud cover percentage.
    - region: A GeoJSON-like geometry specifying the region of interest (optional).

    Returns:
    - None
    """
    # Initialize the Earth Engine API
    ee.Initialize()

    # Define a time range
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Filter Landsat collection based on specified criteria
    landsat_collection = (ee.ImageCollection('LANDSAT/LC08/C01/T1')
                         .filterDate(start_date, end_date)
                         .filterMetadata('CLOUD_COVER', 'less_than', max_cloud_cover)
                         )

    if region:
        # Filter by region of interest
        landsat_collection = landsat_collection.filterBounds(ee.Geometry.Polygon(region))

    # Print the number of images in the collection
    print("Number of images in the collection:", landsat_collection.size().getInfo())

    # Iterate over the images and export to Google Drive
    images = landsat_collection.toList(landsat_collection.size())
    for i in range(images.size().getInfo()):
        image = ee.Image(images.get(i))

        # Get the Landsat ID
        landsat_id = image.get('LANDSAT_ID').getInfo()

        # Define export parameters
        export_params = {
            'image': image,
            'description': "",  # Empty description
            'folder': 'GEE_exports',  # Specify the Google Drive folder
            'fileNamePrefix': f"Landsat_image_{i+1}",  # Use a prefix and system index
            'scale': 30,
            }            


        # If a region is specified, add it to export parameters
        if region:
            export_params['region'] = region

        # Export the image to Google Drive
        task = ee.batch.Export.image.toDrive(**export_params)
        task.start()
        print(f"Export task {i+1} started:", task.id)
