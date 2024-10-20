#!/bin/bash
echo "Download of the map $1 ...."

land=$1
id=$2
type=$3
url=$4

land_lower=$(echo $land | tr '[:upper:]' '[:lower:]')
land_lower=$(echo $land_lower | tr ' ' _ )
file="$land_lower".osm.pbf
if [[ "-latest.osm.pbf" == *"$url"* ]]; then
    url_poly=${url//-latest.osm.pbf/.poly}
else
    url_poly=${url//.pbf/.poly}    
fi

file_poly="$land_lower".poly

cd "carte_$land_lower"

curl -L -o $file $url

curl -L -o $file_poly $url_poly

cd ..