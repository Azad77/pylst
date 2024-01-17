import numpy as np
import unittest

from pylst.temperature import BrightnessTemperatureLandsat

# Test class for BrightnessTemperatureLandsat
class TestBrightnessTemperature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setting up a sample band with all zeros
        cls.sample_band_10 = np.zeros((5, 5))
        # Creating an instance of the BrightnessTemperatureLandsat class
        cls.brightness_temp = BrightnessTemperatureLandsat()

    # Test whether the method returns a tuple
    def test_method_returns_tuple(self):
        output = self.brightness_temp(self.sample_band_10)
        self.assertIsInstance(output, tuple)

    # Test whether the output size matches the input size
    def test_output_and_input_size_equal(self):
        output = self.brightness_temp(self.sample_band_10)
        self.assertEqual(self.sample_band_10.shape, output[0].shape)


if __name__ == "__main__":
    unittest.main()  # Run the tests if this script is executed directly
