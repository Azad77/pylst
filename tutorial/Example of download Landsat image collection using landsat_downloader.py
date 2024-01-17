# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
# pylst/open/example_usage.py

# Import the download_images function from the landsat_downloader module
from landsat_downloader import download_images

# Specify the start and end dates for the Landsat image collection
start_date = "2020-07-01"
end_date = "2020-07-16"

# Set the maximum allowed cloud cover percentage
max_cloud_cover = 20

# Define the region of interest as a bounding box (longitude, latitude)
region = [[-120, 34], [-120, 35], [-119, 35], [-119, 34], [-120, 34]]

# Call the download_images function to download Landsat images
download_images(start_date, end_date, max_cloud_cover, region)
