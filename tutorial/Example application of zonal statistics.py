# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:40:44 2024

@author: gardi
"""
# Import the calculate_zs function from the zonstat module in the pylst.spatial_analysis package
from pylst.spatial_analysis.zonstat import calculate_zs

# Define the path to the shapefile containing the administrative boundaries (in this case, Erbil_Admi_3.shp)
shapefile_path = "C:\\Users\\gardi\\Erbil_Shapefile\\Erbil_Admi_3.shp"

# Define the path to the raster file (in this case, Chirps_Erbil.tif) for spatial analysis
raster_path = "C:\\Users\\gardi\\Chirps_Erbil.tif"

# Call the calculate_zs function, passing the shapefile and raster paths as arguments
# This function performs zone-based statistics, calculating values for each zone in the shapefile from the corresponding raster data
df = calculate_zs(shapefile_path, raster_path)

# Print the resulting DataFrame that contains the calculated zone-based statistics
print(df)

