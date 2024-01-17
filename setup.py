from setuptools import setup, find_packages
import pathlib

# Define metadata
PACKAGE_NAME = "pylst"
VERSION = "0.0.2"
AUTHOR = "Azad Rasul"
AUTHOR_EMAIL = "azad.rasul@soran.edu.iq"
DESCRIPTION = "A Python package for processing and visualizing Landsat LST data."
URL = "https://github.com/pylst/lst"
LICENSE = "MIT"

# Set the current directory as the base path
here = pathlib.Path(__file__).parent.resolve()

# Read the contents of README.md for the long description
long_description = (here / "README.md").read_text(encoding="utf-8")

# Setup configuration
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    
    # Specify the type of long description (Markdown)
    long_description_content_type="text/markdown",
    long_description=long_description,
    
    # Project URL
    url=URL,
    
    # Find all packages in the project
    packages=find_packages(),
    
    # Dependencies required for the package
    install_requires=["numpy>=1.0",
                      "pandas>=1.4.4",
                      "rasterio>=1.0.0",
                      "GDAL>=2.0.0",
                      "geemap>=0.30.4",
                      "ee>=0.2",
                      "opencv-python>=4.7.0.72",
                      "scikit-learn>=1.0.2",
                      "matplotlib>=3.5.2",
                      
                      
                      ],
    
    # Keywords associated with the package
    keywords="Land Surface Temperature (LST), Image processing, Landsat, Remote Sensing, Thermal Satellite images",
    
    # Classification for the pacckage
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
    ],
    
    # Python version required
    python_requires=">=3.9",
)
