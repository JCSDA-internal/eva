#!/bin/bash

# Run this script in the directory with observation files that need upgrading

export build=/discover/nobackup/drholdaw/JediDev/develop/build-intel-release
source $build/modules
export code=/discover/nobackup/drholdaw/JediDev/develop/

# paths to the upgrader and upgrader configuration (make sure to use feature/sprint-ioda-converters branches)
export upgrader=$build/bin/ioda-upgrade-v2-to-v3.x
export config=$code/ioda/share/ioda/yaml/validation/ObsSpace.yaml

for f in ioda_obs_space.*.nc4
do
    echo "Updating " $f
    $upgrader $f $f.new $config
    # Check for success
    if [ $? -eq 0 ]; then
        echo "Updating of " $f " was successful"
        mv $f.new $f
    else
        echo "Updating of " $f " failed"
        exit 1
    fi

done
exit 0
for f in *.nc
do
    echo "Updating " $f
    $upgrader $f $f.new $config
    # Check for success
    if [ $? -eq 0 ]; then
        echo "Updating of " $f " was successful"
        mv $f.new $f
    else
        echo "Updating of " $f " failed"
        exit 1
    fi
done
