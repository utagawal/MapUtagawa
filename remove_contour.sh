#!/bin/bash

for d in */ ; do
    if [[ "$d" == "carte_"* ]]; then
        cd $d
        rm *.img
        rm *.osm.gz
        cd ..
    fi
done