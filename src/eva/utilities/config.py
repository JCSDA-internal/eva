# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from eva.utilities.utils import load_yaml_file

# --------------------------------------------------------------------------------------------------
#  @package config
#
#  Class containing a config for tasks.
#
# --------------------------------------------------------------------------------------------------


class Config(dict):

    # ----------------------------------------------------------------------------------------------

    def __init__(self, dict_or_yaml, logger):

        # Copy of logger
        self.logger = logger

        # Program can recieve a dictionary or a yaml file
        if isinstance(dict_or_yaml, dict):
            self.config = dict_or_yaml
        else:
            self.config = load_yaml_file(dict_or_yaml, logger)

        # Initialize the parent class with the config
        super().__init__(self.config)

    # ----------------------------------------------------------------------------------------------

    def get(self, key, default=None):

        if default is None:

            if key in self.config:

                return super().get(key)

            else:

                self.logger.abort("Configuration does not have the key")

        else:

            return super().get(key, default)


# --------------------------------------------------------------------------------------------------


def get(dict, logger, key, default=None):

    if default is None:

        if key in dict:

            return dict.get(key)

        else:

            logger.abort(f'Configuration does not have the key {key}')

    else:

        return dict.get(key, default)


# --------------------------------------------------------------------------------------------------
