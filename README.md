<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue" alt="Python versions">
  <a href="https://pypi.org/project/pylst/"><img src="https://img.shields.io/pypi/v/pylst.svg?color=brightgreen" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pylst/"><img src="https://img.shields.io/pypi/pyversions/pylst.svg" alt="Python versions"></a>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <a href="https://github.com/Azad77/pylst/actions"><img src="https://img.shields.io/github/actions/workflow/status/Azad77/pylst/ci.yml?branch=main" alt="CI status"></a>
  <a href="https://zenodo.org/doi/10.5281/zenodo.18636233"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18636233.svg" alt="DOI"></a>
</p>

<h1 align="center">pylst</h1>

<p align="center">
  <strong>A Python package for processing and visualizing Landsat Land Surface Temperature (LST) data</strong>
  <br>
  <em>From raw Landsat thermal bands to ready-to-analyze LST maps — with minimal code.</em>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#citation">Citation</a> •
  <a href="#license">License</a>
</p>

## Features

- Retrieve and preprocess Landsat thermal infrared (TIR) data via Google Earth Engine (using `earthengine-api` & `geemap`)
- Compute Land Surface Temperature (LST) using standard single-channel / split-window algorithms
- Atmospheric correction support (basic emissivity & water vapor adjustments)
- Flexible visualization: single-date maps, time-series animations, zonal statistics
- Export results as GeoTIFF, NetCDF or interactive maps (folium / ipyleaflet)
- Built on trusted libraries: rasterio, numpy, pandas, matplotlib, opencv-python, scikit-learn

## Installation

The easiest way is via **pip** (recommended in a virtual environment):

```bash
pip install pylst