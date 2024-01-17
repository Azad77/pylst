# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
# Import necessary libraries
import pandas as pd
from rasterstats import zonal_stats

def calculate_zs(shapefile_path, raster_path):
    """
    Calculate zonal statistics for a given shapefile and raster.

    Parameters:
    - shapefile_path (str): Path to the shapefile containing the zones of interest.
    - raster_path (str): Path to the raster file for which zonal statistics are calculated.

    Returns:
    - df (pd.DataFrame): Pandas DataFrame containing the calculated zonal statistics.
    """

    # Extract zonal statistics using the rasterstats library
    stats = zonal_stats(shapefile_path, raster_path, stats=["min", "max", "mean", "median", "std", "count", "range", "sum",
                                                            "median", "majority", "minority", "unique", "nodata"], geojson_out=False)
    
    # Convert the results to a pandas DataFrame for easier analysis and manipulation
    df = pd.DataFrame(stats)

    # Save the DataFrame as a CSV file for further reference or sharing
    df.to_csv("zonal_stats.csv", index=True)

    # Return the DataFrame containing the zonal statistics
    return df
