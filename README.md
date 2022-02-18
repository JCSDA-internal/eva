
# Evaluation and Verification of the Analysis (EVA)

### Continuous integration:

| Test      | Status  |
| --------- | --------|
| Python coding norms | ![Status](https://github.com/danholdaway/eva/actions/workflows/codestyle.yml/badge.svg) |

### Licence:

(C) Copyright 2021-2022 United States Government as represented by the Administrator of the National
Aeronautics and Space Administration. All Rights Reserved.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


### Installation

The eva package can be installed using pip:

	pip install --prefix=/path/to/install/ .

### Usage

eva uses a strict dictionary/configuration only API. This ensures flexible use for different applications. The most straightforward use of eva is achieved by passing it a yaml configuration file on the command line:

	eva obs_correlation.yaml

Where the yaml must contain a list of the diagnostics to be used in the following format:

```
diagnostics:
  - diagnostic name: ObsCorrelationScatter
    ...
  - diagnostic name: ObsMapScatter
    ...
```

eva can also be invoked from another Python module that passes it a dictionary, rather than a Yaml file that is later translated into a dictionary. This is achieved as follows:

```
from eva.eva_base import eva

eva(eva_dict)
```

The dictionary must take the same hierarchy as shown above in the Yaml file, i.e. with a list of diagnostics to be run. Note that the calling routine can still pass a string with a path to the Yaml file if so desired.

Note that eva can also be invoked within Jupyter notebooks using the above API.
