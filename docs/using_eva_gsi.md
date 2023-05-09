# Using EVA for GSI

EVA can be used to read GSI diagnostic netCDF4 files and produce analysis plots. These capabilities extend to be used for conventional and radiance data types.

## Steps to run and generate plots:

Locate *.nc4 file(s) and construct a .yaml file with the follwoing specific components. Examples can be found in [`eva/src/eva/tests/config`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/tests/config).

### Specify data type

```
- data:
    type: GsiObsSpace
```

GsiObsSpace indicates which data parsing routine is to be used.  The available options are the file names in [`eva/src/eva/data`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/data).  Note the file names are expected in camel case in the yaml file, despite the snake_case used for the python file names.

### Data specifications

#### Conventional Data
```
datasets:
  - name: experiment
    variable: t
    filenames:
      - ${data_input_path}/gsi_obs_space.conv_t_ges.2020092000.nc4
```

The portion of code above points to a sample file found in [`eva/src/eva/tests/data`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/tests/data). It is a conventional temperature (t) file, and only needs the variable input.

#### Radiance Data
```
datasets:
  - name: experiment
    satellite: metop-a
    sensor: amsua
    filenames:
      - ${data_input_path}/gsi_obs_space.amsua_metop-a_ges.2020092200.nc4
    channels: &channels 3,8
```

If using radiance data, it is important to include the `satellite`, `sensor`, and `channels` of interest. The portion of code above is also in [`eva/src/eva/tests/data`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/tests/data), and grabs data from just channels 3 and 8. The user can also include a list of channels as shown in the sample configuration file for IASI Metop-A found in [`eva/src/eva/tests/config/testIodaObsSpaceIASI_Metop-A.yaml`](https://github.com/JCSDA-internal/eva/blob/develop/src/eva/tests/config/testIodaObsSpaceIASI_Metop-A.yaml).

```
channels: [16, 29, 32, 35, 38, 41, 44, 47, 49, 50, 51, 53, 55, 56, 57, 59, 61, 62, 63, 66, 68,
           70, 72, 74, 76, 78, 79, 81, 82, 83, 84, 85, 86, 87, 89, 92, 93, 95, 97, 99, 101, 103,
           104, 106, 109, 110, 111, 113, 116, 119, 122, 125, 128, 131, 133, 135, 138, 141, 144,
           146, 148, 150, 151, 154, 157, 159, 160, 161, 163, 167, 170, 173, 176, 179, 180, 185,
           187, 191, 193, 197, 199, 200, 202, 203, 205, 207, 210, 212, 213, 214, 217, 218, 219,
           222, 224, 225, 226, 228, 230, 231, 232, 236, 237, 239, 243, 246, 249, 252, 254, 259,
           260, 262, 265, 267, 269, 275, 279, 282, 285, 294, 296, 299, 300, 303, 306, 309, 313,
           320, 323, 326, 327, 329, 332, 335, 345, 347, 350, 354, 356, 360, 363, 366, 371, 372,
           373, 375, 377, 379, 381, 383, 386, 389, 398, 401, 404, 405, 407, 408, 410, 411, 414,
           416, 418, 423, 426, 428, 432, 433, 434, 439, 442, 445, 450, 457, 459, 472, 477, 483,
           509, 515, 546, 552, 559, 566, 571, 573, 578, 584, 594, 625, 646, 662, 668, 705, 739,
           756, 797, 867, 906, 921, 1027, 1046, 1090, 1098, 1121, 1133, 1173]
```

If the user wants to include consecutive channels, they can do so by specifying the range of channels as shown below:

```
channels: 1-15
```

### Specify Groups and Data Variables

```
groups:
  - name: GsiNcDiag
    variables: &variables [Obs_Minus_Forecast_adjusted,
                           Observation,
                           Latitude,
                           Longitude]
```

This portion of the .yaml file points to the data variables to be extracted from the inputted .nc4 file(s).

### Plots

Data may be plotted using any of the available plot types. Examples of plot types can be found in [`eva/src/eva/tests/config`](https://github.com/JCSDA-internal/eva/tree/develop/src/eva/tests/config) under the `graphics` sub-section of all configuration file examples.
