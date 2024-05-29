from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object
import os
import geopandas as gpd
import pandas as pd
import hvplot.pandas
import holoviews as hv

from eva.plotting.batch.base.diagnostics.map_scatter import MapScatter

# --------------------------------------------------------------------------------------------------


class HvplotMapScatter(MapScatter):
    """
    Subclass of MapScatter for generating scatter map plots using hvplot.

    Attributes:
        Inherits attributes from the MapScatter class.
    """
    def configure_plot(self):
        """
        Configures and generates a scatter map plot using hvplot.

        Returns:
            plotobj: plot object representing the generated scatter map plot.
        """
        df = pd.DataFrame()
        df['Latitude'] = self.latvar
        df['Longitude'] = self.lonvar
        label = self.config['label']
        cmap = self.config['cmap']
        marker_size = self.config['markersize']
        df[label] = self.datavar
        df = df.dropna()

        gdf = gpd.GeoDataFrame(
            df[label], geometry=gpd.points_from_xy(x=df.Longitude, y=df.Latitude)
        )

        self.plotobj = gdf.hvplot(global_extent=True, c=label, geo=True,
                                  cmap=cmap, legend=True, coastline=True,
                                  s=int(marker_size)+3, xlabel='Longitude',
                                  ylabel='Latitude', width=800, height=400)

        return self.plotobj

# --------------------------------------------------------------------------------------------------
