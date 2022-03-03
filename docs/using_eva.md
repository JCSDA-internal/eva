# Using Eva

Eva uses a dictionary/configuration API. This ensures flexible use for different applications. The
most straightforward use of Eva is achieved by passing it a YAML configuration file on the command
line:

```
	eva obs_correlation.yaml
```

Where the YAML must contain a list of the diagnostics to be used in the following format:

```
diagnostics:
  - diagnostic name: ObsCorrelationScatter
    ...
  - diagnostic name: ObsMapScatter
    ...
```

Eva can also be invoked from another Python module that passes it a dictionary (or a YAML path).
This is achieved as follows:

```
from eva.eva_base import eva

eva(eva_dict)
```

The dictionary must take the same hierarchy as shown above in the YAML file, i.e. with a list of
diagnostics to be run. Note that the calling routine can still pass a string with a path to the YAML
file if so desired.
