# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import math
import numpy as np
from scipy.stats import skew

from eva.utilities.utils import replace_vars_dict


# --------------------------------------------------------------------------------------------------


def vminvmaxcmap(logger, option_dict, plots_dict, data_collections):

    # Get percentage of data to use in computing limits. Code will sort the data
    # by size and then trim the minimum and maximum until this percentage of data
    # is kept
    percentage_capture = option_dict.get('percentage capture', 100)

    # Optionally the data might have a channel.
    channel = option_dict.get('channel', None)

    # Get the data variable to use for determining cbar limits
    varname = option_dict.get('data variable')
    varname_cgv = varname.split('::')
    datavar = data_collections.get_variable_data(varname_cgv[0], varname_cgv[1],
                                                 varname_cgv[2], channel)

    # Reorder the data array
    datavar = np.sort(datavar)

    # Decide how many values to throw out on each end of the dataset
    n = datavar.size
    n_throw_out = ((100-percentage_capture) * n / 100) / 2

    # The value needs to be an integer
    n_throw_out = np.floor(n_throw_out)

    # Create new array with only the data to consider
    if n_throw_out == 0:
        datavar_check = datavar
    else:
        datavar_check = datavar[n_throw_out:-n_throw_out]

    # Find minimum and maximum values
    cmap = option_dict.get('sequential colormap', 'viridis')

    # If everything is nan plot some large min/max (plotting code should do the same)
    if np.isnan(datavar_check).all():
        vmax = 1.0e38
        vmin = 1.0e38
    else:
        vmax = np.nanmax(datavar_check)
        vmin = np.nanmin(datavar_check)

    # If positive and negative values are present then a diverging colormap centered on zero should
    # be used.
    if vmin < 0.0 and vmax > 0.0:
        vmax = np.nanmax(np.abs(datavar_check))
        vmin = -vmax
        cmap = option_dict.get('diverging colormap', 'seismic')

    # Check for nan
    if np.isnan(vmax) or np.isnan(vmin):
        vmax = 0.0
        vmin = 0.0
        cmap = option_dict.get('diverging colormap', 'seismic')

    # Prepare dictionary with values to be overwritten in other dictionaries
    overwrite_dict = {}
    overwrite_dict['dynamic_vmax'] = str(vmax)
    overwrite_dict['dynamic_vmin'] = str(vmin)
    overwrite_dict['dynamic_cmap'] = cmap

    # Perform the overwrite of the plots_dict dictionary and return new dictionary
    return replace_vars_dict(plots_dict, **overwrite_dict)


# --------------------------------------------------------------------------------------------------


def histogram_bins(logger, option_dict, plots_dict, data_collections):

    # Optionally the data might have a channel.
    channel = option_dict.get('channel', None)

    # Get the data variable to use for determining cbar limits
    varname = option_dict.get('data variable')
    varname_cgv = varname.split('::')
    datavar = data_collections.get_variable_data(varname_cgv[0], varname_cgv[1],
                                                 varname_cgv[2], channel)

    # Compute size of the array of data
    n = np.count_nonzero(~np.isnan(datavar))

    # Check for zero data, set to 3 as a reasonable minimum
    if n == 0:
        n = 3

    # Compute number of bins using standard rule
    rule = option_dict.get('number of bins rule', 'sturges')
    rule = rule.lower()  # User might capitalize names so convert to lowercase

    # Allow for some standard rules for computing the number of bins for the histogram
    if rule == 'square root':
        nbins = math.sqrt(n)
    elif rule == 'sturges':
        nbins = 1 + math.log2(n)
    elif rule == 'rice':
        nbins = 2 * math.pow(n, 1/3)
    elif rule == 'doane':
        if n < 3:
            logger.abort(f'Rule \'doane\' is not valid for data with fewer than 3 samples.')
        g1 = skew(datavar, nan_policy='omit')
        sig_g1 = math.sqrt(6*(n-2)/((n+1)*(n+3)))
        nbins = 1 + math.log2(n) + math.log2(1 + abs(g1)/sig_g1)
    else:
        logger.abort(f'Rule {rule} for computing the histogram bins is not valid.')

    # Prepare dictionary with values to be overwritten in other dictionaries
    overwrite_dict = {}
    overwrite_dict['dynamic_bins'] = str(round(nbins))

    # Perform the overwrite of the plots_dict dictionary and return new dictionary
    return replace_vars_dict(plots_dict, **overwrite_dict)


# --------------------------------------------------------------------------------------------------
