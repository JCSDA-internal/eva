# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


def ioda_platform_dict():

    ioda_platform_dictionary = {
      "aircraft": "Aircraft",
      "airs_aqua": "AIRS AQUA",
      "amsua_aqua": "AMSUA AQUA",
      "amsua_metop-a": "AMSUA METOP-A",
      "amsua_metop-b": "AMSUA METOP-B",
      "amsua_metop-c": "AMSUA METOP-C",
      "amsua_n15": "AMSUA NOAA-15",
      "amsua_n18": "AMSUA NOAA-18",
      "amsua_n19": "AMSUA NOAA-19",
      "atms_n20": "ATMS NOAA-20",
      "atms_npp": "ATMS NPP",
      "avhrr3_metop-a": "AVHRR3 METOP-A",
      "avhrr3_n18": "AVHRR3 NOAA-18",
      "avhrr3_n19": "AVHRR3 NOAA-19",
      "cris-fsr_n20": "CRIS FSR NOAA-20",
      "cris-fsr_npp": "CRIS FSR NPP",
      "gmi_gpm": "GMI GPM",
      "gnssrobndnbam": "GNSSRO",
      "iasi_metop-a": "IASI METOP-A",
      "iasi_metop-b": "IASI METOP-B",
      "mhs_metop-b": "MHS METOP-B",
      "mhs_metop-c": "MHS METOP-C",
      "mhs_n19": "MHS NOAA-19",
      "omi_aura": "OMI AURA",
      "ompsnp_npp": "OMPSNP NPP",
      "ompstc8_npp": "OMPSTC8 NPP",
      "rass_tv": "RASS Tv",
      "satwind": "Satellite Wind",
      "scatwind": "Scatterometer Wind",
      "seviri_m11": "SEVIRI Meteosat-11",
      "sfcship": "Surface ship",
      "sfc": "Surface",
      "sondes": "Radiosondes",
      "ssmis_f17": "SSMIS DMSP-F17",
      "vadwind": "VAD Winds"
    }

    return ioda_platform_dictionary


# --------------------------------------------------------------------------------------------------


def find_instrument_from_string(full_string):

    # Get the platform dictionary
    ioda_platform_dictionary = ioda_platform_dict()

    # Set default outputs
    key = None
    variable = None

    # Loop over dictionary
    for key in ioda_platform_dictionary:
        if key in full_string:
            variable = ioda_platform_dictionary[key]
            return key, variable


# --------------------------------------------------------------------------------------------------


def ioda_platform_to_full_name(ioda_platform, logger):

    # Get the platform dictionary
    ioda_platform_dictionary = ioda_platform_dict()

    try:
        ioda_platform_out = ioda_platform_dictionary[ioda_platform]
    except Exception:
        ioda_platform_out = ioda_platform
        logger.info('\''+ioda_platform+'\' is not in the ioda platform dictionary')

    return ioda_platform_out


# --------------------------------------------------------------------------------------------------


def ioda_group_dict(ioda_group, logger):

    ioda_group_dictionary = {
      "omb": "Observation minus h(x)",
      "hofx": "Simulated observation, h(x)",
      "ObsValue": "Observation value",
      "GsiHofX": "GSI simulated observation, h(x)",
      "Gsiomb": "GSI observation minus h(x)",
      "GsiHofXBc": "GSI simulated observation, h(x), bias corrected",
      "GsiombBc": "GSI observation minus h(x), bias corrected"
    }

    try:
        ioda_group_out = ioda_group_dictionary[ioda_group]
    except Exception:
        logger.abort('\''+ioda_group+'\' is not in the ioda group dictionary')

    return ioda_group_out


# --------------------------------------------------------------------------------------------------
