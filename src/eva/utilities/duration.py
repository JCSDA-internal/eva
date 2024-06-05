# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


from datetime import timedelta
import re

from eva.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def iso_duration_to_timedelta(logger: Logger, iso_duration: str) -> timedelta:
    """
    Convert an ISO 8601 duration string to a datetime.timedelta object.

    Parameters:
    iso_duration (str): The ISO 8601 duration string.

    Returns:
    timedelta: The equivalent datetime.timedelta object.
    """
    pattern = re.compile(
        r'P'  # starts with 'P'
        r'(?:(?P<years>\d+)Y)?'  # years
        r'(?:(?P<months>\d+)M)?'  # months
        r'(?:(?P<days>\d+)D)?'  # days
        r'(?:T'  # starts time part with 'T'
        r'(?:(?P<hours>\d+)H)?'  # hours
        r'(?:(?P<minutes>\d+)M)?'  # minutes
        r'(?:(?P<seconds>\d+)S)?'  # seconds
        r')?'  # end time part
    )

    match = pattern.match(iso_duration)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration string: {iso_duration}")

    parts = match.groupdict()
    years = int(parts['years']) if parts['years'] else 0
    months = int(parts['months']) if parts['months'] else 0
    days = int(parts['days']) if parts['days'] else 0
    hours = int(parts['hours']) if parts['hours'] else 0
    minutes = int(parts['minutes']) if parts['minutes'] else 0
    seconds = int(parts['seconds']) if parts['seconds'] else 0

    # Assert that years and months are zero
    logger.assert_abort(years == 0, "Years are not supported in parsing ISO 8601 durations.")
    logger.assert_abort(months == 0, "Months are not supported in parsing ISO 8601 durations.")

    # Compute total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds

    return timedelta(days=days, seconds=total_seconds)


# --------------------------------------------------------------------------------------------------
