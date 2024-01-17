# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 21:15:34 2024

@author: Azad Rasul
"""

# Import the analyze_images function from the changedet module in the pylst.spatial_analysis package
from pylst.spatial_analysis.changedet import analyze_images

# Define paths to Landsat images for analysis
landsat_image_path1 = "D:\\UHI_Baghdad\\LST_Baghdad\\LST23_07_2021_Landsat8_NRS.tif"
landsat_image_path2 = "D:\\UHI_Baghdad\\LST_Baghdad\\LST14_07_2000_Landsat7_NRS.tif"

# Define the output path for saving the analysis result as GeoTIFF
output_path_geotiff = "D:\\UHI_Baghdad\\analysis_result_difference1.tif"

# Call the analyze_images function
analysis_result = analyze_images(landsat_image_path1, landsat_image_path2, output_path_geotiff)

# Print the analysis result
if analysis_result:
    # If analysis was successful, print the result and the path where the GeoTIFF result is saved
    print(analysis_result)
    print(f"Analysis result saved to: {output_path_geotiff}")
else:
    # If analysis failed, print an error message
    print("Analysis failed.")
