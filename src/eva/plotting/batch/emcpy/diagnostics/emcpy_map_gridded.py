from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import emcpy.plots.map_plots
import os
import numpy as np

from eva.plotting.batch.base.diagnostics.map_gridded import MapGridded

# --------------------------------------------------------------------------------------------------


class EmcpyMapGridded(MapGridded):
    """
    EMCPy backend for gridded maps.
    Option A: if latitude/longitude are 1-D centers, convert them to 2-D center grids
    with np.meshgrid and reduce data to a single 2-D level before plotting.
    """

    def _to_2d_centers(self, latvar, lonvar, datavar):
        """
        Normalize inputs for EMCPy MapGridded by ensuring 2-D lat/lon and 2-D data.
        Handles:
          - 3-D curvilinear lat/lon with a 'tile' dim: selects one tile (tile_index, default 0)
          - 2-D curvilinear lat/lon: pass-through, squeeze data to 2-D
          - 1-D centers: meshgrid to 2-D and orient data to (Nlat, Nlon)
        """
        lat = np.asarray(latvar)
        lon = np.asarray(lonvar)
        A = np.asarray(datavar)

        # --- CASE 1: 3-D curvilinear (lon, lat, tile) → choose one tile to get 2-D ---
        if lat.ndim == 3 and lon.ndim == 3 and lat.shape == lon.shape:
            tile_count = lat.shape[2]
            tile_idx = int(self.config.get("tile_index", 0))
            if not (0 <= tile_idx < tile_count):
                raise ValueError(f"tile_index {tile_idx} out of range [0,{tile_count-1}]")

            # slice lat/lon to 2-D for this tile
            lat2d = lat[:, :, tile_idx]
            lon2d = lon[:, :, tile_idx]

            # slice data on its tile axis (if present)
            A2 = A
            if A2.ndim >= 3:
                # find axis whose size == tile_count
                tile_axis = next((i for i, s in enumerate(A2.shape) if s == tile_count), None)
                if tile_axis is not None:
                    A2 = np.take(A2, tile_idx, axis=tile_axis)

            # if any extra leading level/ensemble dim remains, pick first or configured
            if A2.ndim == 3:
                lev_idx = int(self.config.get("level_index", 0))
                # choose an axis that is not lat or lon sized
                lat_size, lon_size = lat2d.shape
                # bring to (lat, lon, extra) or (lon, lat, extra)
                if A2.shape[:2] == (lat_size, lon_size):
                    A2 = A2[:, :, lev_idx]
                elif A2.shape[:2] == (lon_size, lat_size):
                    A2 = A2[:, :, lev_idx].T
                else:
                    # try matching by transpose
                    if A2.transpose(1, 0, 2).shape[:2] == (lat_size, lon_size):
                        A2 = A2.transpose(1, 0, 2)[:, :, lev_idx]
                    else:
                        # last resort: squeeze to 2-D
                        A2 = np.squeeze(A2)

            A2 = np.squeeze(A2)
            # Ensure shapes match lat2d/lon2d
            if A2.shape != lat2d.shape:
                if A2.T.shape == lat2d.shape:
                    A2 = A2.T
                else:
                    raise ValueError(f"Data shape {A2.shape} incompatible "
                                     f"with tile lat/lon {lat2d.shape}")

            return lat2d, lon2d, A2

        # --- CASE 2: 2-D curvilinear lat/lon: pass-through, squeeze data to 2-D ---
        if lat.ndim == 2 and lon.ndim == 2:
            A2 = A
            if A2.ndim == 3:
                lev_idx = int(self.config.get("level_index", 0))
                # assume first axis is level/extra
                A2 = A2[lev_idx, ...]
            return lat, lon, np.squeeze(A2)

        # --- CASE 3: 1-D centers → build 2-D centers via meshgrid ---
        if lat.ndim == 1 and lon.ndim == 1:
            lat1d = lat.squeeze()
            lon1d = lon.squeeze()
            A2 = A
            if A2.ndim == 3:
                # identify lat/lon axes by matching sizes and pick level_index
                shape = A2.shape
                lat_axis = next((i for i, s in enumerate(shape) if s == lat1d.size), None)
                lon_axis = next((i for i, s in enumerate(shape) if s == lon1d.size), None)
                if lat_axis is not None and lon_axis is not None:
                    axes = (lat_axis, lon_axis)
                    extra = [
                        i for i in range(A2.ndim)
                        if i not in axes
                    ]
                    order = [*axes, *extra]
                    A2 = np.transpose(A2, order)
                    lev_idx = int(self.config.get("level_index", 0))
                    if A2.ndim == 3:
                        A2 = A2[:, :, lev_idx]
                else:
                    lev_idx = int(self.config.get("level_index", 0))
                    A2 = A2[lev_idx, ...]
            A2 = np.squeeze(A2)

            # orient to (Nlat, Nlon)
            if A2.shape != (lat1d.size, lon1d.size):
                if A2.T.shape == (lat1d.size, lon1d.size):
                    A2 = A2.T
                else:
                    raise ValueError(
                        f"Data shape {A2.shape} incompatible with "
                        f"lat {lat1d.size} / lon {lon1d.size}"
                    )

            LAT2D, LON2D = np.meshgrid(lat1d, lon1d, indexing="ij")
            return LAT2D, LON2D, A2

        # Otherwise unsupported
        raise ValueError(f"Expected 1-D or 2-D lat/lon; got lat {lat.shape}, lon {lon.shape}")

    def configure_plot(self):
        """
        Configures the plotting settings for the gridded map.
        Returns:
            plotobj: The configured plot object for EMCPy gridded maps.
        """
        # Convert to 2-D centers + 2-D data if needed
        lat2d, lon2d, data2d = self._to_2d_centers(self.latvar, self.lonvar, self.datavar)

        # Create EMCPy MapGridded object
        self.plotobj = emcpy.plots.map_plots.MapGridded(lat2d, lon2d, data2d)

        # Apply schema defaults/overrides
        layer_schema = self.config.get(
            "schema",
            os.path.join(
                return_eva_path(), "plotting", "batch", "emcpy", "defaults", "map_gridded.yaml"
            ),
        )
        new_config = get_schema(layer_schema, self.config, self.logger)
        for d in ["longitude", "latitude", "data", "type", "schema", "level_index"]:
            new_config.pop(d, None)
        self.plotobj = update_object(self.plotobj, new_config, self.logger)
        return self.plotobj

# --------------------------------------------------------------------------------------------------
