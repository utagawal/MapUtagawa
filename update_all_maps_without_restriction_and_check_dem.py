#!/usr/bin/python
import sys
import os
import subprocess
from get_contours import get_contours
import os, shutil, fnmatch
import subprocess
import time
import pathlib
from multiprocessing import Pool

def task(country):
    country_name=country[0].replace("#",'')
    id=country[1]
    style=country[2]
    url=country[3]
    hasFiles=False
    print("Update "+country_name+ " "+id+" "+style+" "+url)
    country_dir =  "carte_"+country_name.replace(' ','_').lower()
    for file in pathlib.Path(country_dir).glob("*.img"):
        if(str(file).split("/")[1].startswith("9")):
            hasFiles=True
    if(hasFiles==False):
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

    with Pool(processes=1) as pool:
        # call the function for each item in parallel
        pool.map(task, country_list)

