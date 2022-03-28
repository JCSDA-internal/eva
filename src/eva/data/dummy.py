from eva.eva_base import EvaBase
import xarray as xr


class Dummy(EvaBase):

    def execute(self, data_collections):

        x_dataArr = xr.DataArray([1, 2, 3, 4, 5])
        y_dataArr = xr.DataArray([1, 2, 3, 4, 5])

        xy_dataSet = xr.Dataset()
        xy_dataSet['x'] = x_dataArr
        xy_dataSet['y'] = y_dataArr

        data_collections.create_or_add_to_collection('dummy', xy_dataSet)
