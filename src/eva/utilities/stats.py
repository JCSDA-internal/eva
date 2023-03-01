# (C) Copyright 2021-2022 NOAA/NWS/EMC
#
# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


'''
stats.py contains statistics utility functions
'''

__all__ = ['lregress', 'ttest', 'get_weights', 'get_weighted_mean',
           'get_linear_regression', 'bootstrap', 'stats_helper']

import numpy as _np
from scipy.stats import t as _t
from sklearn.linear_model import LinearRegression

from eva.utilities.utils import slice_var_from_str


# --------------------------------------------------------------------------------------------------


def stats_helper(logger, plot_obj, data_collections, config):
    """
    Add specified statistics to a plot
    Args:
        logger : logging object
        plotobj : declarative plotting object
        data_collections : eva data collections object
        config : input configuration dictionary
    """

    print(config)

    # List of data to make stats for
    fields = config['fields']

    # List of statistics to include
    statistics_variables = config['statistics_variables']

    # Rounding
    digits = config.get('round', 4)

    # Loop over fields and assemble statistics as a string
    for field in fields:

        # Field name
        field_name = field['field_name']

        # Get collection, group, variable name for field
        var_cgv = field_name.split('::')
        if len(var_cgv) != 3:
            logger.abort('In stats_helper the variable \'var_cgv\' does not appear to ' +
                         'be in the required format of collection::group::variable.')

        # Optionally get the channel to plot
        channel = None
        if 'channel' in field:
            channel = field['channel']

        # Get the field data
        field_data = data_collections.get_variable_data(var_cgv[0], var_cgv[1], var_cgv[2], channel)

        # See if we need to slice data
        field_data = slice_var_from_str(field, field_data, logger)

        # Flatten and mask missing data
        field_data = field_data.flatten()
        mask = ~_np.isnan(field_data)
        field_data = field_data[mask]

        # Start stats string
        stats_string = field_name + '| '

        # Loop over statistics list and assemble string
        for statistics_variable in statistics_variables:

            if statistics_variable in ['n']:
                stat_value = len(field_data)
            elif statistics_variable in ['min', 'max', 'mean', 'median', 'std', 'var']:
                stat_value = eval(f'_np.nan{statistics_variable}(field_data)')
                stat_value = eval(f'_np.round(stat_value, {digits})')
            else:
                logger.abort(f'In stats_helper the statistic {statistics_variable} is not supported.')

            stats_string = stats_string + f'{statistics_variable}: {stat_value} | '

        # Start new line for next data
        stats_string = stats_string + '\n'

    # Get the location for the annotation
    x_loc = config.get('xloc', 0)
    y_loc = config.get('yloc', 0)

    # Get any additional kwargs
    kwargs = config.get('kwargs', {})

    # call plot object method
    plot_obj.add_text(x_loc, y_loc, stats_string, **kwargs)


# --------------------------------------------------------------------------------------------------


def lregress(x, y, ci=95.0):
    '''
    Function that computes the linear regression between two variables and
    returns the regression coefficient and statistical significance
    for a t-value at a desired confidence interval.
    Args:
        x : (array like) independent variable
        y : (array like) dependent variable
        ci : (float, optional, default=95) confidence interval percentage
    Returns:
        The linear regression coefficient (float),
        the standard error on the linear regression coefficient (float),
        and the statistical signficance of the linear regression
        coefficient (bool).
    '''

    # make sure the two samples are of the same size
    if (len(x) != len(y)):
        raise ValueError('samples x and y are not of the same size')
    else:
        nsamp = len(x)

    pval = 1.0 - (1.0 - ci / 100.0) / 2.0
    tcrit = _t.ppf(pval, 2 * len(x) - 2)

    covmat = _np.cov(x, y=y, ddof=1)
    cov_xx = covmat[0, 0]
    cov_yy = covmat[1, 1]
    cov_xy = covmat[0, 1]

    # regression coefficient (rc)
    rc = cov_xy / cov_xx
    # total standard error squared (se)
    se = (cov_yy - (rc**2) * cov_xx) * (nsamp - 1) / (nsamp - 2)
    # standard error on rc (sb)
    sb = _np.sqrt(se / (cov_xx * (nsamp - 1)))
    # error bar on rc
    eb = tcrit * sb

    ssig = True if (_np.abs(rc) - _np.abs(eb)) > 0.0 else False

    return rc, sb, ssig


# --------------------------------------------------------------------------------------------------


