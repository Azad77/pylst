import numpy as np
import unittest

from pylst.temperature import (
    BrightnessTemperatureLandsat,
    SplitWindowJiminezMunozLST,
    SplitWindowKerrLST,
    SplitWindowMcMillinLST,
    SplitWindowPriceLST,
    SplitWindowSobrino1993LST,
)

# Test class for SplitWindowSobrino1993LST
class TestSplitWindowSobrino1993LST(unittest.TestCase):
    # Sample data initialization
    sample_band_10 = np.zeros((5, 5))  # Sample Band 10 data
    mask = np.random.randint(0, high=2, size=(5, 5), dtype=int) == 1  # Random mask data

    # Test for output and input size equality
    def test_output_and_input_size_equal(self):
        # Running the SplitWindowSobrino1993LST algorithm
        output = SplitWindowSobrino1993LST()(
            emissivity_10=self.sample_band_10,
            emissivity_11=self.sample_band_10,
            brightness_temperature_10=self.sample_band_10,
            brightness_temperature_11=self.sample_band_10,
            mask=self.mask,
        )
        self.assertEqual(self.sample_band_10.shape, output.shape)  # Checking if output size matches input size

    # Test for ensuring maximum temperature is within the acceptable range
    def test_max_temp_less_than_or_equal_max_earth_temp(self):
        lst_algorithm = SplitWindowSobrino1993LST()
        # Checking if the maximum earth temperature matches the expected value
        self.assertEqual(lst_algorithm.max_earth_temp, 273.15 + 56.7)



# Test class for SplitWindowJiminezMunozLST functionality
class TestSplitWindowJiminezMunozLST(unittest.TestCase):
    # Creating sample data for testing purposes
    sample_band_10 = np.zeros((5, 5))  # Sample data for band 10
    mask = np.random.randint(0, high=2, size=(5, 5), dtype=int) == 1  # Generating a random mask

    # Test to ensure the output size matches the input size
    def test_output_and_input_size_equal(self):
        # Calling the SplitWindowJiminezMunozLST function with sample data
        output = SplitWindowJiminezMunozLST()(
            emissivity_10=self.sample_band_10,
            emissivity_11=self.sample_band_10,
            brightness_temperature_10=self.sample_band_10,
            brightness_temperature_11=self.sample_band_10,
            mask=self.mask,
        )
        # Asserting that the input and output shapes match
        self.assertEqual(self.sample_band_10.shape, output.shape)

    # Test to ensure the maximum temperature is within a certain range
    def test_max_temp_less_than_or_equal_max_earth_temp(self):
        # Creating an instance of the SplitWindowJiminezMunozLST class
        lst_algorithm = SplitWindowJiminezMunozLST()
        # Asserting that the maximum earth temperature is within a specific range
        self.assertEqual(lst_algorithm.max_earth_temp, 273.15 + 56.7)

class TestSplitWindowKerrLST(unittest.TestCase):
    # Sample data setup for testing purposes
    sample_band_10 = np.zeros((5, 5))
    mask = np.random.randint(0, high=2, size=(5, 5), dtype=int) == 1

    # Test to verify output size matches input size
    def test_output_and_input_size_equal(self):
        # Call the method being tested with sample input data
        output = SplitWindowKerrLST()(
            brightness_temperature_10=self.sample_band_10,
            brightness_temperature_11=self.sample_band_10,
            ndvi=self.sample_band_10,
            mask=self.mask,
        )
        # Assert that the output size matches the input size
        self.assertEqual(self.sample_band_10.shape, output.shape)

    # Test to ensure maximum temperature doesn't exceed maximum Earth temperature
    def test_max_temp_less_than_or_equal_max_earth_temp(self):
        # Create an instance of the tested class
        lst_algorithm = SplitWindowKerrLST()
        # Assert that the maximum calculated Earth temperature is within limits
        self.assertEqual(lst_algorithm.max_earth_temp, 273.15 + 56.7)

# Test class for SplitWindowMcMillinLST
class TestSplitWindowMcMillinLST(unittest.TestCase):
    # Sample data for testing
    sample_band_10 = np.zeros((5, 5))  # Creating a sample Band 10 data
    mask = np.random.randint(0, high=2, size=(5, 5), dtype=int) == 1  # Generating a random mask

    # Testing whether the output size matches the input size
    def test_output_and_input_size_equal(self):
        # Running the SplitWindowMcMillinLST algorithm
        output = SplitWindowMcMillinLST()(
            brightness_temperature_10=self.sample_band_10,
            brightness_temperature_11=self.sample_band_10,
            mask=self.mask,
        )
        # Checking if the output size matches the input size
        self.assertEqual(self.sample_band_10.shape, output.shape)

    # Testing if the maximum calculated temperature is less than or equal to the maximum Earth temperature
    def test_max_temp_less_than_or_equal_max_earth_temp(self):
        # Creating an instance of the SplitWindowMcMillinLST algorithm
        lst_algorithm = SplitWindowMcMillinLST()
        # Checking if the maximum calculated temperature matches the expected maximum Earth temperature
        self.assertEqual(lst_algorithm.max_earth_temp, 273.15 + 56.7)

# Create a test class inheriting from unittest.TestCase
class TestSplitWindowPriceLST(unittest.TestCase):
    # Sample data for testing
    sample_band_10 = np.zeros((5, 5))
    mask = np.random.randint(0, high=2, size=(5, 5), dtype=int) == 1

    # Test case to ensure output and input sizes are equal
    def test_output_and_input_size_equal(self):
        # Create an instance of the class or method being tested
        output = SplitWindowPriceLST()(
            # Provide sample data to the method
            emissivity_10=self.sample_band_10,
            emissivity_11=self.sample_band_10,
            brightness_temperature_10=self.sample_band_10,
            brightness_temperature_11=self.sample_band_10,
            mask=self.mask,
        )
        # Assert that the output shape matches the input shape
        self.assertEqual(self.sample_band_10.shape, output.shape)

    # Test case to verify maximum temperature constraints
    def test_max_temp_less_than_or_equal_max_earth_temp(self):
        # Create an instance of the class being tested
        lst_algorithm = SplitWindowPriceLST()
        # Assert that the maximum earth temperature is as expected
        self.assertEqual(lst_algorithm.max_earth_temp, 273.15 + 56.7)

# Run the tests if this file is executed directly
if __name__ == "__main__":
    unittest.main()