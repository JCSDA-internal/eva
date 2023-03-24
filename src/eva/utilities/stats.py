# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import numpy as np

from eva.utilities.utils import slice_var_from_str


# --------------------------------------------------------------------------------------------------


def get_field_data(logger, field, data_collections):

    # Field name
    field_name = field['field_name']

    # Get collection, group, variable name for field
    var_cgv = field_name.split('::')
    if len(var_cgv) != 3:
        logger.abort('In stats_helper the variable \'var_cgv\' does not appear to ' +
                     'be in the required format of collection::group::variable.')

    # Optionally get the channel to plot
    channel = None
    if 'channel' in field:
        channel = field['channel']

    # Get the field data
    field_data = data_collections.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

    # See if we need to slice data
    field_data = slice_var_from_str(field, field_data, logger)

    # Flatten and mask missing data
    field_data = field_data.flatten()
    mask = ~np.isnan(field_data)
    field_data = field_data[mask]

    return field_data


# --------------------------------------------------------------------------------------------------


def stats_helper(logger, plot_obj, data_collections, config):
    """
    Add specified statistics to a plot
    Args:
        logger : logging object
        plotobj : declarative plotting object
        data_collections : eva data collections object
        config : input configuration dictionary
    """

    # List of data to make stats for
    fields = config['fields']

    # List of statistics to include
    stats_variables = config['statistics_variables']

    # Rounding
    digits = config.get('round', 3)

    # Find the max data length in order to format the string
    counts = []
    for field in fields:
        # Field name
        field_name = field['field_name']
        field_data = get_field_data(logger, field, data_collections)
        counts.append(len(field_data))
    n_len = str(len(str(np.max(counts))))

    # Format dictionary
    double_format = "{:.4E}"
    format_dict = {}
    format_dict['n'] = "{:" + n_len + "d}"
    format_dict['min'] = double_format
    format_dict['max'] = double_format
    format_dict['mean'] = double_format
    format_dict['median'] = double_format
    format_dict['std'] = double_format
    format_dict['var'] = double_format

    # Loop over fields and assemble statistics as a string
    for field in fields:

        # Field name
        field_name = field['field_name']

        # Get field data
        field_data = get_field_data(logger, field, data_collections)

        # Initialize the stats string
        stats_string = ''

        # Loop over statistics list and assemble string
        for index, stats_variable in enumerate(stats_variables):

            if stats_variable in ['n']:
                stat_value = len(field_data)
            elif stats_variable in ['min', 'max', 'mean', 'median', 'std', 'var']:
                stat_value = eval(f'np.nan{stats_variable}(field_data)')
                stat_value = eval(f'np.round(stat_value, {digits})')
            else:
                logger.abort(f'In stats_helper the statistic {stats_variable} is not supported.')

            stat_formatted = format_dict[stats_variable].format(stat_value)
            stats_string = stats_string + f'{stats_variable} = ' + stat_formatted

            if index < len(stats_variables) - 1:
                stats_string = stats_string + ' | '

        # Get the location for the annotation
        x_loc = field.get('xloc', 0.5)
        y_loc = field.get('yloc', -0.15)

        # Get any additional kwargs
        kwargs = field.get('kwargs', {})

        # call plot object method
        plot_obj.add_text(x_loc, y_loc, stats_string, transform='axcoords', ha='center', **kwargs)


# --------------------------------------------------------------------------------------------------
