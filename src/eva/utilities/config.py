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

    """
    Class containing a configuration for tasks.
    """

    def __init__(self, dict_or_yaml, logger):

        """
        Initialize the Config object.

        Args:
            dict_or_yaml (dict or str): Either a dictionary containing configuration parameters
                                        or the path to a YAML file containing the configuration.
            logger: An instance of the logger to handle log messages.

        Returns:
            None
        """

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

    def get(self, key, default=None, abort_on_failure=True):

        """
        Get the value associated with a key from the configuration.

        Args:
            key (str): The key for which the value needs to be retrieved from the configuration.
            default: The default value to return if the key is not found in the configuration.
            abort_on_failure (bool): If True, aborts the program if the key is not found.

        Returns:
            The value associated with the key if found, otherwise the default value.
        """

        if default is None:

            if key in self.config:

                return super().get(key)

            elif abort_on_failure:

                self.logger.abort("Configuration does not have the key")

        else:
            return super().get(key, default)


# --------------------------------------------------------------------------------------------------


def get(dict, logger, key, default=None, abort_on_failure=True):

    """
    Get the value associated with a key from a given dictionary.

    Args:
        dict (dict): The dictionary from which the value needs to be retrieved.
        logger: An instance of the logger to handle log messages.
        key (str): The key for which the value needs to be retrieved from the dictionary.
        default: The default value to return if the key is not found in the dictionary.
        abort_on_failure (bool): If True, aborts the program if the key is not found.

    Returns:
        The value associated with the key if found, otherwise the default value.
    """

    if default is None:

        if key in dict:

            return dict.get(key)

        elif abort_on_failure:

            logger.abort(f'Configuration does not have the key {key}')

    else:
        return dict.get(key, default)


# --------------------------------------------------------------------------------------------------
