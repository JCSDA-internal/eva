from eva.eva_base import EvaBase
from eva.utilities.config import get
import xarray as xr


valid_groups = ['state', 'increment']


class LatLon(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, data_collections):

        # Loop over the datasets
        # ----------------------
        for dataset in self.config.get('datasets'):

            # Filename to be read into this collection
            filename = get(dataset, self.logger, 'filename')
            # get list of variables
            variables = get(dataset, self.logger, 'variables')
            # Set the collection name
            collection_name = dataset['name']
            # get 'group' name
            group = get(dataset, self.logger, 'group')

            if group not in valid_groups:
                self.logger.abort('For collection \'' + dataset['name'] + '\'' +
                                  f' group \'{group}\' is not a valid group type for LatLon.' +
                                  f' The valid types are {valid_groups}')

            # open the input netCDF file
            ds = xr.open_dataset(filename)

            # Drop data variables not in user requested variables
            vars_to_remove = list(set(list(ds.keys())) - set(variables))
            ds = ds.drop_vars(vars_to_remove)

            # for lat and lon, need to do a meshgrid so that each point has a lat and a lon

            # rename variables in dataset
            rename_dict = {}
            for v in variables:
                rename_dict[v] = f'{group}::{v}'
            ds = ds.rename(rename_dict)

            # Assert that the collection contains at least one variable
            if not ds.keys():
                self.logger.abort('Collection \'' + dataset['name'] + '\', group \'' +
                                  group + '\' in file ' + filename +
                                  ' does not have any variables.')

            # add the dataset to the collections
            data_collections.create_or_add_to_collection(collection_name, ds)

            ds.close()

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()
