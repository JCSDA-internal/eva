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
import array

from xarray import Dataset, concat, merge, align
from scipy.io import FortranFile
from datetime import datetime

from eva.data.eva_dataset_base import EvaDatasetBase
from eva.utilities.config import get
from eva.utilities.utils import parse_channel_list, is_number

# --------------------------------------------------------------------------------------------------


class MonDataSpace(EvaDatasetBase):

    """
    A class for handling MonDataSpace dataset configuration and processing.
    """

    # index values for specific control files
    level_iuse_ozn = 7
    channel_iuse_rad = 7
    channel_num_rad = 4
    type_con = 1
    datatype_con = 5
    subtype_con = 7
    regions_rad_ang = 5

    def execute(self, dataset_config, data_collections, timing):

        """
        Executes the processing of MonDataSpace dataset.

        Args:
            dataset_config (dict): Configuration dictionary for the dataset.
            data_collections (DataCollections): Object for managing data collections.
            timing (Timing): Timing object for tracking execution time.
        """

        stn_data = False

        # Set the collection name
        # -----------------------
        collection_name = get(dataset_config, self.logger, 'name')

        # Filenames to be read into this collection
        # -----------------------------------------
        filenames = get(dataset_config, self.logger, 'filenames')

        # Get control file and parse
        # --------------------------
        control_file = get(dataset_config, self.logger, 'control_file')

        dims_arr = []
        if self.is_stn_data(control_file[0]):
            coords, dims, attribs, nvars, vars, scanpo, levs_dict, chans_dict, datatype_dict = (
                                                        self.get_stn_ctl_dict(control_file[0]))
            ndims_used = 2
            dims_arr = ['xdef', 'ydef', 'zdef']
            stn_data = True
        else:
            coords, dims, attribs, nvars, vars, scanpo, levs_dict, chans_dict, datatype_dict = (
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
        channo = chans_dict["chan_nums"] if chans_dict is not None else None
        datatypes = datatype_dict["datatype"] if datatype_dict is not None else None
        x_range, y_range, z_range = self.get_dim_ranges(coords, dims, channo, datatypes)

        # Get missing value threshold
        # ---------------------------
        threshold = float(get(dataset_config, self.logger, 'missing_value_threshold', 1.0e30))

        ds_list = []
        for filename in filenames:

            lat = []
            lon = []
            if stn_data:

                # Read station data file.  Note that the variable dimensions
                # will NOT be the same for different station data files.
                darr, cycle_tm, dims, lat, lon = self.read_stn_ieee(filename, coords, dims,
                                                                    ndims_used, dims_arr, nvars,
                                                                    vars)
                y_range = np.arange(1, dims['ydef']+1)

            else:
                # read data file
                darr, cycle_tm = self.read_ieee(filename, coords, dims, ndims_used,
                                                dims_arr, nvars, vars)

            # add cycle as a variable to data array
            cyc_darr = self.var_to_np_array(dims, ndims_used, dims_arr, cycle_tm)

            # create dataset from file contents
            timestep_ds = None
            timestep_ds = self.load_dset(vars, nvars, coords, darr, dims, ndims_used,
                                         dims_arr, x_range, y_range, z_range, cyc_darr)

            if attribs['sat']:
                timestep_ds.attrs['satellite'] = attribs['sat']
            if attribs['sensor']:
                timestep_ds.attrs['sensor'] = attribs['sensor']

            # Add lat and lon variables.  This is done separately because they are
            # only single dimension arrays unlike the obs which are 2d (level, nobs).
            if stn_data and len(lat):
                timestep_ds['lat'] = (['Nobs'], (lat))
            if stn_data and len(lon):
                timestep_ds['lon'] = (['Nobs'], (lon))

            # add cycle_tm dim for concat
            timestep_ds['Time'] = cycle_tm.strftime("%Y%m%d%H")

            # Add this dataset to the list of ds_list
            ds_list.append(timestep_ds)

        # Align all datasets.  This syncs the dimensions and variables
        # of all datasets in ds_list using NaN for all missing data.
        if stn_data:
            ds_list = align(*ds_list, join='outer', exclude=[])

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
                    ds, chans_dict = \
                       self.subset_coordinate(ds, coord_dict[x][1], requested_coord[x], chans_dict)

            # Conditionally add channel, level, scan, and iteration related variables
            # -----------------------------------------------------------------------
            iterations = x_range if 'Iteration' in coords.values() else None
            ds = self.loadConditionalItems(ds, chans_dict, levs_dict,
                                           datatype_dict, scanpo, iterations)

            # Rename variables with group
            rename_dict = {}
            for var in list(ds.data_vars):
                rename_dict[var] = group_name + '::' + var
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

        """
        Generates a default configuration for MonDataSpace dataset.

        Args:
            filenames (list): List of file names.
            collection_name (str): Name of the data collection.
            control_file (str): Path to the control file.

        Returns:
            dict: Default configuration dictionary.
        """

        eva_dict = {'satellite': None,
                    'sensor': None,
                    'control_file': control_file,
                    'filenames': filenames,
                    'channels': [],
                    'regions': [],
                    'levels': [],
                    'groups': [],
                    'name': collection_name}
        return eva_dict

    # ----------------------------------------------------------------------------------------------

    def subset_coordinate(self, ds, coordinate, requested_subset, chans_dict):

        """
        Subset the input dataset along the specified coordinate dimension and update channel
        information.

        Args:
            ds (xarray.Dataset): Input dataset to be subset.
            coordinate (str): Name of the coordinate dimension to subset.
            requested_subset (list): List of values to keep along the specified coordinate.
            chans_dict (dict): Dictionary of channel components.
        Returns:
            xarray.Dataset: Subset of the input dataset.
            chans_dict (dict): Updated dictionary of channel components.
        """

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

            # If Channel coordinate has been reduced from "all" (by yaml
            # file) then reset chan_assim/nassim and channo accordingly
            if coordinate == 'Channel':
                new_chan_assim = []
                new_chan_nassim = []

                for x in requested_subset:
                    if x in chans_dict['chans_assim']:
                        new_chan_assim.append(x)
                    elif x in chans_dict['chans_nassim']:
                        new_chan_nassim.append(x)

                for x in range(len(new_chan_assim), len(requested_subset)):
                    new_chan_assim.append(0)
                for x in range(len(new_chan_nassim), len(requested_subset)):
                    new_chan_nassim.append(0)

                chans_dict['chan_nums'] = requested_subset
                chans_dict['chans_assim'] = new_chan_assim
                chans_dict['chans_nassim'] = new_chan_nassim

        else:
            self.logger.info('Warning:  requested coordinate, ' + str(coordinate) + ' is not in ' +
                             ' dataset dimensions valid dimensions include ' + str(ds.dims))

        return ds, chans_dict

    # ----------------------------------------------------------------------------------------------

    def get_ctl_dict(self, control_file):

        """
        Parse the control file and extract information into dictionaries.

        Args:
            control_file (str): Path to the control file.

        Returns:
            dict: Dictionary containing various coordinates and information.
            dict: Dictionary containing dimension sizes.
            dict: Dictionary containing sensor and satellite attributes.
            int: Number of variables.
            list: List of variable names.
            list: List of scan positions.
            dict: Dictionary containing channel information.
            dict: Dictionary containing level information.
            dict: Dictionary containing datatype information.
        """

        coords = {'xdef': None, 'ydef': None, 'zdef': None}
        coord_list = []
        dims = {'xdef': 0, 'ydef': 0, 'zdef': 0}
        dim_list = []
        attribs = {'sensor': None, 'sat': None, 'datatype': None}
        vars = []
        nvars = 0
        chans_dict = None
        channo = []
        chan_assim = []
        chan_nassim = []
        scanpo = None
        scan_info = []
        levs_dict = None
        levs = []
        level_assim = []
        level_nassim = []
        datatype_dict = None
        datatype = []
        datatype_assim = []

        coord_dict = {
                     'channel': 'Channel',
                     'scan': 'Scan',
                     'pressure': 'Level',
                     'vertical': 'Level',
                     'region': 'Region',
                     'iter': 'Iteration',
                     'data type': 'DataType'
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

                if line.find('datatype station') != -1 or line.find('DTYPE station') != -1:
                    attribs['datatype'] = 'station'

                if line.find('subtype') != -1:
                    strs = line.split()
                    datatype.append(strs[self.type_con] + strs[self.datatype_con] + '_' +
                                    strs[self.subtype_con])
                    datatype_assim.append(strs[9])

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
                        channo.append(int(strs[self.channel_num_rad]))
                    if strs[self.channel_iuse_rad] == '1':
                        chan_assim.append(int(strs[self.channel_num_rad]))
                    if strs[self.channel_iuse_rad] == '-1':
                        chan_nassim.append(int(strs[self.channel_num_rad]))

                if line.find('level=') != -1:

                    strs = line.split()
                    tlev = strs[2].replace(',', '')
                    if tlev.isdigit():
                        levs.append(int(tlev))

                    # Ozn data control files include the assim flag on the Level definition
                    # lines.  Con data control files use level but assim is included on the
                    # datatype line, not Level
                    #
                    if len(strs) >= self.level_iuse_ozn:
                        if strs[self.level_iuse_ozn] == '1':
                            level_assim.append(int(tlev))
                        if strs[self.level_iuse_ozn] == '-1':
                            level_nassim.append(int(tlev))

            # The list of variables is at the end of the file between the lines
            # "vars" and "end vars".
            start = len(lines) - (nvars + 1)
            for x in range(start, start + nvars):
                strs = lines[x].split()
                vars.append(strs[0])

            # Ignore any coordinates in the control file that have a value of 1.
            used = 0
            mydef = ["xdef", "ydef", "zdef"]
            for x in range(len(dim_list)):
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
                chans_dict = {'chan_nums': channo,
                              'chans_assim': chan_assim,
                              'chans_nassim': chan_nassim}

            if 'Level' in coords.values():
                levs_dict = {'levels': levs}

                if len(level_assim) > 0 or len(level_nassim) > 0:
                    for x in range(len(level_assim), len(levs)):
                        level_assim.append(0)
                    for x in range(len(level_nassim), len(levs)):
                        level_nassim.append(0)
                    levs_dict['levels_assim'] = level_assim
                    levs_dict['levels_nassim'] = level_nassim

            if 'DataType' in coords.values():
                datatype_dict = {'datatype': datatype,
                                 'assim': datatype_assim}

            fp.close()
        return coords, dims, attribs, nvars, vars, scanpo, levs_dict, chans_dict, datatype_dict

    # ----------------------------------------------------------------------------------------------

    def get_stn_ctl_dict(self, control_file):

        """
        Parse the station data control file and extract information into dictionaries.

        Args:
            control_file (str): Path to the control file.

        Returns:
            dict: Dictionary containing various coordinates and information.
            dict: Dictionary containing dimension sizes.
            dict: Dictionary containing sensor and satellite attributes.
            int: Number of variables.
            list: List of variable names.
            list: List of scan positions.
            dict: Dictionary containing channel information.
            dict: Dictionary containing level information.
            dict: Dictionary containing datatype information.
        """

        coords = {'xdef': 'Level', 'ydef': 'Nobs', 'zdef': None}
        dims = {'xdef': 0, 'ydef': 0, 'zdef': 0}
        dim_list = []
        attribs = {'sensor': None, 'sat': None, 'datatype': 'station'}
        vars = []
        nvars = 0
        chans_dict = None
        scanpo = None
        levs_dict = None
        levs = []
        lev_vals = []
        level_assim = []
        level_nassim = []
        datatype_dict = None
        datatype = []
        datatype_assim = []

        coord_dict = {
                     'channel': 'Channel',
                     'scan': 'Scan',
                     'pressure': 'Level',
                     'region': 'Region',
                     'iter': 'Iteration',
                     'data type': 'DataType'
        }

        with open(control_file, 'r') as fp:
            lines = fp.readlines()
            for line in lines:

                # Find level information
                if line.find('level=') != -1:
                    strs = line.split()

                    lev_vals.append({'lev_val': strs[4], 'iuse': strs[7], 'err_val': strs[10]})
                    lev_str = strs[2].split(',')
                    levs.append(int(lev_str[0]))

                    if strs[7] == '1':
                        level_assim.append(int(lev_str[0]))
                    else:
                        level_nassim.append(int(lev_str[0]))

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

            # The list of variables is at the end of the file between the lines
            # "vars" and "end vars".  Note that for ozn station control files the
            # var is repeated for every level (e.g. obs1, obs2, obs3, etc).  These
            # need to be combined into single entries in the vars list and nvars
            # then set to the final size of the vars list.
            start = len(lines) - (nvars + 1)
            for x in range(start, start + nvars):
                strs = lines[x].split()
                if strs[-1] not in vars:
                    vars.append(strs[-1])
            nvars = len(vars)

            # set levels
            dim_list.append(len(lev_vals))
            dim_list.append(0)

            # Ignore any coordinates in the control file that have a value of 1.
            used = 0
            mydef = ["xdef", "ydef", "zdef"]

            if 'Level' in coords.values():
                for x in range(len(level_assim), len(levs)):
                    level_assim.append(0)
                for x in range(len(level_nassim), len(levs)):
                    level_nassim.append(0)
                levs_dict = {'levels': levs,
                             'levels_assim': level_assim,
                             'levels_nassim': level_nassim}
                dims['xdef'] = len(levs)

            if 'DataType' in coords.values():
                datatype_dict = {'datatype': datatype,
                                 'assim': datatype_assim}

        fp.close()
        return coords, dims, attribs, nvars, vars, scanpo, levs_dict, chans_dict, datatype_dict

    # ----------------------------------------------------------------------------------------------

    def read_ieee(self, file_name, coords, dims, ndims_used, dims_arr, nvars, vars, file_path=None):

        """
        Read data from an IEEE file and arrange it into a numpy array.

        Args:
            file_name (str): Name of the IEEE file to read.
            coords (dict): Dictionary of coordinates.
            dims (dict): Dictionary of dimension sizes.
            ndims_used (int): Number of dimensions used.
            dims_arr (list): List of dimension names used.
            nvars (int): Number of variables.
            vars (list): List of variable names.
            file_path (str, optional): Path to the directory containing the file. Defaults to None.

        Returns:
            numpy.ndarray: Numpy array containing the read data.
            datetime.datetime: Cycle time extracted from the filename.
        """

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
            rtn_array = np.empty((0, dims[dims_arr[0]]), datatype=float)
            if not load_data:
                zarray = np.zeros((dims[dims_arr[0]]), float)
            dimensions = [dims[dims_arr[0]]]

        if ndims_used == 2:		# RadMon time, bcoef, bcor, OznMon time
            rtn_array = np.empty((0, dims[dims_arr[0]], dims[dims_arr[1]]), float)
            if not load_data:
                zarray = np.zeros((dims[dims_arr[0]], dims[dims_arr[1]]), float)
            dimensions = [dims[dims_arr[1]], dims[dims_arr[0]]]

        if ndims_used == 3:		# RadMon angle, ConMon time/vert
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
                        for z in range(dims['zdef']):
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
                        with open(filename, 'rb') as infile:
                            binary_data = infile.read()

                        arr = array.array('f')
                        arr.frombytes(binary_data)
                    else:
                        arr = np.transpose(f.read_reals(dtype=np.dtype('>f4')).reshape(dimensions))
                else:
                    arr = zarray

                rtn_array = np.append(rtn_array, [arr], axis=0)
        if load_data:
            f.close()
        return rtn_array, cycle_tm

    # ----------------------------------------------------------------------------------------------

    def read_stn_ieee(self, file_name, coords, dims, ndims_used, dims_arr,
                      nvars, vars, file_path=None):

        """
        Read station data from an IEEE file and arrange it into a numpy array.

        Args:
            file_name (str): Name of the IEEE station file to read.
            coords (dict): Dictionary of coordinates.
            dims (dict): Dictionary of dimension sizes.
            ndims_used (int): Number of dimensions used.
            dims_arr (list): List of dimension names used.
            nvars (int): Number of variables.
            vars (list): List of variable names.
            file_path (str, optional): Path to the directory containing the file. Defaults to None.

        Returns:
            numpy.ndarray: Numpy array containing the read data.
            datetime.datetime: Cycle time extracted from the filename.
            list: Updated list of dimensions
            list: Lat location of obs
            list: Lon location of obs
        """

        rtn_array = None

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

        mylist = []
        lat = []
        lon = []
        numobs = 0

        if load_data:
            nlev = 1
            while (nlev):

                # Header components are stn id, lat, lon, time, nlev, flag.
                # Data follows header if nlev > 0, else it's EOF.
                record = f.read_record('>i8', '>f4', '>f4', '>f4', '>i4', '>i4')
                nlev = record[4]
                if nlev:
                    lat.append(record[1])
                    lon.append(record[2])
                    data = f.read_record('>f4').reshape([nvars, dims[dims_arr[0]]])
                    numobs += 1
                    mylist.append(data)

            # dimensions are nvar, nlev, numobs
            rtn_array = np.dstack(mylist)
            dims['ydef'] = numobs

        f.close()
        rtn_lat = np.asarray(lat).reshape(-1)
        rtn_lon = np.asarray(lon).reshape(-1)

        return rtn_array, cycle_tm, dims, rtn_lat, rtn_lon

    # ----------------------------------------------------------------------------------------------

    def var_to_np_array(self, dims, ndims_used, dims_arr, var):

        """
        Create a numpy array with specified dimensions and fill it with a given value.

        Args:
            dims (dict): Dictionary of dimension sizes.
            ndims_used (int): Number of dimensions used.
            dims_arr (list): List of dimension names used.
            var: Value to fill the array with.

        Returns:
            numpy.ndarray: Numpy array with the requested dimensions and filled with the given
            value.
        """

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

    def get_dim_ranges(self, coords, dims, channo, datatypes):

        """
        Get the valid ranges for each dimension based on the specified coordinates and channel
        numbers.

        Args:
            coords (dict): Dictionary of coordinates.
            dims (dict): Dictionary of dimension sizes.
            channo (list): List of channel numbers.
            datatypes (list): List of data types.

        Returns:
            numpy.ndarray or None: Valid x coordinate range or None.
            numpy.ndarray or None: Valid y coordinate range or None.
            numpy.ndarray or None: Valid z coordinate range or None.
        """

        x_range = None
        y_range = None
        z_range = None

        # - Return None for a coordinate that has value 0 or 1.
        # - "Channel" can be either the x or y coordinate and can be
        #      numbered non-consecutively, which has been captured in channo.
        # - The z coordinate is never used for channel.

        if dims['xdef'] > 1:
            if coords['xdef'] == 'Channel':
                x_range = channo
            elif coords['xdef'] == 'DataType':
                x_range = datatypes
            else:
                x_range = np.arange(1, dims['xdef']+1)

        if dims['ydef'] > 1:
            y_range = channo if coords['ydef'] == 'Channel' else np.arange(1, dims['ydef']+1)

        if dims['zdef'] > 1:
            z_range = np.arange(1, dims['zdef']+1)

        return x_range, y_range, z_range

    # ----------------------------------------------------------------------------------------------

    def get_ndims_used(self, dims):

        """
        Determine the number of dimensions used based on the provided dimension sizes.

        Args:
            dims (dict): Dictionary of dimension sizes.

        Returns:
            int: Number of dimensions used.
            list: List of dimension names used.
        """

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
                  dims_arr, x_range, y_range, z_range, cyc_darr=None):

        """
        Create a dataset from various components.

        Args:
            vars (list): List of variable names.
            nvars (int): Number of variables.
            coords (dict): Dictionary of coordinates.
            darr (numpy.ndarray): Numpy array of data.
            dims (dict): Dictionary of dimension sizes.
            ndims_used (int): Number of dimensions used.
            dims_arr (list): List of dimension names used.
            x_range (numpy.ndarray or None): Valid x coordinate range.
            y_range (numpy.ndarray or None): Valid y coordinate range.
            z_range (numpy.ndarray or None): Valid z coordinate range.
            cyc_darr (numpy.ndarray): Numpy array of cycle data.

        Returns:
            xarray.Dataset: Created dataset.
        """

        # create dataset from file components
        rtn_ds = None

        new_coords = {}
        for x in range(0, nvars):
            if ndims_used == 1:
                d = {
                    vars[x]: {"dims": (coords[dims_arr[0]]), "data": darr[x, :]}
                }

                # MinMon plots require both the 'allgnorm' data and log('allgnorm').
                if vars[x] == 'allgnorm':
                    d.update({
                        "log_gnorm": {"dims": (coords[dims_arr[0]]), "data": np.log(darr[x, :])}
                    })
                new_coords = {
                    coords[dims_arr[0]]: x_range
                }
            if ndims_used == 2:
                d = {
                    vars[x]: {"dims": (coords[dims_arr[0]], coords[dims_arr[1]]),
                              "data": darr[x, :, :]}
                }
                new_coords = {
                    coords[dims_arr[0]]: x_range,
                    coords[dims_arr[1]]: y_range
                }
            if ndims_used == 3:
                d = {
                    vars[x]: {"dims": (coords[dims_arr[0]], coords[dims_arr[1]],
                                       coords[dims_arr[2]]),
                              "data": darr[x, :, :]}
                }
                new_coords = {
                    coords[dims_arr[0]]: x_range,
                    coords[dims_arr[1]]: y_range,
                    coords[dims_arr[2]]: z_range
                }

            new_ds = Dataset.from_dict(d)
            rtn_ds = new_ds if rtn_ds is None else rtn_ds.merge(new_ds)

        # Add the new coordinates to the dataset
        rtn_ds = rtn_ds.assign_coords(new_coords)

        # tack on 'cycle' as a variable
        # -----------------------------
        if cyc_darr is not None:
            if ndims_used == 1:
                new_cyc = Dataset(
                    {
                        'cycle': ((coords[dims_arr[0]]), cyc_darr),
                    },
                    coords={coords[dims_arr[0]]: x_range},
                )
            if ndims_used == 2:
                new_cyc = Dataset(
                    {
                        'cycle': ((coords[dims_arr[0]], coords[dims_arr[1]]), cyc_darr),
                    },
                    coords={coords[dims_arr[0]]: x_range,
                            coords[dims_arr[1]]: y_range},
                )
            if ndims_used == 3:
                new_cyc = Dataset(
                    {
                        'cycle': ((coords[dims_arr[0]], coords[dims_arr[1]],
                                   coords[dims_arr[2]]), cyc_darr),
                    },
                    coords={coords[dims_arr[0]]: x_range,
                            coords[dims_arr[1]]: y_range,
                            coords[dims_arr[2]]: z_range},
                )

            rtn_ds = rtn_ds.merge(new_cyc)

        return rtn_ds

    # ----------------------------------------------------------------------------------------------

    def loadConditionalItems(self, dataset, chans_dict, levs_dict, datatype_dict,
                             scanpo, iterations=None):

        """
        Add channel, level, and scan related variables to the dataset.

        Args:
            dataset (xarray.Dataset): Dataset to which variables will be added.
            chans_dict (dict): Dictionary of channel components.
            levs_dict (dict): Dictionary of level components.
            scanpo (list): List of scan positions.
            iterations (list): List of iterations.
        Returns:
            xarray.Dataset: Dataset with added scan-related variables.
        """

        if chans_dict is not None:
            dataset['channel'] = (['Channel'], chans_dict["chan_nums"])
            dataset['chan_yaxis_z'] = (['Channel'], [0.0]*len(chans_dict["chan_nums"]))

            if len(chans_dict["chans_assim"]) > 0:
                dataset['chan_assim'] = (['Channel'], chans_dict["chans_assim"])
            if len(chans_dict["chans_nassim"]) > 0:
                dataset['chan_nassim'] = (['Channel'], chans_dict["chans_nassim"])

        if levs_dict is not None:

            # If datatype_dict is available then level needs to include that dimension
            # for potential batch processing by DataType (conmon vert plots).
            if datatype_dict is not None:
                combined_list = []
                for x in datatype_dict['datatype']:
                    combined_list.append(levs_dict['levels'])
                dataset['level'] = (['DataType', 'Level'], combined_list)
            else:
                dataset['level'] = (['Level'], levs_dict["levels"])
            dataset['level_yaxis_z'] = (['Level'], [0.0]*len(levs_dict["levels"]))

            if 'levels_assim' in levs_dict:
                dataset['level_assim'] = (['Level'], levs_dict["levels_assim"])
            if 'levels_nassim' in levs_dict:
                dataset['level_nassim'] = (['Level'], levs_dict["levels_nassim"])
            if 'levels_value' in levs_dict:
                dataset['level_value'] = (['Level'], levs_dict["levels_value"])

        if datatype_dict is not None:
            dataset['datatype'] = (['DataType'], datatype_dict['datatype'])
            dataset['datatype_assim'] = (['DataType'], datatype_dict['assim'])

        if scanpo is not None:
            nscan = dataset.dims.get('Scan')
            nchan = dataset.dims.get('Channel')	      # 'Channel' is always present with 'Scan'
            scan_array = np.zeros(shape=(nscan, nchan))

            for x in range(nchan):
                scan_array[:, x] = np.array([scanpo])
                dataset['scan'] = (['Scan', 'Channel'], scan_array)

        if iterations is not None:
            dataset['iteration'] = (['Iteration'], iterations)

        return dataset

    # ----------------------------------------------------------------------------------------------

    def is_stn_data(self, control_file):

        """
        Check for station data indicator in control file.

        Args:
            control_file(string): control file name.

        Returns:
            is_stn(boolean): True if this is a control file.
        """

        with open(control_file, 'r') as fp:
            content = fp.read()
            is_stn = True if 'DTYPE station' in content or 'dtype station' in content else False
            fp.close()

        return is_stn
