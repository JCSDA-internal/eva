from eva.utilities.logger import Logger
from eva.utilities.timing import Timing
from eva.data import data_driver
from eva.transforms import transform_driver
from eva.plot_tools import figure_driver


def eva(eva_config, eva_logger=None):

    # Create timing object
    timing = Timing()

    # Create temporary logger
    logger = Logger('EvaSetup')

    logger.info('Starting Eva')

    # Convert incoming config (either dictionary or file) to dictionary
    timing.start('Generate Dictionary')
    if isinstance(eva_config, dict):
        eva_dict = eva_config
    else:
        # Create dictionary from the input file
        eva_dict = load_yaml_file(eva_config, logger)

    # Get the list of applications
    try:
        diagnostic_configs = eva_dict['diagnostics']
    except KeyError:
        logger.abort('eva configuration must contain \'diagnostics\' and it should provide a ' +
                     'list of diagnostics to be run.')

    if not isinstance(diagnostic_configs, list):
        raise TypeError(f'diagnostics should be a list, it was type: {type(diagnostic_configs)}')
    timing.stop('Generate Dictionary')

    # Loop over the applications and run
    for diagnostic_config in diagnostic_configs:

        # Each diagnostic should have two dictionaries: data and graphics
        if not all(sub_config in diagnostic_config for sub_config in ['data', 'graphics']):
            msg = "diagnostic config must contain 'data' and 'graphics'"
            raise KeyError(msg)

        # Create the data collections
        # ---------------------------
        data_collections = DataCollections()

        # Prepare diagnostic data
        logger.info(f'Running data driver')
        timing.start('DataDriverExecute')
        data_driver(diagnostic_config, data_collections, timing, logger)
        timing.stop('DataDriverExecute')

        # Create the transforms
        if 'transforms' in diagnostic_config:
            logger.info(f'Running transform driver')
            timing.start('TransformDriverExecute')
            transform_driver(diagnostic_config, data_collections, timing, logger)
            timing.stop('TransformsDriverExecute')

        # Generate figure(s)
        logger.info(f'Running figure driver')
        timing.start('FigureDriverExecute')
        figure_driver(diagnostic_config, data_collections, timing, logger)
        timing.stop('FigureDriverExecute')

    timing.finalize()


# --------------------------------------------------------------------------------------------------


def main():

    # Arguments
    # ---------
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help='Configuration YAML file for driving ' +
                        'the diagnostic. See documentation/examples for how to configure the YAML.')

    # Get the configuation file
    args = parser.parse_args()
    config_file = args.config_file

    assert os.path.exists(config_file), "File " + config_file + " not found"

    # Run the diagnostic(s)
    eva(config_file)


# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------------
