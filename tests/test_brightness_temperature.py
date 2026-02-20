import numpy as np
import unittest
from numpy.testing import assert_array_almost_equal

from pylst.temperature import BrightnessTemperatureLandsat


class TestBrightnessTemperatureLandsat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bt = BrightnessTemperatureLandsat()

        # Typical constants for Landsat 8 & 9 TIRS (Band 10)
        # Update these from your actual implementation / metadata if different
        cls.K1 = 774.8853       # K1 constant band 10 (Collection 2)
        cls.K2 = 1321.0789      # K2 constant band 10 (Collection 2)
        cls.MULT = 3.3420e-04   # Radiance_mult_band_10
        cls.ADD = 0.10000       # Radiance_add_band_10

    def test_shape_preserved(self):
        band = np.random.randint(5000, 30000, size=(20, 30)).astype(np.float32)
        bt, _ = self.bt(band)           # assuming it returns (bt_array, something_else)
        self.assertEqual(band.shape, bt.shape)

    def test_returns_tuple(self):
        band = np.ones((10, 10), dtype=np.float32) * 20000
        result = self.bt(band)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)   # change this number if your method returns more/fewer items

    def test_zero_input_gives_reasonable_behavior(self):
        band = np.zeros((5, 5), dtype=np.float32)
        bt, _ = self.bt(band)
        # Usually radiance becomes very small or invalid → BT should be very low or NaN
        self.assertTrue(np.all(np.isnan(bt) | (bt <= 0)))

    def test_known_physical_value(self):
        # Manual calculation check using standard TOA radiance → brightness temperature formula
        dn = np.array([[13000.0]])          # example DN value
        radiance = dn * self.MULT + self.ADD
        bt_expected = self.K2 / np.log(self.K1 / radiance + 1)

        bt_computed, _ = self.bt(dn)
        # Allow ~0.1–0.5 K difference due to rounding/constants/formatting
        assert_array_almost_equal(bt_computed, bt_expected, decimal=1)

    def test_handles_nan(self):
        band = np.full((8, 8), 18000.0, dtype=np.float32)
        band[2:5, 3:6] = np.nan
        bt, _ = self.bt(band)
        self.assertTrue(np.isnan(bt[2:5, 3:6]).all())
        self.assertFalse(np.isnan(bt[0, 0]))  # outside the NaN region should be valid


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)