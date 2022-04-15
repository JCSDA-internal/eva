# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from eva.utilities.config import get
from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def accept_or_reject_where(config, data_collections):

    # Create a logger
    logger = Logger('RejectWhereTransform')

    logger.info(f'{config}')


# --------------------------------------------------------------------------------------------------
