# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
# pylst/open/remopener.py
import rasterio
from io import BytesIO

class RemoteOpener:
    @staticmethod
    def open(remote_url, *args, **kwargs):
        try:
            # Open the remote raster file
            with rasterio.Env():
                with rasterio.open(remote_url) as src:
                    # Read the content of the raster file
                    content = src.read()
                    print(f"Successfully opened remote file: {remote_url}")
                    return BytesIO(content.tobytes())
        except rasterio.errors.RasterioError as e:
            print(f"Failed to open remote file: {remote_url}. Error: {e}")
            return None
