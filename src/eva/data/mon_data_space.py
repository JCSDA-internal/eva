# (C) Copyright 2021-2023 NOAA/NWS/EMC
#
# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import numpy as np

from xarray import Dataset, concat
from scipy.io import FortranFile
from datetime import datetime

from eva.eva_base import EvaBase
from eva.utilities.config import get
from eva.utilities.utils import parse_channel_list, is_number

# --------------------------------------------------------------------------------------------------


class MonDataSpace(EvaBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, data_collections, timing):

        # Loop over the datasets
        # ----------------------
        for dataset in self.config.get('datasets'):

            # Set the collection name
            # -----------------------
            collection_name = get(dataset, self.logger, 'name')

            # Get control file and parse
            # --------------------------
            control_file = get(dataset, self.logger, 'control_file')
            coords, dims, attribs, nvars, vars, channo = self.get_ctl_dict(control_file[0])
            self.logger.info('coords: ' + str(coords))
            self.logger.info('dims: ' + str(dims))
            self.logger.info('attribs: ' + str(attribs))
            self.logger.info('nvars: ' + str(nvars))
            self.logger.info('vars: ' + str(vars))
            self.logger.info('channo: ' + str(channo))

            ndims_used = self.get_ndims_used(dims)

            # Get the groups to be read
            # -------------------------
            groups = get(dataset, self.logger, 'groups')

            # Get requested channels, convert to list
            # ---------------------------------------
            channels_str_or_list = get(dataset, self.logger, 'channels')
            drop_channels = False
            requested_channels = []

            if channels_str_or_list is not None:

                if len(str(channels_str_or_list)) > 0:
                    requested_channels = parse_channel_list(str(channels_str_or_list), self.logger)
                    drop_channels = True

            # Get requested regions, convert to list
            # --------------------------------------
            regions_str_or_list = get(dataset, self.logger, 'regions')
            requested_regions = []
            drop_regions = False

            if regions_str_or_list is not None:

                if len(str(regions_str_or_list)) > 0:
                    requested_regions = parse_channel_list(str(regions_str_or_list), self.logger)
                    drop_regions = True
            self.logger.info('drop_regions = ' + str(drop_regions))
            self.logger.info('regions_str_or_list = ' + str(regions_str_or_list))

            # Need to add levels to the potential drop list
            # ---------------------------------------------

            # Set coordinate ranges
            # ---------------------
            x_range, y_range, z_range = self.get_dim_ranges(coords, dims, channo)

            # Filenames to be read into this collection
            # -----------------------------------------
            filenames = get(dataset, self.logger, 'filenames')
            ds_list = []

            # Get missing value threshold
            # ---------------------------
            threshold = float(get(dataset, self.logger, 'missing_value_threshold', 1.0e30))
            self.logger.info('threshold = ' + str(threshold))

            for filename in filenames:

                # read data file
                darr, cycle_tm = self.read_ieee(filename, coords, dims, ndims_used, nvars, vars)

                # add cycle as a variable in data array
                cyc_darr = self.cycle_to_np_array(dims, ndims_used, cycle_tm)

                # conditionally add 'scan' as a variable
                if 'Scan' in coords:
                    self.logger.info('Need to add scan')

                # create dataset from file contents
                timestep_ds = None

                timestep_ds = self.load_dset(vars, nvars, coords, darr, dims, ndims_used,
                                             x_range, y_range, z_range, cyc_darr)

                if attribs['sat']:
                    timestep_ds.attrs['satellite'] = attribs['sat']
                if attribs['sensor']:
                    timestep_ds.attrs['sensor'] = attribs['sensor']

                # add cycle_tm dim for concat
                timestep_ds['times'] = cycle_tm

                # Add this dataset to the list of ds_list
                ds_list.append(timestep_ds)

            # Concatenate datasets from ds_list into a single dataset
            ds = concat(ds_list, dim='Time')

            # Group name and variables
            # ------------------------
            for group in groups:
                group_name = get(group, self.logger, 'name')
                group_vars = get(group, self.logger, 'variables', 'all')

                # Drop channels not in user requested list
                # ----------------------------------------
                if drop_channels:
                    ds = self.subset_coordinate(ds, 'Channel', requested_channels)

                # Drop regions not in user requested list
                # ---------------------------------------
                if drop_regions:
                    ds = self.subset_coordinate(ds, 'Region', requested_regions)

                # If user specifies all variables set to group list
                # -------------------------------------------------
                if group_vars == 'all':
                    group_vars = list(ds.data_vars)

                # Drop data variables not in user requested variables
                # ---------------------------------------------------
                vars_to_remove = list(set(list(ds.keys())) - set(group_vars))
                ds = ds.drop_vars(vars_to_remove)

                # Conditionally add channel as a variable using single dimension
                if 'channel' in group_vars:

                    # find channel dimension
                    chan_dim = list(coords.keys()) [list(coords.values()).index('Channel')]
                    if len(channo) == dims[chan_dim]:
                        ds['channel'] = (['Channel'], channo)
                    else:
                        self.logger.abort(f"number of channels in yaml file does not match number of channels in control file") 

                # Rename variables with group
                rename_dict = {}
                for group_var in group_vars:
                    rename_dict[group_var] = group_name + '::' + group_var

                ds = ds.rename(rename_dict)

                # Assert that the collection contains at least one variable
                if not ds.keys():
                    self.logger.abort('Collection \'' + dataset['name'] + '\', group \'' +
                                      group_name + '\' in file ' + filename +
                                      ' does not have any variables.')

            # Add the dataset to the collections
            data_collections.create_or_add_to_collection(collection_name, ds, 'times')

        # Nan out unphysical values
        data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()

    # ----------------------------------------------------------------------------------------------

    def subset_coordinate(self, ds, coordinate, requested_subset):

        if coordinate in list(ds.dims):

            # Number of entries in requested_subset
            num_coord_to_use = len(requested_subset)

            # Number of specified coordinate in the ds
            num_specified_coordinate_in_ds = len(ds.coords[coordinate])

            if all(x in ds[coordinate] for x in requested_subset):
                ds = ds.sel(**{coordinate: requested_subset})

            else:
                bad_coordinates = [x for x in requested_subset if x not in ds[coordinate]]

                self.logger.abort(f"{', '.join(str(i) for i in bad_coordinates)} was inputted" +
                                  " as a selected value of the coordinate " + str(coordinate) +
                                  ", but that is not a valid value. \n" +
                                  "Valid values for " + str(coordinate) + " are: \n" +
                                  f"{', '.join(str(i) for i in ds[coordinate].data)}")
        else:
            self.logger.abort('requested coordinate, ' + str(coordinate) + ' is not in ' +
                              ' dataset dimensions valid dimensions include ' + str(ds.dims))

        return ds

    # ----------------------------------------------------------------------------------------------

    def get_ctl_dict(self, control_file):

        coords = {'xdef': None, 'ydef': None, 'zdef': None}
        dims = {'xdef': 0, 'ydef': 0, 'zdef': 0}
        attribs = {'sensor': None, 'sat': None}
        vars = []
        nvars = 0
        channo = []
        scan_info = []

        with open(control_file, 'r') as fp:
            lines = fp.readlines()

            for line in lines:
                if line.find('XDEF') != -1:
                    if line.find('channel') != -1:
                        coords['xdef'] = 'Channel'
                    elif line.find("scan") != -1:
                        coords['xdef'] = 'Scan'

                if line.find('YDEF') != -1:
                    if line.find('region') != -1:
                        coords['ydef'] = 'Region'
                    elif line.find('channel') != -1:
                        coords['ydef'] = 'Channel'

                if line.find('ZDEF') != -1:
                    if line.find('region') != -1:
                        coords['zdef'] = 'Region'

                if line.find('xdef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            dims['xdef'] = int(st)
                      

                if line.find('ydef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            dims['ydef'] = int(st)

                if line.find('zdef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            dims['zdef'] = int(st)

                if line.find('vars') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            nvars = int(st)

                if line.find('title') != -1:
                    if line.find('conventional') == -1 and line.find('gsistat') == -1:
                        strs = line.split()
                        attribs['sensor'] = strs[1]
                        attribs['sat'] = strs[2]

                # Note we need to extract the actual channel numbers.  We have the
                # number of channels via the xdef line, but they are not necessarily
                # ordered consecutively.
                if line.find('channel=') != -1:
                    strs = line.split()
                    if strs[4].isdigit():
                        channo.append(int(strs[4]))

            # The list of variables is at the end of the file between the lines
            # "vars" and "end vars".
            start = len(lines) - (nvars + 1)
            for x in range(start, start + nvars):
                strs = lines[x].split()
                vars.append(strs[-1])

            self.logger.info('scan_info = ' + str(scan_info))
            self.logger.info('coords: ' + str(coords))
 
        return coords, dims, attribs, nvars, vars, channo

    # ----------------------------------------------------------------------------------------------

    def read_ieee(self, file_name, coords, dims, ndims_used, nvars, vars, file_path=None):

        # find cycle time in filename and create cycle_tm as datetime object
        cycle_tm = None
        cycstrs = file_name.split('.')

        for cycstr in cycstrs:
            if cycstr.isnumeric():
                cycle_tm = datetime(int(cycstr[0:4]), int(cycstr[4:6]),
                                    int(cycstr[6:8]), int(cycstr[8:]))

        filename = os.path.join(file_path, file_name) if file_path else file_name

        if not os.path.isfile(filename):
            rtn_array = None
            return rtn_array

        # read binary Fortran file
        f = FortranFile(filename, 'r', '>u4')

        if ndims_used == 1:
            rtn_array = np.empty((0, dims['xdef']), float)
            for x in range(nvars):
                arr = f.read_reals(dtype=np.dtype('>f4')).reshape(dims['xdef'])
                arr = np.array(arr, dtype=np.float)
                rtn_array = np.append(rtn_array, [arr], axis=0)

        if ndims_used == 2:
            rtn_array = np.empty((0, dims['xdef'], dims['ydef']), float)
            for x in range(nvars):
                arr = f.read_reals(dtype=np.dtype('>f4')).reshape(dims['xdef'],
                                                                  dims['ydef'])
                arr = np.array(arr, dtype=np.float)
                rtn_array = np.append(rtn_array, [arr], axis=0)

        if ndims_used == 3:
            rtn_array = np.empty((0, dims['xdef'], dims['ydef'], dims['zdef']), float)

            for x in range(nvars):

                self.logger.info('vars[x] = ' + str(vars[x]))

                # satang variable is deprecated, not used, and a non-standard size
                if vars[x] == 'satang':	
                    skip = f.read_reals(dtype=np.dtype('>f4')).reshape(dims['xdef'],
                                                                       dims['ydef'])
                    tarr = np.zeros((dims['xdef'], dims['ydef'], dims['zdef']), 
                                     dtype=np.dtype('>f4'))
                else:
                    mylist = []
                    for z in range(5):
                        arr = f.read_reals(dtype=np.dtype('>f4')).reshape(dims['xdef'],
                                                                          dims['ydef'])
                        mylist.append(arr)
                    tarr = np.dstack(mylist)

                rtn_array = np.append(rtn_array, [tarr], axis=0)

        f.close()
        return rtn_array, cycle_tm

    # ----------------------------------------------------------------------------------------------

    def cycle_to_np_array(self, dims, ndims_used, cycle_tm):

        # build array with requested dimensions
        cycle_arr = None

        if ndims_used == 3:
            cycle_arr = np.reshape([[cycle_tm] * dims['xdef'] * dims['ydef'] * dims['zdef']],
                                   (dims['xdef'], dims['ydef'], dims['zdef']))
        elif ndims_used == 2:
            cycle_arr = np.reshape([[cycle_tm] * dims['xdef']] * dims['ydef'],
                                   (dims['xdef'], dims['ydef']))
        elif ndims_used == 1:
            cycle_arr = np.reshape([[cycle_tm] * dims['xdef']], (dims['xdef']))
        else:
            self.logger.abort(f'ndims_used must be in range of 1-3, value is {ndims_used}')
        return cycle_arr

    # ----------------------------------------------------------------------------------------------

    def get_dim_ranges(self, coords, dims, channo):
        x_range = None
        y_range = None
        z_range = None

        # - Return None for a coordinate that is 0 or 1.
        # - "Channel" can be either the x or y coordinate and can be
        #      numbered non-consecutively, which has been captured in channo.
        # - The z coordinate is never used for channel.
    def get_dim_ranges(self, coords, dims, channo):
        x_range = None
        y_range = None
        z_range = None

        # - Return None for a coordinate that is 0 or 1.
        # - "Channel" can be either the x or y coordinate and can be
        #      numbered non-consecutively, which has been captured in channo.
        # - The z coordinate is never used for channel.

        if dims['xdef'] > 1:

            if coords['xdef'] == 'Channel':
                x_range = channo
            else:
                x_range = np.arange(1, dims['xdef']+1)

        if dims['ydef'] > 1:
            if coords['ydef'] == 'Channel':
                y_range = channo
            else:
                y_range = np.arange(1, dims['ydef']+1)

        if dims['zdef'] > 1:
            z_range = np.arange(1, dims['zdef']+1)

        return x_range, y_range, z_range

    # ----------------------------------------------------------------------------------------------

    def get_ndims_used(self, dims):

        # Ignore dims with values of 0 or 1
        ndims = len(dims)
        for x in range(ndims):
            if list(dims.values())[x] <= 1:
                ndims -= 1

        return ndims

    # ----------------------------------------------------------------------------------------------

    def load_dset(self, vars, nvars, coords, darr, dims, ndims_used,
                  x_range, y_range, z_range, cyc_darr):

        # create dataset from file components
        rtn_ds = None

        if ndims_used == 1:
            for x in range(0, nvars):
                new_ds = Dataset(
                    {
                        vars[x]: ((coords['xdef']), darr[x, :]),
                    },
                    coords={coords['xdef']: x_range},
                )
                rtn_ds = new_ds if rtn_ds is None else rtn_ds.merge(new_ds)

            # tack on 'cycle' as a variable
            new_cyc = Dataset(
                {
                    'cycle': ((coords['xdef']), cyc_darr),
                },
                coords={coords['xdef']: np.arange(1, dims['xdef']+1)},
            )

        if ndims_used == 2:
            for x in range(0, nvars):
                new_ds = Dataset(
                    {
                        vars[x]: ((coords['xdef'], coords['ydef']), darr[x, :, :]),
                    },
                    coords={coords['xdef']: x_range,
                            coords['ydef']: y_range},
                )
                rtn_ds = new_ds if rtn_ds is None else rtn_ds.merge(new_ds)

            # tack on 'cycle' as a variable
            new_cyc = Dataset(
                {
                    'cycle': ((coords['xdef'], coords['ydef']), cyc_darr),
                },
                coords={coords['xdef']: np.arange(1, dims['xdef']+1),
                        coords['ydef']: np.arange(1, dims['ydef']+1)},
            )

        if ndims_used == 3:
            self.logger.info('x_range: ' + str(x_range))
            self.logger.info('darr.shape: ' + str(darr.shape))

            for x in range(0, nvars):
                new_ds = Dataset(
                    {
                        vars[x]: ((coords['xdef'], coords['ydef'],
                                   coords['zdef']), darr[x, :, :, :]),
                    },
                    coords={coords['xdef']: x_range,
                            coords['ydef']: y_range,
                            coords['zdef']: z_range},
                )
                rtn_ds = new_ds if rtn_ds is None else rtn_ds.merge(new_ds)

            # tack on 'cycle' as a variable
            new_cyc = Dataset(
                {
                    'cycle': ((coords['xdef'], coords['ydef'], coords['zdef']), cyc_darr),
                },
                coords={coords['xdef']: np.arange(1, dims['xdef']+1),
                        coords['ydef']: np.arange(1, dims['ydef']+1),
                        coords['zdef']: np.arange(1, dims['zdef']+1)},
            )

        rtn_ds = rtn_ds.merge(new_cyc)
        return rtn_ds
