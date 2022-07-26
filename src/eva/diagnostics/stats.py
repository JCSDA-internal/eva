from eva.eva_path import return_eva_path
from eva.utilities.config import get
from eva.utilities.utils import get_schema, update_object, slice_var_from_str
import os
import numpy as np


class Stats():

    def __init__(self, config, logger, dataobj):

        # Get the data to compute stats for from the data_collection
        # ----------------------------------------------------------
        varstr = config['data']['variable']

        var_cgv = varstr.split('::')

        if len(var_cgv) != 3:
            logger.abort('In Stats the variable \'varstr\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel for statistics
        channel = None
        if 'channel' in config['data']:
            channel = config['data'].get('channel')

        data = dataobj.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

        # see if we need to slice data
        data = slice_var_from_str(config['data'], data, logger)

        # should flatten the data for statistics
        data = data.flatten()

        # need to remove NaN values
        mask = ~np.isnan(data)
        data = data[mask]
