#!/usr/bin/python
import sys
import os
import subprocess
from get_contours import get_contours
import os, shutil, fnmatch
import subprocess
import time

country_name_args=sys.argv[1]

country_list=[]

#File country
file_in = open("country.txt", "rt")

lines = file_in.readlines()
for line in lines:
    result = line.split(";")
    country_name=result[0].replace('#','')
    add=0
    if(country_name==country_name_args):
        add=1
    if(len(result)==4):
        country_list.append([result[0],result[1],result[2],result[3],add+1])
    else:
        country_list.append([result[0],result[1],result[2],result[3],int(result[4])+add])

file_in.close()

file_out = open("country.txt", "wt")
file_modif="\n"
for idx, country in enumerate(country_list):
    file_modif=file_modif+"\n"+country[0]+";"+country[1]+";"+country[2]+";"+country[3].strip()+";"+str(country[4])

file_out.write(file_modif.strip())
file_out.close()

for idx, country in enumerate(country_list):
    country_name=country[0].replace('#','')
    id=country[1]
    style=country[2]
    url=country[3]
    if(country_name==country_name_args):
        print("Update "+country_name+ " "+id+" "+style+" "+url)
        #Launch script
        subprocess.run(["bash", "download_osm.sh",country_name,id,style,url])
        subprocess.run(["bash", "create_map.sh",country_name,id,style])