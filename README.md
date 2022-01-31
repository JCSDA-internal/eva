# Evaluation and Verification of the Analysis (EVA)


## Installation

The eva package can be installed using pip:

	pip install --prefix=/path/to/install/ .

## Usage

eva uses a strict dictionary only API. This ensures flexible use for different applications. The most straightforward use is achieved by choosing the Class containing the diagnostic and passing a yaml configuration file:

	eva ObsCorrelationScatter obs_correlation.yaml

Alternatively you can invoke eva passing the class name within the yaml configuration:

	eva obs_correlation.yaml

Where the yaml must contain a list of the diagnostics to be used:

```
applications:
  - application name: ObsCorrelationScatter
    ...
  - application name: ObsMapScatter
    ...
```

eva can also be invoked from another Python module that passes a dictionary, rather than a Yaml file that is later translated into a dictionary. This is achieved as follows:

```
from eva.base import create_and_run

create_and_run("ObsCorrelationScatter", eva_dict)
```

Note that this also allows for use of eva within Jupyter notebooks.
