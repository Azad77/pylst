# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
import pylst
# Importing the functions from plotter.py
from pylst.visualization import rastshow, plot_data

# Example data to plot
data = [1, 2, 3, 4, 5]

# Calling the plot_data function
plot_data(data)

# Path to the raster file
path_to_raster = ('C:\\Users\\gardi\\Chirps_Erbil.tif')

# Calling the rastshow function to display the raster
# Call rastshow with a valid figsize argument
rastshow(
    path_to_raster,
    title='Rain of Erbil from CHIRPS',
    colorbar_label='Ran (mm)',
    xlabel='Longitude',
    ylabel='Latitude',
    cmap='viridis',
    figsize=(8, 6)  # Change to valid width and height values in inches
)
