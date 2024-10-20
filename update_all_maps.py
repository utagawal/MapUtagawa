#!/usr/bin/python
import sys
import os
import subprocess
from scripts_hgt.get_hgt import get_hgt
from get_contours import get_contours
import os, shutil, fnmatch
import subprocess
import time
from multiprocessing import Pool
import pathlib


def task(country):
    country_name=country[0]
    id=country[1]
    style=country[2]
    url=country[3]
    if(not country_name.startswith('#')):
        print("Update "+country_name+ " "+id+" "+style+" "+url)
        country_dir =  "carte_"+country_name.replace(' ','_').lower()
        hasFiles=False
        for file in pathlib.Path(country_dir).glob("*.img"):
            if(str(file).split("/")[1].startswith("55")):
                hasFiles=True
        if(hasFiles==False):
            #Get contours
            get_contours(country_name, url)
        #Get contours
        get_contours(country_name, url)
        #Launch script
        subprocess.run(["bash", "download_osm.sh",country_name,id,style,url])
        subprocess.run(["bash", "create_map.sh",country_name,id,style])

if __name__ == '__main__':
    country_list=[]

    #File country
    file_in = open("country.txt", "rt")

    lines = file_in.readlines()
    for line in lines:
        result = line.split(";")
        country_list.append([result[0],result[1],result[2],result[3]])

    file_in.close()

    with Pool(processes=3) as pool:
        # call the function for each item in parallel
        pool.map(task, country_list)


