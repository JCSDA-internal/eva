from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get
import xarray as xr


valid_groups = ['state', 'increment']


class LatLon(EvaDatasetBase):

    """
    A class for handling LatLon dataset configuration and processing.
    """

    def execute(self, dataset_config, data_collections, timing):

        """
        Executes the processing of LatLon dataset.

        Args:
            dataset_config (dict): Configuration dictionary for the dataset.
            data_collections (DataCollections): Object for managing data collections.
            timing (Timing): Timing object for tracking execution time.
        """

        # Filename to be read into this collection
        filename = get(dataset_config, self.logger, 'filename')
        # get list of variables
        variables = get(dataset_config, self.logger, 'variables')
        # Set the collection name
        collection_name = dataset_config['name']
        # get 'group' name
        group = get(dataset_config, self.logger, 'group')

        if group not in valid_groups:
            self.logger.abort('For collection \'' + dataset_config['name'] + '\'' +
                              f' group \'{group}\' is not a valid group type for LatLon.' +
                              f' The valid types are {valid_groups}')

        # open the input netCDF file
        ds = xr.open_dataset(filename)

        # Drop data variables not in user requested variables
        vars_to_remove = list(set(list(ds.keys())) - set(variables))
        ds = ds.drop_vars(vars_to_remove)

        # rename variables in dataset_config
        rename_dict = {}
        for v in variables:
            rename_dict[v] = f'{group}::{v}'
        ds = ds.rename(rename_dict)

        # Assert that the collection contains at least one variable
        if not ds.keys():
            self.logger.abort('Collection \'' + dataset_config['name'] + '\', group \'' +
                              group + '\' in file ' + filename +
                              ' does not have any variables.')

        # add the dataset_config to the collections
        data_collections.create_or_add_to_collection(collection_name, ds)

        ds.close()

    # ----------------------------------------------------------------------------------------------

    def generate_default_config(self, filenames, collection_name):

        """
        Generates a default configuration for LatLon dataset.

        Args:
            filenames (list): List of file names.
            collection_name (str): Name of the data collection.

        Returns:
            dict: Default configuration dictionary.
        """

        # Needs to be implemented

        pass

    # ----------------------------------------------------------------------------------------------
