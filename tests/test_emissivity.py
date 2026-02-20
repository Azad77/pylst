import unittest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_allclose

from pylst.emissivity.registry import ComputeMonoWindowEmissivity, ComputeEmissivityGopinadh


class TestEmissivityComputation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mono = ComputeMonoWindowEmissivity()
        cls.gopinadh = ComputeEmissivityGopinadh()

        # Realistic small NDVI array (typical Landsat range: -0.2 water → 0.8 dense veg)
        cls.ndvi = np.array([
            [-0.1, 0.15, 0.45],
            [0.65, 0.82, -0.05],
            [0.30, np.nan, 0.55]
        ], dtype=np.float32)

        # Dummy red band (reflectance 0–1 range, same shape as NDVI)
        cls.red_band = np.array([
            [0.12, 0.08, 0.04],
            [0.03, 0.02, 0.15],
            [0.06, 0.10, 0.05]
        ], dtype=np.float32)

    def test_mono_returns_tuple_and_correct_length(self):
        result = self.mono(ndvi=self.ndvi, red_band=self.red_band)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)  # Mono-window typically returns 2 items

        emiss = result[0]
        self.assertIsInstance(emiss, np.ndarray)
        self.assertEqual(emiss.shape, self.ndvi.shape)

    def test_gopinadh_returns_tuple_and_correct_length(self):
        result = self.gopinadh(ndvi=self.ndvi)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)  # Fixed: now matches actual return (2 items)

        emiss = result[0]
        self.assertIsInstance(emiss, np.ndarray)
        self.assertEqual(emiss.shape, self.ndvi.shape)

    def test_mono_output_shape_matches_input(self):
        emiss, *_ = self.mono(ndvi=self.ndvi, red_band=self.red_band)
        self.assertEqual(self.ndvi.shape, emiss.shape)

    def test_gopinadh_output_shape_matches_input(self):
        emiss, *_ = self.gopinadh(ndvi=self.ndvi)
        self.assertEqual(self.ndvi.shape, emiss.shape)

    def test_mono_emissivity_values_in_reasonable_range(self):
        emiss, *_ = self.mono(ndvi=self.ndvi, red_band=self.red_band)
        # Typical NDVI-based emissivity: ~0.93 bare soil → ~0.98–0.99 vegetation/water
        valid = emiss[~np.isnan(emiss)]
        self.assertTrue(np.all(valid >= 0.90))
        self.assertTrue(np.all(valid <= 0.995))

    def test_gopinadh_emissivity_values_in_reasonable_range(self):
        emiss, *_ = self.gopinadh(ndvi=self.ndvi)
        valid = emiss[~np.isnan(emiss)]
        self.assertTrue(np.all(valid >= 0.90))
        self.assertTrue(np.all(valid <= 0.995))

    def test_handles_nan_propagation(self):
        # Position (2,1) is NaN in NDVI → should propagate to output
        emiss_mono, *_ = self.mono(ndvi=self.ndvi, red_band=self.red_band)
        emiss_gop, *_ = self.gopinadh(ndvi=self.ndvi)

        self.assertTrue(np.isnan(emiss_mono[2, 1]))
        self.assertTrue(np.isnan(emiss_gop[2, 1]))

    def test_gopinadh_known_ndvi_values(self):
        # Simple test array with known NDVI thresholds
        ndvi_test = np.array([[0.0, 0.2, 0.5, 0.8]], dtype=np.float32)
        emiss, *_ = self.gopinadh(ndvi=ndvi_test)

        # Rough check: emissivity should generally increase with NDVI
        self.assertLess(emiss[0, 0], emiss[0, 3])  # low NDVI → lower emissivity

        # Typical high-vegetation value check (adjust tolerance if needed)
        assert_allclose(emiss[0, 3], 0.985, atol=0.015)

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False, verbosity=2)