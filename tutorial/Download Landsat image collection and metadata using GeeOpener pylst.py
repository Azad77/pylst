# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 18:56:51 2024

@author: gardi
"""

import ee
# Authenticate using your GEE account credentials
ee.Authenticate()
ee.Initialize()

# from pylst.open.coopener import ColOpener
import sys
sys.path.append('D:\Python\pylst\pylst12\pylst\open')

from coopener import ColOpener

#from .coopener import ColOpener

# Create an instance of the GeeOpener class
gee_opener = ColOpener()

# Specify region, start date, and end date
region = ee.Geometry.Point(44.0092, 36.1911).buffer(100)
start_date = '2020-07-01'
end_date = '2020-08-01'

# Open the Landsat image collection from Google Earth Engine
gee_opener.open(region, start_date, end_date)
