#!/usr/bin/python
import sys
import urllib.request
import os
import os.path
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import shutil

def get_hgt(country_name, url_poly):
    print("Calculation in progress "+url_poly)
    hgt_list=set()
    point_list=list()

    file = urllib.request.urlopen(url_poly)
    polygon = file.read().decode('utf8')
    for line in polygon.splitlines():
        if(line=='END') :
            break
        if(line!='none' and line!='1'):
            split = line.split("   ")
            longitude_string = split[1]
            latitude_string = split[2]
            
            point_list.append(Point(float(longitude_string),float(latitude_string)))
            

    polygon = Polygon(point_list)
    hgt_list=list()
    for x in range(-180, 180):
        for y in range(90, -90, -1):
            poly_hgt = Polygon([(x,y),(x+1,y),(x+1,y+1),(x,y+1)])
            if(poly_hgt.intersects(polygon)):
                hgt_list.append(Point(x,y))
                
    os.makedirs("dem/"+country_name+"/", exist_ok=True)
    urls=[]
    for hgt in hgt_list:
        longitude = int(hgt.x)
        latitude = int(hgt.y)
        
        if ( longitude>= 0 ):
            longitude_export="E{:03d}".format(longitude)
        else:
            longitude_export="W{:03d}".format(abs(longitude)) 

        if ( latitude>= 0 ):
            latitude_export="N{:02d}".format(latitude)
        else:
            latitude_export="S{:02d}".format(abs(latitude)) 
        file = latitude_export+longitude_export+".SRTMGL1.hgt.zip"
        if ( os.path.isfile("dem/lidar_europe/"+latitude_export+longitude_export+".hgt")): 
            shutil.copy("dem/lidar_europe/"+latitude_export+longitude_export+".hgt", "dem/"+country_name+"/"+latitude_export+longitude_export+".hgt")
        if ( not os.path.isfile("dem/"+country_name+"/"+latitude_export+longitude_export+".hgt")):   
            urls.append("https://e4ftl01.cr.usgs.gov//DP133/SRTM/SRTMGL1.003/2000.02.11/"+file)

    if(len(urls)>0):
        file_out = open("dem/"+country_name+"/hgt_urls.txt", "wt")
        file_out.write("\n".join(urls)+"\n")
        file_out.close()   

if __name__ == '__main__':
    country_name=sys.argv[1]
    url_poly=sys.argv[2]
    get_hgt(country_name, url_poly)