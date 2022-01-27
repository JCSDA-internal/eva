# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import numpy as np
import matplotlib.pyplot as plt


# --------------------------------------------------------------------------------------------------


def scatter_correlation_plot(data_a, data_b, data_a_label, data_b_label, plot_title, output_name,
                             marker_size=2):

    # Compute limits for the figure
    # -----------------------------
    data_min = min(min(data_a), min(data_b))
    data_max = max(max(data_a), max(data_b))
    data_dif = data_max - data_min

    # Compute correlation between two datasets
    # ----------------------------------------
    correlation = np.corrcoef(data_a, data_b)[0, 1]
    # TODO add this to the plot somewhere

    # Create figure
    # -------------
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.scatter(data_a, data_b, s=marker_size)
    plt.title(plot_title)

    # Figure labeling
    # ---------------
    plt.xlabel(data_a_label)
    plt.ylabel(data_b_label)
    ax.set_aspect('equal', adjustable='box')
    plt.xlim(data_min - 0.1*data_dif, data_max + 0.1*data_dif)
    plt.ylim(data_min - 0.1*data_dif, data_max + 0.1*data_dif)
    plt.axline((0, 0), slope=1.0, color='k')

    # Save figure
    # -----------
    plt.savefig(output_name)
    plt.close('all')
