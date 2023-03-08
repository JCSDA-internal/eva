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
from eva.utilities.utils import parse_channel_list

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
            channo, nchans, nregion, satellite, sensor = self.get_ctl_stats(control_file[0])

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
            regions_str_or_list = get(dataset, self.logger, 'regions', [])
            requested_regions = []
            drop_regions = False

            if regions_str_or_list is not None:

                if len(str(regions_str_or_list)) > 0:
                    requested_regions = parse_channel_list(str(regions_str_or_list), self.logger)
                    drop_regions = True

            # Filenames to be read into this collection
            # -----------------------------------------
            filenames = get(dataset, self.logger, 'filenames')
            ds_list = []

            # Get missing value threshold
            # ---------------------------
            threshold = float(get(dataset, self.logger, 'missing_value_threshold', 1.0e30))

            for filename in filenames:

                # read data file
                count_tmp, penalty_tmp, omgnbc_sum_tmp, total_sum_tmp, \
                    omgbc_sum_tmp, omgnbc_sum2_tmp, total_sum2_tmp, omgbc_sum2_tmp, cycle_tm = \
                    self.read_radmon_ieee(filename, nchans, nregion)

                # add cycle as a variable in dataset
                cycle_tmp = [[cycle_tm] * nregion] * nchans

                # create dataset from file contents
                timestep_ds = Dataset(
                    {
                        "count": (("channels", "regions"), count_tmp),
                        "penalty": (("channels", "regions"), penalty_tmp),
                        "omgnbc": (("channels", "regions"), omgnbc_sum_tmp),
                        "total": (("channels", "regions"), total_sum_tmp),
                        "omgbc": (("channels", "regions"), omgbc_sum_tmp),
                        "omgnbc2": (("channels", "regions"), omgnbc_sum2_tmp),
                        "total2": (("channels", "regions"), total_sum2_tmp),
                        "omgbc2": (("channels", "regions"), omgbc_sum2_tmp),
                        "cycle": (("channels", "regions"), cycle_tmp),
                    },
                    coords={"channels": channo, "regions": np.arange(1, nregion+1)},
                    attrs={'satellite': satellite, 'sensor': sensor},
                )
                timestep_ds['times'] = cycle_tm

                # Add this dataset to the list of ds_list
                ds_list.append(timestep_ds)

            # Concatenate datasets from ds_list into a single dataset
            ds = concat(ds_list, dim='times')

            # Group name and variables
            # ------------------------
            for group in groups:
                group_name = get(group, self.logger, 'name')
                group_vars = get(group, self.logger, 'variables', 'all')

                # Drop channels not in user requested list
                # ----------------------------------------
                if drop_channels:
                    ds = self.subset_coordinate(ds, 'channels', requested_channels)

                # Drop regions not in user requested list
                # ---------------------------------------
                if drop_regions:
                    ds = self.subset_coordinate(ds, 'regions', requested_regions)

                # If user specifies all variables set to group list
                # -------------------------------------------------
                if group_vars == 'all':
                    group_vars = list(ds.data_vars)

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
                    self.logger.abort('Collection \'' + dataset['name'] + '\', group \'' +
                                      group_name + '\' in file ' + filename +
                                      ' does not have any variables.')

            # Add the dataset to the collections
            data_collections.create_or_add_to_collection(collection_name, ds, 'count')

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

    def get_ctl_stats(self, control_file):
        chans = []
        nchans = None
        nregion = None
        satellite = None
        sensor = None

        with open(control_file, 'r') as fp:
            lines = fp.readlines()

            for line in lines:
                if line.find('xdef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            nchans = int(st)

                if line.find('ydef') != -1:
                    strs = line.split()
                    for st in strs:
                        if st.isdigit():
                            nregion = int(st)

                if line.find('channel=') != -1:
                    strs = line.split()
                    chans.append(strs[4])

                if line.find('title') != -1:
                    strs = line.split()
                    sensor = strs[1]
                    satellite = strs[2]

            channo = np.array(chans, dtype=int)
        return channo, nchans, nregion, satellite, sensor

    # ----------------------------------------------------------------------------------------------

    def read_radmon_ieee(self, file_name, nchans, nregion, file_path=None):

        if file_path:
            filename = os.path.join(file_path, file_name)
        else:
            filename = file_name
        if not os.path.isfile(filename):
            count = None
            penalty = None
            omgnbc_sum = None
            omgnbc_sum = None
            total_sum = None
            omgbc_sum = None
            omgnbc_sum2 = None
            omgbc_sum2 = None
            total_sum2 = None
            cycle_tm = None
            return count, penalty, omgnbc_sum, omgnbc_sum, total_sum, \
                omgbc_sum, omgnbc_sum2, omgbc_sum2, cycle_tm

        # find cycle time in filename and create cycle_tm as datetime object
        cycle_tm = None
        cycstrs = filename.split('.')

        for cycstr in cycstrs:
            if cycstr.isnumeric():
                cycle_tm = datetime(int(cycstr[0:4]), int(cycstr[4:6]),
                                    int(cycstr[6:8]), int(cycstr[8:]))

        # read binary Fortran file
        f = FortranFile(filename, 'r', '>u4')

        count = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        penalty = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        omgnbc_sum = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        total_sum = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        omgbc_sum = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        omgnbc_sum2 = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        total_sum2 = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)
        omgbc_sum2 = f.read_reals(dtype=np.dtype('>f4')).reshape(nchans, nregion)

        f.close()

        return count, penalty, omgnbc_sum, total_sum, omgbc_sum, \
            omgnbc_sum2, total_sum2, omgbc_sum2, cycle_tm

    # ----------------------------------------------------------------------------------------------
