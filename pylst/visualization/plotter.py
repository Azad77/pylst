# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
# pylst/visualization/plotter.py
import matplotlib.pyplot as plt
import cv2
import rasterio
from rasterio.plot import show

def plot_data(data):
    # Function to plot data using matplotlib
    plt.plot(data)
    plt.show()

from localtileserver import TileClient, get_leaflet_tile_layer
from ipyleaflet import Map

def create_interactive_map(tif_path):
    # Create a TileClient and get the tile layer
    client = TileClient(tif_path)
    layer = get_leaflet_tile_layer(client)

    # Create a map centered around the data
    m = Map(center=client.center(), zoom=client.default_zoom)
    
    # Add the tile layer to the map
    m.add(layer)
    
    return m



def rastshow(path_to_raster, title='', colorbar_label='', figsize='', xlabel='', ylabel='', cmap='viridis', extent=None):
    # Open the raster dataset
    with rasterio.open(path_to_raster) as src:
        # Display the raster data
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        show(src, ax=ax, title=title, cmap=cmap, extent=extent)
        plt.colorbar(ax=ax, mappable=ax.images[0], label=colorbar_label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.show()

def histogram_equalization(image_path):
    # Function for histogram equalization using OpenCV
    img = cv2.imread(image_path, 0)
    equ = cv2.equalizeHist(img)

    # Display original and equalized images side by side
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Original Image')

    plt.subplot(1, 2, 2)
    plt.imshow(equ, cmap='gray')
    plt.title('Equalized Image')

    plt.show()

