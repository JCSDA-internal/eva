# Using EVA with Cubed-Sphere Restart Files

EVA can be used to read cubed-sphere restart files and produce analysis plots. [EMCPy](https://github.com/NOAA-EMC/emcpy) plotting techniques now includes features that can stitch all six cubed-sphere tiles and produce a global view figure. 

## Steps to run and generate plots:

Locate *.nc file(s) and construct a .yaml file with the following specific components. Examples can be found in [`eva/src/eva/tests/config`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/tests/config).

### Specify data type

```
- data:
    type: CubedSphereRestart
```

CubedSphereRestart indicates which data parsing routine is to be used.  The available options are the file names in [`eva/src/eva/data`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/data).  Note the file names are expected in camel case in the yaml file, despite the snake_case used for the Python file names.

### Data specifications

```
datasets:
  - name: experiment
    variable: T
    resolution: C48
    fv3_filenames:
      - ${data_input_path}/20210323.150000.sfc_data.tile1.nc
      - ${data_input_path}/20210323.150000.sfc_data.tile2.nc
      - ${data_input_path}/20210323.150000.sfc_data.tile3.nc
      - ${data_input_path}/20210323.150000.sfc_data.tile4.nc
      - ${data_input_path}/20210323.150000.sfc_data.tile5.nc
      - ${data_input_path}/20210323.150000.sfc_data.tile6.nc
    orog_filenames:
      - ${data_input_path}/C48_oro_data.tile1.nc
      - ${data_input_path}/C48_oro_data.tile2.nc
      - ${data_input_path}/C48_oro_data.tile3.nc
      - ${data_input_path}/C48_oro_data.tile4.nc
      - ${data_input_path}/C48_oro_data.tile5.nc
      - ${data_input_path}/C48_oro_data.tile6.nc
```

Two data type files need to be included in the input .yaml file; `fv3_filenames` which are the cubed-sphere restart files and `orog_filenames` which are cubed-sphere orographic files. The above code can be found in [`eva/src/eva/tests/config/testCubedSphereRestart.yaml`](https://github.com/JCSDA-internal/eva/blob/develop/src/eva/tests/config/testCubedSphereRestart.yaml) and uses an example to plot all six cubed-sphere tiles. The variable `resolution` must also match the resolution of the data being used or the code will report an error.

### Specify Groups and Data Variables

```
groups:
  - name: FV3Restart
    variables: &variables [geolon,
                           geolat,
                           t2m]

```

This portion of the .yaml file points to the data variables to be extracted from the inputted .nc file(s).

### Plots

Data may be plotted using any of the available plot types. Examples of plot types can be found in [`eva/src/eva/tests/config`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/tests/config) under the `graphics` sub-section of all configuration file examples.