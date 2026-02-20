# pylst/open/remopener.py
"""
Utilities for opening remote raster files (Cloud Optimized GeoTIFFs, HTTPS, S3, etc.)
using rasterio with virtual filesystem support (/vsicurl/, /vsis3/, etc.).

Main class:
- RemoteOpener: Context manager for remote rasters with windowed reading support
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

import rasterio
from rasterio.io import DatasetReader
from rasterio.windows import Window


class RemoteOpener:
    """
    Context manager for safely opening and reading remote raster files.

    Uses rasterio's virtual filesystem drivers (/vsicurl/, /vsis3/, etc.) to
    read only the needed parts of the file (especially useful for COGs).

    Example:
        with RemoteOpener("https://.../lst_cog.tif") as src:
            data = src.read(1)           # full band
            profile = src.profile
            meta = src.meta

        # Or windowed reading (memory efficient)
        with RemoteOpener(url) as src:
            window = Window(100, 100, 512, 512)
            chunk = src.read(1, window=window)
    """

    def __init__(
        self,
        url: str,
        env_options: Optional[dict] = None,
    ):
        """
        Args:
            url: Remote URL (https://..., s3://..., gs://..., etc.)
            env_options: Optional GDAL environment variables (e.g. AWS credentials)
        """
        self.url = str(url)
        self.env_options = env_options or {}
        self._src: Optional[DatasetReader] = None

    @contextmanager
    def open(self) -> Generator[DatasetReader, None, None]:
        """Context manager that yields an open rasterio dataset."""
        env = rasterio.Env(**self.env_options)

        with env:
            with rasterio.open(self.url) as src:
                self._src = src
                yield src

        self._src = None

    def read(
        self,
        indexes: int | list[int] | None = None,
        window: Optional[Window] = None,
        masked: bool = True,
    ) -> NDArray:
        """
        Read data from the remote raster (full or windowed).

        Args:
            indexes: Band(s) to read (int or list; default all)
            window: Optional rasterio.windows.Window for partial read
            masked: Return masked array (NaN for nodata)

        Returns:
            NumPy array (or masked array)
        """
        if self._src is None:
            raise RuntimeError("RemoteOpener must be used in a 'with' block")

        return self._src.read(indexes=indexes, window=window, masked=masked)

    @property
    def meta(self) -> dict:
        """Raster metadata (CRS, transform, etc.)"""
        if self._src is None:
            raise RuntimeError("RemoteOpener must be used in a 'with' block")
        return self._src.meta

    @property
    def profile(self) -> dict:
        """Raster profile (creation options)"""
        if self._src is None:
            raise RuntimeError("RemoteOpener must be used in a 'with' block")
        return self._src.profile


@contextmanager
def open_remote_raster(
    url: str,
    env_options: Optional[dict] = None,
) -> Generator[DatasetReader, None, None]:
    """
    Simple context manager shortcut for opening remote rasters.

    Example:
        with open_remote_raster("https://.../lst.tif") as src:
            lst_data = src.read(1)
    """
    opener = RemoteOpener(url, env_options)
    with opener.open() as src:
        yield src