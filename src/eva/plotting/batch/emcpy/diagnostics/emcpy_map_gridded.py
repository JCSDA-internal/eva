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
        Normalize inputs for EMCPy MapGridded by ensuring:
          - lat/lon are 2-D center grids,
          - data is 2-D (matching lat/lon).
        If lat/lon are already 2-D (curvilinear), just squeeze data to 2-D.
        """
        lat = np.asarray(latvar)
        lon = np.asarray(lonvar)
        A   = np.asarray(datavar)

        # If lat/lon are already 2-D curvilinear, just pick/squeeze one level if needed.
        if lat.ndim == 2 and lon.ndim == 2:
            if A.ndim == 3:
                # default to level 0 unless overridden in config
                lev_idx = int(self.config.get("level_index", 0))
                # choose first axis as level by default
                A = np.squeeze(A[lev_idx, ...])
            else:
                A = np.squeeze(A)
            return lat, lon, A

        # 1-D center coordinates path
        lat1d = lat.squeeze()
        lon1d = lon.squeeze()
        if lat1d.ndim != 1 or lon1d.ndim != 1:
            raise ValueError(
                f"Expected 1-D or 2-D lat/lon; got lat {lat.shape}, lon {lon.shape}"
            )

        # Reduce data to 2-D (Nlat, Nlon)
        if A.ndim == 3:
            # Try to identify lat/lon axes by matching sizes
            shape = A.shape
            lat_axis = next((i for i, s in enumerate(shape) if s == lat1d.size), None)
            lon_axis = next((i for i, s in enumerate(shape) if s == lon1d.size), None)
            if lat_axis is not None and lon_axis is not None:
                order = [lat_axis, lon_axis] + [i for i in range(3) if i not in (lat_axis, lon_axis)]
                A = np.transpose(A, order)
                lev_idx = int(self.config.get("level_index", 0))
                if A.ndim == 3:
                    A = A[:, :, lev_idx]
            else:
                # Fallback: assume first dim is level
                lev_idx = int(self.config.get("level_index", 0))
                A = A[lev_idx, ...]
        A = np.squeeze(A)

        # Ensure orientation (Nlat, Nlon)
        if A.shape != (lat1d.size, lon1d.size):
            if A.T.shape == (lat1d.size, lon1d.size):
                A = A.T
            else:
                raise ValueError(
                    f"Data shape {A.shape} incompatible with lat {lat1d.size} / lon {lon1d.size}"
                )

        # Make 2-D center grids
        LAT2D, LON2D = np.meshgrid(lat1d, lon1d, indexing="ij")
        return LAT2D, LON2D, A

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
