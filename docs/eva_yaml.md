# EVA yaml files

EVA uses yaml formatted files to load data, make transformations to the data, and generate plots.  YAML is a human-readable data-serialization language.  It is written with a .yml or .yaml (preferred) file extension.

Examples of working yaml files can be found at `eva/src/eva/tests/config`.  

EVA expects to find This at the top of the yaml file and un-indented:

```
diagnostics:
```

The terminating colon indicates a key-value pair analagous to a python dicationary format.  

Next the file should contain `- data:`.  The `-` indicates a list element, and data is a another key-value pair.  Like `diagnostics:` preceeding it, this line is not indented.

This must be followed with a type:

```
- data:
    type: MonDataSpace
```

The type line is indented 4 spaces.

The value associated with type corresponds to the data parsing object defined in `eva/src/eva/data`.  Note that EVA expects camel case in the yaml file and maps that to file names in "snake_case", so MonDataSpace indicates the use of `eva/src/eva/data/mon_data_space.py`.

Next is the datasets declaration:

```
    datasets:
      - name: experiment
        filenames:
           - ../data/ioda_ops_space.amsua_n19.hofx.2020-12-14T210000Z.nc4
        channels: &channels 3,8
        groups:
          - name: ObsValue
            variables: &variables [brightnessTemperature]
          - name: GsiHofXBc
          - name: hofx
          - name: EffectiveQC
          - name: MetaData
```

Filenames indicates the data files to be loaded.  The path may be relative or absolute.  Test files in `eva/src/eva/tests/config` will contain `${data_input_path}` as the file location.  Know this only works with the continuious integration tests and will not work from the command line.  It must be replaced with the filepath.

Next is  the channel specification.  This indicates which channel(s) are to be included in the dataset.  The `&channels` is termed an anchor.  Wherever `*channels` is used later in the file it will be replaced with that which follows the anchor declaration -- 3 and 8 in this case. 

```
        channels: &channels 3,8
```

The several `name:` keys specify group names.  

The `variables: &variables [brightnessTemperature]` is a bit special.  The `&variables` is an anchor.  Wherever `*variables` is used later in the file it will be replaced with that which is in the braces `[brightnessTemperature]`.

Next are transforms.  Transforms are not required.  They are a means to modify the dataset.  Currently the available transforms include `accept where`, `arithmetic`, `channel stats`, and `select time`.  

Here is an example transform:

```
  transforms:
    - transform: arithmetic
      new name: experiment::ObsValueMinusGsiHofXBc::${variable}
      equals: experiment::ObsValue::${variable}-experiment::GsiHofXBc::${variable}
      for:
        variable: *variable
```

Again the `*variable` string is substituted for the anchor declaration so brightnessTemperature will be used.  A new variable, brightnessTemperature in group ObsValueMinusGsiHofXBc will be created by subtracting brightnessTemperature in group GsiHofXBc from brightnessTemperature in group ObsValue.

There is no limit to the number of transforms in a yaml file.  

The final component in the yaml file is graphics.  

```
  graphics:
    - figure:
        layout: [1,1]
        title: 'Some title string'
        output name: lineplots/dir/my_plot.png
      plots:
        - add_xlabel: 'Observation Value'
          add_ylable: 'Gsi h(x)'
          add legend: 
            loc: 'upper left'
          layers:
          - type: Scatter
            x: 
              variable: experiment::ObsValue::${variable}
            y:
              variable: experiment::GsiHofXBc::${variable}
            color: 'black'
            label: 'GSI h(x) versus obs (all obs)'
```

This will generate a scatter plot. 
