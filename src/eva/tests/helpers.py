import os
import re
import yaml

# local imports
from eva.utilities.logger import Logger


def envvar_constructor(loader, node):
    # method to help substitute parent directory for a yaml env var
    return os.path.expandvars(node.value)


def load_yaml_file(yaml_file, logger):
    # this yaml load function will allow a user to specify an environment
    # variable to substitute in a yaml file if the tag '!ENVVAR' exists
    # this will help developers create absolute system paths that are related
    # to the install path of the eva package.

    if logger is None:
        logger = Logger('Test Helpers')

    try:
        loader = yaml.SafeLoader
        loader.add_implicit_resolver(
            '!ENVVAR',
            re.compile(r'.*\$\{([^}^{]+)\}.*'),
            None
        )

        loader.add_constructor('!ENVVAR', envvar_constructor)
        yaml_dict = None
        with open(yaml_file, 'r') as ymlfile:
            yaml_dict = yaml.load(ymlfile, Loader=loader)

    except Exception as e:
        logger.trace('Eva diagnostics is expecting a valid yaml file, but it encountered ' +
                     f'errors when attempting to load: {yaml_file}, error: {e}')
        raise TypeError(f'Errors encountered loading  yaml file: {yaml_file}, error: {e}')

    return yaml_dict
