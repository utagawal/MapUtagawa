#!/usr/bin/python
import sys
import os
import subprocess
import os, shutil, fnmatch
import subprocess
import time
from multiprocessing import Pool


def createMap(country):
    country_name=country[0]
    id=country[1]
    style=country[2]
    url=country[3]
    if(not country_name.startswith('#')):
        print("Update "+country_name+ " "+id+" "+style+" "+url)
        #Launch script
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
        pool.map(createMap, country_list)
