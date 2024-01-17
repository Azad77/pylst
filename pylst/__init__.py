# __init__.py

# Importing specific functionalities from different modules within the package

# Importing from the 'pylst' module
from .pylst import emissivity

# Importing visualization functions from the 'visualization' module
from .visualization import (
    plot_data,        # Function to plot data
    show,             # Function to show visualization
    rastshow,         # Function to show raster visualization
    create_interactive_map,  # Function to create interactive map
    histogram_equalization   # Function for histogram equalization
)

# Importing spatial analysis functions from the 'spatial_analysis' module
from .spatial_analysis.zonstat import calculate_zs  # Zonal statistics
from .spatial_analysis.changedet import analyze_images  # Change Detection

# Importing image handling classes and functions from the 'open' module
from .open import (
    Opener,        # Class for opening image data
    remopener,     # Class for opening remote image data
    download_images  # Function to download image collection images
)

# Importing normalization function from the 'normalization' module
from .normalization import nrs  # Normalization Ratio Scale function

# Importing machine learning functions from the 'ml' module
from .ml import (
    train_regression_model,      # Function to train regression model
    train_classification_model,  # Function to train classification model
    train_test_split,            # Function to split data for training and testing
    accuracy_score               # Function to compute accuracy score
)