def ttest(x, y=None, ci=95.0, paired=True, scale=False):
    '''
    Given two samples, perform the Student's t-test and return the errorbar.
    The test assumes the sample size be the same between x and y.
    Args:
        x: (numpy array) control
        y: (numpy array, optional, default=x )experiment
        ci: (float, optional, default=95) confidence interval percentage
        paired: (bool, optional, default=True) paired t-test
        scale: (bool, optional, default=False) normalize with mean(x) and
               return as a percentage
    Returns:
        The (normalized) difference in the sample means and
        the (normalized) errorbar with respect to control.
    To mask out statistically significant values:\n
    `diffmask = numpy.ma.masked_where(numpy.abs(diffmean)
                                      <=errorbar,diffmean).mask`
    '''

    nsamp = x.shape[0]

    if y is None:
        y = x.copy()

    pval = 1.0 - (1.0 - ci / 100.0) / 2.0
    tcrit = _t.ppf(pval, 2*(nsamp-1))

    xmean = _np.nanmean(x, axis=0)
    ymean = _np.nanmean(y, axis=0)

    diffmean = ymean - xmean

    if paired:
        # paired t-test
        std_err = _np.sqrt(_np.nanvar(y-x, axis=0, ddof=1) / nsamp)
    else:
        # unpaired t-test
        std_err = _np.sqrt((_np.nanvar(x, axis=0, ddof=1) +
                            _np.nanvar(y, axis=0, ddof=1)) / (nsamp-1.))

    errorbar = tcrit * std_err

    # normalize (rescale) the diffmean and errorbar
    if scale:
        scale_fac = 100.0 / xmean
        diffmean = diffmean * scale_fac
        errorbar = errorbar * scale_fac

    return diffmean, errorbar


# --------------------------------------------------------------------------------------------------


def get_weights(lats):
    '''
    Get weights for latitudes to do weighted mean
    Args:
        lats: (array like) Latitudes
    Returns:
        An array of weights for latitudes
    '''
    return _np.cos((_np.pi / 180.0) * lats)


# --------------------------------------------------------------------------------------------------


def get_weighted_mean(data, weights, axis=None):
    '''
    Given the weights for latitudes, compute weighted mean
    of data in that direction
    Note, `data` and `weights` must be same dimension
    Uses `numpy.average`
    Args:
        data: (numpy array) input data array
        weights: (numpy array) input weights
        axis: (int) direction to compute weighted average
    Returns:
        An array of data weighted mean by weights
    '''
    assert data.shape == weights.shape, (
        'data and weights mis-match array size')

    return _np.average(data, weights=weights, axis=axis)


# --------------------------------------------------------------------------------------------------


def get_linear_regression(x, y):
    """
    Calculate linear regression between two sets of data.
    Fits a linear model with coefficients to minumize the
    residual sum of squares between the observed targets
    in the dataset, and the targets predicted by the linear
    approximation.
    Args:
        y, x : (array like) Data to calculate linear regression
    Returns:
        The predicted y values from calculation,
        the R squared value, the intercept of the line, and the
        slope of the line from the equation for the predicted
        y values.
    """
    x = x.reshape((-1, 1))
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)
    intercept = model.intercept_
    slope = model.coef_[0]
    # This is the same as if you calculated y_pred
    # by y_pred = slope * x + intercept
    y_pred = model.predict(x)
    return y_pred, r_sq, intercept, slope


# --------------------------------------------------------------------------------------------------


def bootstrap(insample, level=.95, estimator='mean', nrepl=10000):
    """
    Generate emprical bootstrap confidence intervals.
    See https://ocw.mit.edu/courses/mathematics/
                18-05-introduction-to-probability-and-statistics-spring-2014/
                readings/MIT18_05S14_Reading24.pdf for more information.
    Args:
        insample: (array like) is the array from which the estimator (u)
                  was derived (x_1, x_2,....x_n).
        level: (float, default=0.95) desired confidence level for CI bounds
        estimator: (char, default='mean') type of statistic obtained from
                  the sample (mean or median)
        nrepl: (integer, default=1000) number of replicates
    Returns:
        Lower and upper bounds of confidence intervals
    """
    if any(_np.isnan(insample)):
        print('bootstrap_ci.py: NaN detected. Dropping NaN(s) input prior to bootstrap...')
        sample = insample[~_np.isnan(insample)]
    else:
        sample = insample

    boot_dist = [_np.random.choice(sample, _np.size(sample)) for x in _np.arange(nrepl)]
    if estimator.lower() == 'mean':
        deltas = _np.sort(_np.mean(boot_dist, axis=1) - _np.mean(sample))
    elif estimator.lower() == 'median':
        deltas = _np.sort(_np.median(boot_dist, axis=1) - _np.median(sample))

    lower_pctile = 100*((1. - level)/2.)
    upper_pctile = 100. - lower_pctile
    ci_lower = _np.percentile(deltas, lower_pctile)
    ci_upper = _np.percentile(deltas, upper_pctile)

    return ci_lower, ci_upper


# --------------------------------------------------------------------------------------------------
