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

from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get
from eva.utilities.utils import parse_channel_list, is_number

# --------------------------------------------------------------------------------------------------


class MonDataSpace(EvaDatasetBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, dataset_config, data_collections, timing):

        # Set the collection name
        # -----------------------
        collection_name = get(dataset_config, self.logger, 'name')

        # Get control file and parse
        # --------------------------
        control_file = get(dataset_config, self.logger, 'control_file')
        coords, dims, attribs, nvars, vars, channo, scanpo, chan_assim, chan_nassim = (
                                                      self.get_ctl_dict(control_file[0]))
        ndims_used, dims_arr = self.get_ndims_used(dims)

        # Get the groups to be read
        # -------------------------
        groups = get(dataset_config, self.logger, 'groups')

        # Trim coordinates
        # ----------------
        coord_dict = {
            0: ['channels', 'Channel'],
            1: ['regions', 'Region'],
            2: ['levels', 'Level']
        }
        drop_coord = [False, False, False]
        requested_coord = [None, None, None]

        for x in range(len(coord_dict)):
            str_or_list = get(dataset_config, self.logger, coord_dict[x][0], abort_on_failure=False)
            if str_or_list is not None:
                requested_coord[x] = parse_channel_list(str(str_or_list), self.logger)
                drop_coord[x] = True

        # Set coordinate ranges
        # ---------------------
        x_range, y_range, z_range = self.get_dim_ranges(coords, dims, channo)

        # Filenames to be read into this collection
        # -----------------------------------------
        filenames = get(dataset_config, self.logger, 'filenames')
        ds_list = []

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        for filename in filenames:

            # read data file
            darr, cycle_tm = self.read_ieee(filename, coords, dims, ndims_used,
                                            dims_arr, nvars, vars)

            # add cycle as a variable to data array
            cyc_darr = self.var_to_np_array(dims, ndims_used, dims_arr, cycle_tm)

            # create dataset from file contents
            timestep_ds = None

            timestep_ds = self.load_dset(vars, nvars, coords, darr, dims, ndims_used,
                                         dims_arr, x_range, y_range, z_range, cyc_darr, channo)

            if attribs['sat']:
                timestep_ds.attrs['satellite'] = attribs['sat']
            if attribs['sensor']:
                timestep_ds.attrs['sensor'] = attribs['sensor']

            # add cycle_tm dim for concat
            timestep_ds['Time'] = cycle_tm.strftime("%Y%m%d%H")

            # Add this dataset to the list of ds_list
            ds_list.append(timestep_ds)

        # Concatenate datasets from ds_list into a single dataset
        ds = concat(ds_list, dim='Time')

        # Group name and variables
        # ------------------------
        for group in groups:
            group_name = get(group, self.logger, 'name')
            group_vars = get(group, self.logger, 'variables', 'all')

            # Drop coordinates not in requested list
            # --------------------------------------
            for x in range(len(coord_dict)):
                if drop_coord[x]:
                    ds = self.subset_coordinate(ds, coord_dict[x][1], requested_coord[x])

            # If user specifies all variables set to group list
            # -------------------------------------------------
            if group_vars == 'all':
                group_vars = list(ds.data_vars)

            # Conditionally add channel as a variable using single dimension
            # If channel is used then add chan_assim, chan_nassim, and
            # chan_yaxis to allow plotting of channel markers.
            # --------------------------------------------------------------
            if 'channel' in group_vars:
                ds['channel'] = (['Channel'], channo)
                ds['chan_assim'] = (['Channel'], chan_assim)
                ds['chan_nassim'] = (['Channel'], chan_nassim)
                ds['chan_yaxis_100'] = (['Channel'], [-100]*len(channo))
                ds['chan_yaxis_1p5'] = (['Channel'], [-1.5]*len(channo))
                ds['chan_yaxis_p05'] = (['Channel'], [-0.05]*len(channo))

            # Conditionally add scan position as a variable using single dimension
            # --------------------------------------------------------------------
            if 'scan' in group_vars:
                ds['scan'] = (['scan'], scanpo)

            # Drop data variables not in user requested variables
            # ---------------------------------------------------
            vars_to_remove = list(set(list(ds.keys())) - set(group_vars))
            ds = ds.drop_vars(vars_to_remove)

            # Rename variables with group
            rename_dict = {}
            for group_var in group_vars:
                rename_dict[group_var] = group_name + '::' + group_var

            ds = ds.rename(rename_dict)

            # Assert that the collection contains at least one variable
            if not ds.keys():
                self.logger.abort('Collection \'' + dataset_config['name'] + '\', group \'' +
                                  group_name + '\' in file ' + filename +
                                  ' does not have any variables.')

        # Add the dataset to the collections
        data_collections.create_or_add_to_collection(collection_name, ds, 'cycle')

        # Nan out unphysical values
        data_collections.nan_float_values_outside_threshold(threshold)

        # Display the contents of the collections for helping the user with making plots
        data_collections.display_collections()

    # ----------------------------------------------------------------------------------------------

    def generate_default_config(self, filenames, collection_name, control_file):
        'satellite': None,
        'sensor': None,
        'control_file': control_file,
        'filenames': filenames,
        'channels': [],
        'regions': [],
        'levels': [],
        'groups': [],
        'name': collection_name

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
            self.logger.info('Warning:  requested coordinate, ' + str(coordinate) + ' is not in ' +
                             ' dataset dimensions valid dimensions include ' + str(ds.dims))

        return ds

    # ----------------------------------------------------------------------------------------------

    # Parse control file and return elements in dictionaries
    def get_ctl_dict(self, control_file):

        coords = {'xdef': None, 'ydef': None, 'zdef': None}
        coord_list = []
        dims = {'xdef': 0, 'ydef': 0, 'zdef': 0}
        dim_list = []
        attribs = {'sensor': None, 'sat': None}
        vars = []
        nvars = 0
        channo = []
        chan_assim = []
        chan_nassim = []
        scanpo = None
        scan_info = []

        coord_dict = {
                     'channel': 'Channel',
                     'scan': 'Scan',
                     'pressure': 'Level',
                     'region': 'Region',
                     'iter': 'Iteration'
        }

        with open(control_file, 'r') as fp:
            lines = fp.readlines()
            for line in lines:

                # Locate the coordinates using coord_dict.  There will be 1-3
                # coordinates specified as XDEF, YDEF, and ZDEF.
                for item in list(coord_dict.keys()):
                    if 'DEF' in line and item in line:
                        coord_list.append(coord_dict[item])

                # In most cases xdef, ydef, and zdef specify the size of
                # the coresponding coordinate.
                #
                # Scan is different. If xdef coresponds to Scan then the xdef line
                # specifies the number of scan steps, starting position, and step size.
                # The last 2 are floats.  Add all to scan_info for later use.
                if line.find('xdef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            dim_list.append(int(st))
                        if is_number(st):
                            scan_info.append(st)

                if line.find('ydef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            dim_list.append(int(st))

                if line.find('zdef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            dim_list.append(int(st))

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
                #
                # If channel is used then assign channel numbers to the chan_assim and
                # chan_nassim arrays based on the channel's iuse setting in the control
                # file.  In the file 1 = assimilated, -1 = not assimilated.
                if line.find('channel=') != -1:
                    strs = line.split()
                    if strs[4].isdigit():
                        channo.append(int(strs[4]))
                    if strs[7] == '1':
                        chan_assim.append(int(strs[4]))
                    if strs[7] == '-1':
                        chan_nassim.append(int(strs[4]))

            # The list of variables is at the end of the file between the lines
            # "vars" and "end vars".
            start = len(lines) - (nvars + 1)
            for x in range(start, start + nvars):
                strs = lines[x].split()
                vars.append(strs[-1])

            # Ignore any coordinates in the control file that have a value of 1.
            used = 0
            mydef = ["xdef", "ydef", "zdef"]
            for x in range(3):
                if dim_list[x] > 2:
                    coords[mydef[used]] = coord_list[x]
                    dims[mydef[used]] = dim_list[x]
                    used += 1

            # If Scan is in the coords calculate the scan positions.
            # scan_info[0] = num steps, [1] = start position, [2] = step size
            if 'Scan' in coords.values():
                scanpo = [(float(scan_info[1]))]
                for x in range(1, int(scan_info[0])):
                    scanpo.append(float(scan_info[1])+(float(scan_info[2])*x))

            # If Channel is in the coords then pad out the chan_assim adn chan_nassim
            # arrays with zeros.  They need to be the correct length to use 'Channel' as
            # the dimension.  Also the yaml file can use the 'select where' transform
            # to drop all values < 1 and plot only the assim/nassim channel markers.
            if 'Channel' in coords.values():
                for x in range(len(chan_assim), len(channo)):
                    chan_assim.append(0)
                for x in range(len(chan_nassim), len(channo)):
                    chan_nassim.append(0)

        return coords, dims, attribs, nvars, vars, channo, scanpo, chan_assim, chan_nassim

    def read_ieee(self, file_name, coords, dims, ndims_used, dims_arr, nvars, vars, file_path=None):

        # find cycle time in filename and create cycle_tm as datetime object
        cycle_tm = None
        cycstrs = file_name.replace('/', '.').split('.')

        for cycstr in cycstrs:
            if ((cycstr.isnumeric()) and (len(cycstr) == 10)):
                cycle_tm = datetime(int(cycstr[0:4]), int(cycstr[4:6]),
                                    int(cycstr[6:8]), int(cycstr[8:]))

        filename = os.path.join(file_path, file_name) if file_path else file_name

        load_data = True
        if os.path.isfile(filename):
            f = FortranFile(filename, 'r', '>u4')
        else:
            self.logger.info(f"WARNING:  file {filename} is missing")
            load_data = False

        if ndims_used == 1:		# MinMon
            rtn_array = np.empty((0, dims[dims_arr[0]]), dtype=float)
            if not load_data:
                zarray = np.zeros((dims[dims_arr[0]]), float)
            dimensions = [dims[dims_arr[0]]]

        if ndims_used == 2:		# RadMon time, bcoef, bcor, OznMon time
            rtn_array = np.empty((0, dims[dims_arr[0]], dims[dims_arr[1]]), float)
            if not load_data:
                zarray = np.zeros((dims[dims_arr[0]], dims[dims_arr[1]]), float)
            dimensions = [dims[dims_arr[1]], dims[dims_arr[0]]]

        if ndims_used == 3:		# RadMon angle
            rtn_array = np.empty((0, dims[dims_arr[0]], dims[dims_arr[1]],
                                  dims[dims_arr[2]]), float)
            zarray = np.zeros((dims[dims_arr[0]], dims[dims_arr[1]],
                               dims[dims_arr[2]]), float)

            dimensions = [dims[dims_arr[0]], dims[dims_arr[1]]]

            for x in range(nvars):

                if load_data:
                    # satang variable is not used and a non-standard size
                    if vars[x] == 'satang':
                        skip = f.read_reals(dtype=np.dtype('>f4')).reshape(dims['xdef'],
                                                                           dims['ydef'])
                        tarr = zarray
                    else:
                        mylist = []
                        for z in range(5):
                            arr = f.read_reals(dtype=np.dtype('>f4')).reshape(dims['ydef'],
                                                                              dims['xdef'])
                            mylist.append(np.transpose(arr))
                        tarr = np.dstack(mylist)

                else:
                    tarr = zarray
                rtn_array = np.append(rtn_array, [tarr], axis=0)

        else:		# ndims_used == 1|2
            for x in range(nvars):
                if load_data:
                    if ndims_used == 1:
                        arr = np.fromfile(file_name, dtype='f4').reshape(dimensions)
                    else:
                        arr = np.transpose(f.read_reals(dtype=np.dtype('>f4')).reshape(dimensions))
                else:
                    arr = zarray
                rtn_array = np.append(rtn_array, [arr], axis=0)

        if load_data:
            f.close()
        return rtn_array, cycle_tm

    # ----------------------------------------------------------------------------------------------

    def var_to_np_array(self, dims, ndims_used, dims_arr, var):

        # build numpy array with requested dimensions
        d = {
            1: np.reshape([[var] * dims[dims_arr[0]]], (dims[dims_arr[0]])),
            2: np.reshape([[var] * dims[dims_arr[0]]] * dims[dims_arr[1]],
                          (dims[dims_arr[0]], dims[dims_arr[1]])),
            3: np.reshape([[var] * dims[dims_arr[0]] * dims[dims_arr[1]] * dims[dims_arr[2]]],
                          (dims[dims_arr[0]], dims[dims_arr[1]], dims[dims_arr[2]]))
        }

        try:
            cycle_arr = d[ndims_used]
        except KeyError:
            self.logger.abort(f'ndims_used must be in range of 1-3, value is {ndims_used}')

        return cycle_arr

    # ----------------------------------------------------------------------------------------------

    def get_dim_ranges(self, coords, dims, channo):
        x_range = None
        y_range = None
        z_range = None

        # - Return None for a coordinate that has value 0 or 1.
        # - "Channel" can be either the x or y coordinate and can be
        #      numbered non-consecutively, which has been captured in channo.
        # - The z coordinate is never used for channel.

        if dims['xdef'] > 1:
            x_range = channo if coords['xdef'] == 'Channel' else np.arange(1, dims['xdef']+1)

        if dims['ydef'] > 1:
            y_range = channo if coords['ydef'] == 'Channel' else np.arange(1, dims['ydef']+1)

        if dims['zdef'] > 1:
            z_range = np.arange(1, dims['zdef']+1)

        return x_range, y_range, z_range

    # ----------------------------------------------------------------------------------------------

    def get_ndims_used(self, dims):
        # Some ieee files (ozn) can be 1 or 2 dimensions depending on the
        # number of levels used.  Levels is the xdef, Regions is the ydef.
        # All Ozn files use ydef, but many have xdef = 1.  The dims_arr[]
        # will return the name(s) of the dimensions actually used.

        # Ignore dims with values of 0 or 1
        ndims = len(dims)
        dims_arr = []
        for x in range(ndims):
            if list(dims.values())[x] <= 1:
                ndims -= 1
            else:
                dims_arr.append(list(dims)[x])

        for x in range(ndims, 3):
            dims_arr.append(list(dims)[2])

        return ndims, dims_arr

    # ----------------------------------------------------------------------------------------------

    def load_dset(self, vars, nvars, coords, darr, dims, ndims_used,
                  dims_arr, x_range, y_range, z_range, cyc_darr, channo):

        # create dataset from file components
        rtn_ds = None

        for x in range(0, nvars):
            if ndims_used == 1:
                d = {
                    vars[x]: {"dims": (coords[dims_arr[0]]), "data": darr[x, :]}
                }
            if ndims_used == 2:
                d = {
                    vars[x]: {"dims": (coords[dims_arr[0]], coords[dims_arr[1]]),
                              "data": darr[x, :, :]}
                }
            if ndims_used == 3:
                d = {
                    vars[x]: {"dims": (coords[dims_arr[0]], coords[dims_arr[1]],
                                       coords[dims_arr[2]]),
                              "data": darr[x, :, :]}
                }

            if 'Channel' in coords.values():
                d.update({"Channel": {"dims": ("Channel"), "data": channo}})

            new_ds = Dataset.from_dict(d)
            rtn_ds = new_ds if rtn_ds is None else rtn_ds.merge(new_ds)

        # tack on 'cycle' as a variable
        # -----------------------------
        if ndims_used == 1:
            new_cyc = Dataset(
                {
                    'cycle': ((coords[dims_arr[0]]), cyc_darr),
                },
                coords={coords[dims_arr[0]]: np.arange(1, dims[dims_arr[0]]+1)},
            )
        if ndims_used == 2:
            new_cyc = Dataset(
                {
                    'cycle': ((coords[dims_arr[0]], coords[dims_arr[1]]), cyc_darr),
                },
                coords={coords[dims_arr[0]]: np.arange(1, dims[dims_arr[0]]+1),
                        coords[dims_arr[1]]: np.arange(1, dims[dims_arr[1]]+1)},
            )
        if ndims_used == 3:
            new_cyc = Dataset(
                {
                    'cycle': ((coords[dims_arr[0]], coords[dims_arr[1]],
                               coords[dims_arr[2]]), cyc_darr),
                },
                coords={coords[dims_arr[0]]: np.arange(1, dims[dims_arr[0]]+1),
                        coords[dims_arr[1]]: np.arange(1, dims[dims_arr[1]]+1),
                        coords[dims_arr[2]]: np.arange(1, dims[dims_arr[2]]+1)},
            )
        rtn_ds = rtn_ds.merge(new_cyc)
        return rtn_ds
