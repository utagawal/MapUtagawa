#!/bin/bash

start_time="$(date +%s)"
d=`date "+%d.%m.%Y"`

time_task () {
   T="$(($(date +%s)-start_time))"
   D=$((T/60/60/24))
   H=$((T/60/60%24))
   M=$((T/60%60))
   S=$((T%60))
   time_display=""
   if [ $D -gt 0 ];then
      time_display="${time_display}${D} days "
   fi
   if [ $H -gt 0 ];then
      time_display="${time_display}${H} hours "
   fi
   if [ $M -gt 0 ];then
      time_display="${time_display}${M} minutes "
   fi
   time_display="${time_display}${S} seconds "

   echo "Finished in ${time_display}"
}

echo "Map creation : $1 ...."

land=$1
id=$2
type=$3

land_lower=$(echo $land | tr '[:upper:]' '[:lower:]')
land_lower=$(echo $land_lower | tr ' ' _ )
land_without_space=$(echo $land | tr ' ' _ )
file="$land_lower".osm.pbf
poly="$land_lower".poly
type_upper="$(tr '[:lower:]' '[:upper:]' <<< ${type:0:1})${type:1}"

cd "carte_$land_lower"

name="Map${type_upper} ${land} ${d%%}"
mapname="77$id"
mapname_courbes="88$id"
name_file=Map${type_upper}_${land_without_space}_


count=`ls -1 *.osm.gz 2>/dev/null | wc -l`
if [ $count != 0 ];then
   rm *.img 
   echo "Split contour ...."
   
   java -Xmx16384m -jar ../splitter/splitter.jar --mapid=${mapname_courbes}0000 --max-nodes=2000000 --polygon-file=${poly} --keep-complete=false *.osm.gz

   mv template.args courbes.args
 
   echo "Creation of the map courbes ...."
   java -Xmx16384m -jar ../mkgmap/mkgmap.jar -c ../options_courbes.args -c courbes.args

   rm ${mapname_courbes}*.osm.pbf
   rm areas.list
   rm areas.poly
   rm courbes.args
   rm none-areas.poly
   rm none-template.args
   rm densities-out.txt
   rm osmmap.img
   rm osmmap.tdb
   rm *.osm.gz
fi   


if [ ! -f "${mapname}.osm.pbf" ]; then
   echo "***** Split OSM file ...."

   java -Xmx16384m -jar ../splitter/splitter.jar --mapid=${mapname}0000 --max-nodes=2000000 --keep-complete=true --route-rel-values=foot,hiking,bicycle --overlap=0 ${file}

   mv template.args map.args
fi

   echo "***** Compile Garmin img ...."
java -Xmx16384m -jar ../mkgmap/mkgmap.jar -c ../options_${type}.args -c map.args

if [ -f "${mapname_courbes}0000.img" ]; then
   java -Xmx16384m -jar ../mkgmap/mkgmap.jar --mapname=${mapname}0000 --family-id=${mapname} --family-name="MapUtagawa ${land}" --series-name="MapUtagawa ${land} ${d%%}" --description="MapUtagawa (${name})" -c ../options_${type}.args --gmapsupp ../style/${type}.typ ${mapname}*.img ${mapname_courbes}*.img
else
   java -Xmx16384m -jar ../mkgmap/mkgmap.jar --mapname=${mapname}0000 --family-id=${mapname} --family-name="MapUtagawa ${land}" --series-name="MapUtagawa ${land} ${d%%}" --description="MapUtagawa (${name})" -c ../options_${type}.args --gmapsupp ../style/${type}.typ ${mapname}*.img
fi

echo "***** Create installer ...."
echo "***** Retrieving TYP style file ...."
cp ../style/${type}.typ ./${type}.typ
echo "** Change compression method... "
sed -i 's_SetCompressor /SOLID lzma_SetCompressor /SOLID zlib_g' ./osmmap.nsi
makensis -V4 ./osmmap.nsi

   echo "***** Cleanup files ...."
 # rm x${type}.typ
 # rm ${mapname}*.img 
 rm ${mapname}*.osm.pbf
 rm areas.list
 rm areas.poly
 rm map.args
 rm densities-out.txt
 # rm osmmap.img
 # rm osmmap.tdb
 # rm osmmap.nsi
 
 rm -f /var/data/garminmaps/UtagawaVTTmap/${land_without_space}/${name_file}*

dm=`date "+%Y_%m_%d"`

mkdir /var/data/garminmaps/UtagawaVTTmap/${land_without_space}

# zip /var/data/garminmaps/UtagawaVTTmap/${land_without_space}/${name_file}${dm}.zip gmapsupp.img

mv -f gmapsupp.img /var/data/garminmaps/UtagawaVTTmap/${land_without_space}/${name_file}latest.img
mv -f "MapUtagawa ${land}.exe" /var/data/garminmaps/UtagawaVTTmap/${land_without_space}/MapUtagawa_${land_without_space}_${d%%}.exe

time_task

cd ..