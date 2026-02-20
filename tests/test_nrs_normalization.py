# -*- coding: utf-8 -*-
"""
Unit tests for NRS (Normalized Ratio Something) normalization function.

@author: Azad Rasul
@date: 2025-2026
"""
import unittest
import numpy as np

# Import the function you want to test
from pylst.normalization.normalizer import nrs


class TestNRSNormalization(unittest.TestCase):
    """Test suite for the nrs() normalization function."""

    def test_basic_linear_sequence(self):
        """Test with simple increasing sequence."""
        lst = np.array([1, 2, 3, 4, 5], dtype=float)
        result = nrs(lst)

        # Manual / expected calculation
        norm = lst / np.sqrt(np.sum(lst**2))
        expected = norm * (np.mean(lst) / np.mean(norm))

        np.testing.assert_array_almost_equal(
            result, expected, decimal=8,
            err_msg="Basic linear sequence normalization failed"
        )

    def test_all_equal_values(self):
        """When all values are equal → should return values close to 1."""
        lst = np.array([7, 7, 7, 7], dtype=float)
        result = nrs(lst)

        np.testing.assert_array_almost_equal(
            result, [1.0, 1.0, 1.0, 1.0],
            decimal=10,
            err_msg="All-equal input should produce values ≈ 1.0"
        )

    def test_single_element(self):
        """Single element array → should return [1.0]"""
        lst = np.array([42.0])
        result = nrs(lst)
        np.testing.assert_array_almost_equal(
            result, [1.0],
            decimal=10,
            err_msg="Single element should normalize to 1.0"
        )

    def test_zero_array(self):
        """All zeros → mean=0 → should return zeros (or handle gracefully)"""
        lst = np.zeros(5)
        result = nrs(lst)

        # Most sensible mathematical result in this case is zeros
        np.testing.assert_array_equal(
            result, np.zeros(5),
            err_msg="All-zero input should return all zeros"
        )

    def test_negative_and_positive_values(self):
        """Input with both positive and negative values"""
        lst = np.array([-2, -1, 0, 3, 6], dtype=float)
        result = nrs(lst)

        norm = lst / np.sqrt(np.sum(lst**2))
        expected = norm * (np.mean(lst) / np.mean(norm))

        np.testing.assert_array_almost_equal(
            result, expected, decimal=8,
            err_msg="Normalization with negative values failed"
        )

    def test_float_precision_and_larger_array(self):
        """Somewhat larger array with floating point values"""
        lst = np.array([1.5, 2.7, 0.3, 8.1, 4.2, 5.6], dtype=float)
        result = nrs(lst)

        norm = lst / np.sqrt(np.sum(lst**2))
        expected = norm * (np.mean(lst) / np.mean(norm))

        np.testing.assert_allclose(
            result, expected, rtol=1e-10, atol=1e-12,
            err_msg="Larger float array normalization check failed"
        )


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)
    # You can also run with: python -m unittest test_normalizer.py -v