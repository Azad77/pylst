# Import emissivity computation algorithms from the algorithms module
from .algorithms import (
    ComputeMonoWindowEmissivity,
    ComputeEmissivityNBEM,
    ComputeEmissivityGopinadh,
)

# Define a dictionary of default emissivity computation algorithms
# Each key corresponds to a method name, and the value is the corresponding algorithm class
default_algorithms = {
    "avdan": ComputeMonoWindowEmissivity,   # Avdan Ugur et al, 2016 method
    "xiaolei": ComputeEmissivityNBEM,       # Xiaolei Yu et al, 2014 method
    "gopinadh": ComputeEmissivityGopinadh,  # Gopinadh Rongali et al, 2018 method
}

# This dictionary allows users to easily choose a specific algorithm by providing the method name.
# For example, to use the Avdan Ugur et al, 2016 method, users can select "avdan" as the method.
# The corresponding algorithm class (ComputeMonoWindowEmissivity) will be used for computation.
# Users can extend this dictionary by adding more methods and their corresponding algorithm classes.
