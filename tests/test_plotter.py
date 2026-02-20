import unittest
import numpy as np
import os
import tempfile
import matplotlib
matplotlib.use('Agg')           # ← important for CI/headless
import matplotlib.pyplot as plt

from pylst.visualization.plotter import rastshow
import rasterio
from rasterio.transform import from_origin

class TestRastShow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.raster_path = os.path.join(self.temp_dir.name, "test_raster.tif")

        data = np.array([[1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9]], dtype=np.float32)

        transform = from_origin(0, 3, 1, 1)
        with rasterio.open(
            self.raster_path, 'w',
            driver='GTiff',
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs="EPSG:4326",           # modern style
            transform=transform
        ) as dst:
            dst.write(data, 1)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_runs_without_error(self):
        try:
            rastshow(self.raster_path)
        except Exception as e:
            self.fail(f"Failed to run: {e}")

    def test_accepts_vmin_vmax_and_other_kwargs(self):
        try:
            rastshow(
                self.raster_path,
                vmin=3,
                vmax=7,
                cmap='magma',
                title="Custom Title",
                colorbar_label="Intensity"
            )
        except Exception as e:
            self.fail(f"Failed with custom args: {e}")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)