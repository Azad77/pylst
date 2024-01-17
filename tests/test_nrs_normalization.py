# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
import unittest
import numpy as np
from pylst.normalization.normalizer import nrs

class TestNRSNormalization(unittest.TestCase):
    
    def test_nrs_normalization(self):
        # Create a sample input array
        lst = np.array([1, 2, 3, 4, 5])
        
        # Compute NRS using my function
        result = nrs(lst)
        
        # Expected calculation of NRS
        NR = lst / np.sqrt(np.sum(np.square(lst)))
        expected_result = NR * (np.mean(lst)) / np.mean(NR)

        # Assert that the computed NRS matches the expected result
        np.testing.assert_array_almost_equal(result, expected_result, decimal=6)
        
if __name__ == '__main__':
    unittest.main()
    