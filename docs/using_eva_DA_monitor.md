# Using EVA for DA Monitoring Plots

EVA can be used to produce plots similar to those produced by the GSI DA Monitor package (https://github.com/NOAA-EMC/GSI-Monitor).   

Note that there are 4 distinct monitors:  Radiance (RadMon), Ozone (OznMon), GSI minimization (MinMon), and Conventional (ConMon).  All of these produce interim data storage files (*.ieee_d) in (fortran) binary format as well as control files (*.ctl), which describe the contents of the data files.

Steps to generate a plot:

Locate *.ieee_d file(s) and associated control (*.ctl) file.  
Construct a .yaml file with the following specific components.  Examples can be found in `eva/src/eva/tests/config`.

1. Specify data type.


```
- data:
    type: MonDataSpace

```

MonDataSpace indicates which data parsing routine is to be used.  The available options are the file names in `eva/src/eva/data`.  Note the file names are expected in camel case in the yaml file, despite the snake_case used for the python file names.

2. File control and data specifications


```
datasets:
  - name: experiment
   control_file:
     - ../data/time.hirs4_metop-a.ctl
   filenames:
     - ../data/time.hirs4_metop-a.2015051418.ieee_d
     - ../data/time.hirs4_metop-a.2015051500.ieee_d
```

When EVA loads the data files all the variables in the control file will be added to the dataset.  Additionally `cycle` will be added as a variable, as will `scan` (scan angle) if specified as a dimension in the control file.

3. Desired transforms. Any of the available transforms may be applied, but of particular note is the `select time` transform:


```
    - transform: select time
      new name: experiment::GsiIeee::count2
      starting field: experiment::GsiIeee::count
      cycle: 2015051500
```

This may be used to construct a subset of the data by single cycle or multiple cycles covering a time span.

4. Plots.  Data may be plotting using any of the available plot types.  Typically these are `Lineplot` and `Histogram` types.
