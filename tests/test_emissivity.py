import unittest
import numpy as np

from pylst.emissivity.emissivity import ComputeMonoWindowEmissivity, ComputeEmissivityGopinadh

# Test class for testing emissivity computation methods
class TestEmissivityComputation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Setting up a sample NDVI and red band with all zeros
        #cls.sample_ndvi = 'band_4_red_Landsat.tif'
        #cls.sample_red_band = 'band_4_red_Landsat.tif'
        # Sample NDVI and red band data (replace with your actual data)
        self.sample_ndvi = np.array([[0.1, 0.2], [0.3, 0.4]])
        self.sample_red_band = np.array([[0.5, 0.6], [0.7, 0.8]])

    # Test whether the methods return a tuple
    def test_method_returns_tuple(self):
        # Instantiate the classes for different emissivity computation methods
        mono_window_emissivity = ComputeMonoWindowEmissivity()
        #nbem_emissivity = ComputeEmissivityNBEM()
        gopinadh_emissivity = ComputeEmissivityGopinadh()

        # Compute emissivity for the sample data using different methods
        output_mono_window = mono_window_emissivity(ndvi=self.sample_ndvi, red_band=self.sample_red_band)
        #output_nbem = nbem_emissivity(ndvi=self.sample_ndvi, red_band=self.sample_red_band)
        output_gopinadh = gopinadh_emissivity(ndvi=self.sample_ndvi)

        # Assert that the outputs are tuples
        self.assertIsInstance(output_mono_window, tuple)
        #self.assertIsInstance(output_nbem, tuple)
        self.assertIsInstance(output_gopinadh, tuple)

    # Test whether the output sizes match the input sizes
    def test_output_and_input_size_equal(self):
        # Instantiate the class for mono-window emissivity computation method
        mono_window_emissivity = ComputeMonoWindowEmissivity()

        # Compute emissivity for the sample data using the mono-window method
        output = mono_window_emissivity(ndvi=self.sample_ndvi, red_band=self.sample_red_band)

        # Assert that the output shapes match the input shapes
        self.assertEqual(self.sample_ndvi.shape, output[0].shape)
        self.assertEqual(self.sample_ndvi.shape, output[1].shape)

# Run the tests if this script is executed directly
if __name__ == "__main__":
    unittest.main()
