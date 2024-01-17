# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
# Import necessary libraries for image analysis
import rasterio
import numpy as np

def analyze_images(image_path1, image_path2, output_path):
    """
    Analyzes two images and saves the difference as a GeoTIFF.

    Parameters:
    - image_path1 (str): File path to the first image.
    - image_path2 (str): File path to the second image.
    - output_path (str): File path to save the analysis result as GeoTIFF.

    Returns:
    - result (dict): A dictionary containing the analysis results or None if an error occurs.
    """
    try:
        # Open the images using rasterio
        with rasterio.open(image_path1) as src1, rasterio.open(image_path2) as src2:
            # Read the image data
            image1 = src1.read(1)  # Assuming a single band for simplicity
            image2 = src2.read(1)  # Assuming a single band for simplicity

            # Check if the shapes of the two images are compatible
            if image1.shape != image2.shape:
                raise ValueError("Images have different shapes and cannot be subtracted.")

            # Perform any desired analysis on the images
            # For example, you can calculate the difference between the two images
            image_difference = np.subtract(image2, image1)

            # You can add more analysis steps here based on your specific requirements

            # Store the results in a dictionary
            result = {
                "image_difference": image_difference,
                # Add more result keys and values as needed
            }

            # Get metadata from one of the input images (assuming both have the same properties)
            meta = src1.meta.copy()

            # Update metadata for the output GeoTIFF
            meta.update(driver='GTiff', count=1, dtype='float32')

            # Create a new GeoTIFF file for the image_difference
            with rasterio.open(output_path, 'w', **meta) as dst:
                dst.write(image_difference.astype('float32'), 1)

            return result

    except Exception as e:
        # Handle exceptions such as file not found or invalid file format
        print(f"Error during image analysis: {e}")
        return None
