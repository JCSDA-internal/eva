import os
import pathlib
import pytest
from eva import eva_base
from unittest.mock import patch

# local imports
from eva.utilities.logger import Logger
from eva.tests import helpers


EVA_TESTS_DIR = pathlib.Path(__file__).parent.resolve()
PYTEST_ENVVARS = {
    'EVA_TESTS_DIR': str(EVA_TESTS_DIR)
}

OBS_CORRELATION_SCATTER_YAML = os.path.join(
    EVA_TESTS_DIR, 'config/ObsCorrelationScatterDriver.yaml')

# redirect load_yaml_file from eva_base to helpers
eva_base.load_yaml_file = helpers.load_yaml_file


def test_obs_correlation_scatter():
    # unit test meant to assure that the loop_and_create_and_run
    # method returns without errors when running the
    # ObsCorrelationScatter plot method with test data defined in
    # src/eva/tests/config/ObsCorrelationScatterDriver.yaml
    try:
        with patch.dict(os.environ, PYTEST_ENVVARS):
            eva_base.eva(OBS_CORRELATION_SCATTER_YAML)
    except Exception as e:
        raise ValueError(f'Unexpected error encountered: {e}')
