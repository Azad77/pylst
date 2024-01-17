# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 00:43:52 2024

@author: gardi
"""

import folium

political_countries_url = (
    "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
)

m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron")
folium.GeoJson(political_countries_url).add_to(m)

m.save("footprint.html")