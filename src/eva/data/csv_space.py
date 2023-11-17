from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get
from datetime import datetime
import xarray as xr
import numpy as np
import csv


class CsvSpace(EvaDatasetBase):

    """
    A class for handling CSV dataset configuration and processing.
    """

    def execute(self, dataset_config, data_collections, timing):

        """
        Executes the processing of CSV dataset.

        Args:
            dataset_config (dict): Configuration dictionary for the dataset.
            data_collections (DataCollections): Object for managing data collections.
            timing (Timing): Timing object for tracking execution time.
        """

        # Set the collection name
        # -----------------------
        collection_name = get(dataset_config, self.logger, 'name')

        # Filename to be read into this collection
        filenames = get(dataset_config, self.logger, 'filenames')

        # get 'groups'
        groups = get(dataset_config, self.logger, 'groups')

        # Set the collection name
        collection_name = dataset_config['name']

        ds_list = []

        # Read in the CSV files
        for file in filenames:

            f = open(file, "r")
            fd = list(csv.reader(f, delimiter=","))
            file_data = [[element.strip() for element in row] for row in fd]
            f.close()

            for group in groups:
                group_name = get(group, self.logger, 'name')
                group_vars = get(group, self.logger, 'variables', None, False)

                selected_fields = get(group, self.logger, 'selected_fields', 'all')
                date_config = get(group, self.logger, 'date', None, False)
                coord = None

                # load datetime if available
                if date_config is not None:
                    coord = 'Cycle'
                    var_name = group_name + "::datetime"
                    dt_arr = self.get_datetime_array(file_data, date_config)
                    ds = xr.Dataset({var_name: (coord, dt_arr),
                         coord: range(0, len(dt_arr))})
                    
                    ds_list.append(ds)

                # load requested data 
                if group_vars is not None:
                    for key, var in group_vars.items():
                        if coord is None: coord = 'Unit'
                        var_name = group_name + "::" + key
                        st_var_arr = [row[var] for row in file_data]
                        var_arr = np.array(st_var_arr, dtype=np.float32)

                        ds = xr.Dataset({var_name: (coord, var_arr),
                             coord: range(0, len(var_arr))})
                        ds_list.append(ds)

        # Concatenate datasets from ds_list into a single dataset
        ds = xr.merge(ds_list)

        # Assert that the collection contains at least one variable
        if not ds.keys():
            self.logger.abort('Collection \'' + dataset_config['name'] + '\', group \'' +
                              group + '\' in file ' + filename +
                              ' does not have any variables.')

        # add the dataset_config to the collections
        data_collections.create_or_add_to_collection(collection_name, ds)
        ds.close()

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()

    # ----------------------------------------------------------------------------------------------

    def generate_default_config(self, filenames, collection_name):

        """
        Generates a default configuration for CSV dataset.

        Args:
            filenames (list): List of file names.
            collection_name (str): Name of the data collection.

        Returns:
            dict: Default configuration dictionary.
        """

        eva_dict = {'channels': [],
                    'regions': [],
                    'levels': [],
                    'groups': [],
                    'name': collection_name}
        return eva_dict

    # ----------------------------------------------------------------------------------------------

    def get_datetime_array(self, file_data, date_config):

        """
        Load date components and return a datetime array.  Date/time information
        may be in a single field of file_data or in 4 fields (y,m,d,h).

        Args:
            file_data (list): List of data
            date_config (dict): date configuration information

        Returns:
            np.array: datetime array 
        """

        datetime_key = 'datetime'
        date_keys = {'year', 'month', 'day', 'hour'}

        if datetime_key in date_config:
            date_str_list = [row[date_config.get('datetime')] for row in file_data]

        elif all(k in (date_keys) for k in date_config):
            yr = [row[date_config.get('year')] for row in file_data]
            mon = [row[date_config.get('month')] for row in file_data]
            day = [row[date_config.get('day')] for row in file_data]
            hr = [row[date_config.get('hour')] for row in file_data]
            date_str_list = [y + m + d + h for y,m,d,h in zip(yr,mon,day,hr)]
            
        else:
            self.logger.abort("The date configuration in yaml file does not contain required date " +
                              "information. A \'date\': entry must specify either " +
                              "\'datetime\': (int) file field position or entries specifying " +
                              " \'year\': int, \'month\': int, \'day\': int, and \'hour\': int. " +  
                              f" Date information found was {date_config}") 

        return np.array([np.datetime64(datetime.strptime(ds, '%Y%m%d%H')) for ds in date_str_list])
