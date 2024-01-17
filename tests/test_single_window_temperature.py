import numpy as np
import unittest

from pylst.temperature import MonoWindowLST

class TestMonoWindowLST(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setting up sample data and class instance for testing
        cls.sample_band_10 = np.zeros((5, 5))  # Creating a sample band 10 array
        cls.mask = np.random.randint(0, high=1, size=(5, 5), dtype=int)  # Creating a random mask
        cls.mask = cls.mask == 1  # Converting random mask to boolean type
        cls.lst_algorithm = MonoWindowLST()  # Initializing MonoWindowLST instance

    def test_output_and_input_size_equal(self):
        # Testing if the output size matches input size
        output = self.lst_algorithm(
            emissivity_10=self.sample_band_10,
            brightness_temperature_10=self.sample_band_10,
            mask=self.mask,
        )
        self.assertEqual(self.sample_band_10.shape, output.shape)

    def test_max_temp_less_than_or_equal_max_earth_temp(self):
        # Testing if the maximum temperature in the algorithm is within known Earth temperature limits
        self.assertEqual(self.lst_algorithm.max_earth_temp, 273.15 + 56.7)

if __name__ == "__main__":
    # Running the unit tests
    unittest.main()

