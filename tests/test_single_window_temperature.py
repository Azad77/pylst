# tests/test_single_window_temperature.py
# -*- coding: utf-8 -*-
"""
Unit tests for MonoWindowLST (mono-window land surface temperature algorithm)
Author: Azad Rasul
"""
import unittest
import numpy as np
from pylst.temperature import MonoWindowLST

class TestMonoWindowLST(unittest.TestCase):
    """Test suite for the MonoWindowLST class."""

    @classmethod
    def setUpClass(cls):
        """Set up reusable test data and algorithm instance."""
        cls.algorithm = MonoWindowLST()
        # Fixed, small test arrays (5×5) for reproducibility
        cls.brightness_temp = np.array([
            [290., 295., 300., 305., 310.],
            [288., 293., 298., 303., 308.],
            [285., 290., 295., 300., 305.],
            [280., 285., 290., 295., 300.],
            [275., 280., 285., 290., 295.],
        ], dtype=np.float32)

        cls.emissivity = np.array([
            [0.96, 0.97, 0.98, 0.97, 0.96],
            [0.95, 0.96, 0.97, 0.98, 0.97],
            [0.94, 0.95, 0.96, 0.97, 0.98],
            [0.93, 0.94, 0.95, 0.96, 0.97],
            [0.92, 0.93, 0.94, 0.95, 0.96],
        ], dtype=np.float32)

        cls.mask = np.array([
            [True, True, True, False, True],
            [True, False, True, True, True],
            [False, True, True, True, False],
            [True, True, False, True, True],
            [True, True, True, True, False],
        ], dtype=bool)

    # Example for one test — apply the same pattern to all
    def test_output_shape_matches_input(self):
        lst = self.algorithm.compute(
            brightness_temperature_10 = self.brightness_temp,
            emissivity_10             = self.emissivity,
            mask                      = self.mask,
        )
        self.assertEqual(self.brightness_temp.shape, lst.shape)


    def test_masked_pixels_get_nan(self):
        lst = self.algorithm.compute(
            brightness_temperature_10 = self.brightness_temp,
            emissivity_10             = self.emissivity,
            mask                      = self.mask,
        )
        masked_locations = ~self.mask
        self.assertTrue(np.all(np.isnan(lst[masked_locations])))
        self.assertFalse(np.any(np.isnan(lst[self.mask])))


    def test_lst_values_are_reasonable(self):
        lst = self.algorithm.compute(
            brightness_temperature_10 = self.brightness_temp,
            emissivity_10             = self.emissivity,
            mask                      = self.mask,
        )
        valid_lst = lst[self.mask]
        self.assertTrue(np.all(valid_lst >= 250))
        self.assertTrue(np.all(valid_lst <= 345))


    def test_lst_higher_than_brightness_temp_on_average(self):
        lst = self.algorithm.compute(
            brightness_temperature_10 = self.brightness_temp,
            emissivity_10             = self.emissivity,
            mask                      = self.mask,
        )
        valid_bt = self.brightness_temp[self.mask]
        valid_lst = lst[self.mask]
        mean_diff = np.mean(valid_lst - valid_bt)
        self.assertGreater(mean_diff, -1.0)


    def test_raises_on_invalid_input_shapes(self):
        with self.assertRaises(ValueError):
            self.algorithm.compute(
                brightness_temperature_10 = self.brightness_temp[:-1, :],  # mismatched shape
                emissivity_10             = self.emissivity,
                mask                      = self.mask,
            )
if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)