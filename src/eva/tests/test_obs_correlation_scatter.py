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

logger = Logger('UnitTests')


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


def test_obs_correlation_scatter__bad_config_type():

    with pytest.raises(TypeError):
        eva_base.eva([])

    with pytest.raises(TypeError):
        eva_base.eva(1234)

    with pytest.raises(TypeError):
        eva_base.eva(eva_base)

    with pytest.raises(TypeError):
        eva_base.eva('foo')


def test_obs_correlation_scatter__bad_config_dict():

    with pytest.raises(TypeError):
        test_config = {'diagnostics': 'bar'}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    with pytest.raises(TypeError):
        test_config = {'diagnostics': {'diagnostic name': []}}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    with pytest.raises(SystemExit):
        eva_base.eva({'foo': 'bar'})

    with pytest.raises(KeyError):
        test_config = {'diagnostics': [{'foo': 'bar'}]}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    with pytest.raises(TypeError):
        test_config = {'diagnostics': [{'diagnostic name': 1234}]}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    with pytest.raises(TypeError):
        test_config = {'diagnostics': [{'diagnostic name': {}}]}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    with pytest.raises(TypeError):
        test_config = {'diagnostics': [{'diagnostic name': []}]}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    with pytest.raises(ValueError):
        test_config = {'diagnostics': [{'diagnostic name': '1234'}]}
        logger.info(f'Testing eva_base.eva with config: {test_config}')
        eva_base.eva(test_config)

    all_printable_chars = [chr(i) for i in range(128)]
    for char in all_printable_chars:
        if char.isalpha():
            continue

        name_str = 'foo' + char

        with pytest.raises(ValueError):
            test_config = {'diagnostics': [{'diagnostic name': name_str}]}
            logger.info(f'Testing eva_base.eva with config: {test_config}')
            eva_base.eva(test_config)
