# pylst/visualization/plotter.py
"""
Plotting utilities for raster data.
Author: Azad Rasul
"""

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - may fail due to numpy version conflict
    plt = None

import rasterio
import os


def rastshow(
    path,
    title=None,
    colorbar_label="Value",
    cmap="viridis",
    figsize=(8, 6),
    vmin=None,
    vmax=None,
    xlabel="Longitude",
    ylabel="Latitude",
    **imshow_kwargs
):
    """
    Display a single-band GeoTIFF raster using matplotlib.

    Parameters
    ----------
    path : str
        Path to the .tif file
    title : str, optional
    colorbar_label : str, optional
    cmap : str, optional
    figsize : tuple, optional
    vmin, vmax : float, optional
    xlabel, ylabel : str, optional
    **imshow_kwargs : dict
        Additional kwargs passed to ax.imshow()

    Returns
    -------
    None  (displays the plot)
    """
    if plt is None:
        raise ImportError(
            "matplotlib is required for rastshow(). "
            "Install with: pip install matplotlib"
        )
    
    with rasterio.open(path) as src:
        data = src.read(1)  # first band
        extent = [src.bounds.left, src.bounds.right,
                  src.bounds.bottom, src.bounds.top]

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(
        data,
        cmap=cmap,
        extent=extent,
        origin="upper",           # rasterio usually top-left origin
        vmin=vmin,
        vmax=vmax,
        **imshow_kwargs
    )

    ax.set_title(title or os.path.basename(path))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    plt.colorbar(im, ax=ax, label=colorbar_label)
    plt.tight_layout()

    plt.show()   # comment out if you want to return fig instead
    # return fig     ← alternative: return figure for testing / saving