# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 10:16:04 2024

@author: gardi
"""

#src = rasterio.open("C:/Users/gardi/NDVI.tif")


from localtileserver import TileClient, get_leaflet_tile_layer
from ipyleaflet import Map

client = TileClient('C:/Users/gardi/NDVI.tif')

layer = get_leaflet_tile_layer(client)

m = Map(center=client.center(), zoom=client.default_zoom)
m.add(layer)
m

# Save the interactive map as an HTML file (optional)
m.save("interactive_map22.html")
