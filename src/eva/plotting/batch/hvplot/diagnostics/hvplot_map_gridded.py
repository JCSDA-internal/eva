from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import cartopy.crs as ccrs
import hvplot.xarray 
import numpy as np

from eva.plotting.batch.base.diagnostics.map_gridded import MapGridded

# --------------------------------------------------------------------------------------------------


class HvplotMapGridded(MapGridded):

    def configure_plot(self):

        cmap = self.config['cmap']
        x = eval(self.slice)
        data_slice = x[0]
        dataset = self.dataobj.get_data_collection(self.collection)
        var = self.datavar_name
        dataset = dataset.assign_coords({'lat_coord':(['lon', 'lat'], self.latvar)})
        dataset = dataset.assign_coords({'lon_coord':(['lon', 'lat'], self.lonvar)})
        ds = dataset.sel(lev=data_slice)
        self.plotobj = ds.hvplot.quadmesh('lon_coord', 'lat_coord', z = self.datavar_name,
                                          hover_cols=[self.datavar_name], cmap=cmap,
                                          geo=True, coastline=True) 

        return self.plotobj

# --------------------------------------------------------------------------------------------------
