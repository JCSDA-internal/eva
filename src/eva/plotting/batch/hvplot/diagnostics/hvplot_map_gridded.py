import hvplot.xarray
from eva.plotting.batch.base.diagnostics.map_gridded import MapGridded

# --------------------------------------------------------------------------------------------------


class HvplotMapGridded(MapGridded):
    """
    Subclass of MapGridded for generating gridded map plots using hvplot.

    Attributes:
        Inherits attributes from the MapGridded class.
    """
    def configure_plot(self):
        """
        Configures and generates a gridded map plot using hvplot.

        Returns:
            plotobj: plot object representing the generated map plot.
        """
        cmap = self.config['cmap']
        x = eval(self.config['data']['slices'])
        data_slice = x[0]
        dataset = self.dataobj.get_data_collection(self.collection)
        var = self.datavar_name
        dataset = dataset.assign_coords({'lat_coord': (['lon', 'lat'], self.latvar)})
        dataset = dataset.assign_coords({'lon_coord': (['lon', 'lat'], self.lonvar)})
        ds = dataset.sel(lev=data_slice)
        self.plotobj = ds.hvplot.quadmesh('lon_coord', 'lat_coord', z=self.datavar_name,
                                          hover_cols=[self.datavar_name], cmap=cmap,
                                          geo=True, coastline=True, xlabel='Longitude',
                                          ylabel='Latitude', width=800, height=400)
        return self.plotobj

# --------------------------------------------------------------------------------------------------
