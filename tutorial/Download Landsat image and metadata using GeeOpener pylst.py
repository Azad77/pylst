# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 18:56:51 2024

@author: gardi
"""

import ee
# Authenticate using your GEE account credentials
ee.Authenticate()

ee.Initialize()

from pylst.open.geeopener import GeeOpener

# Create an instance of the GeeOpener class
gee_opener = GeeOpener()

# Specify region, start date, and end date
region = ee.Geometry.Point(44.0092, 36.1911).buffer(10000)
start_date = '2021-10-01'
end_date = '2021-11-01'

# Open the Landsat image from Google earth Engine and use landsat image ID as the filename with ".tif" 
gee_opener.open(region, start_date, end_date)