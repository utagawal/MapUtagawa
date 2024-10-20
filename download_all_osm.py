#!/usr/bin/python
import sys
import os
import subprocess
import os, shutil, fnmatch
import subprocess
import time
from multiprocessing import Pool


def task(country):
    country_name=country[0].replace("#",'')
    id=country[1]
    style=country[2]
    url=country[3]
    #if(not country_name.startswith('#')):
    print("Update "+country_name+ " "+id+" "+style+" "+url)
    #Launch script
    subprocess.run(["bash", "download_osm.sh",country_name,id,style,url])

if __name__ == '__main__':
    country_list=[]

    #File country
    file_in = open("country.txt", "rt")

    lines = file_in.readlines()
    for line in lines:
        result = line.split(";")
        country_list.append([result[0],result[1],result[2],result[3]])

    file_in.close()

    with Pool() as pool:
        pool.map(task, country_list)
                


