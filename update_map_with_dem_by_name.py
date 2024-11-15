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
    country_list.append([result[0],result[1],result[2],result[3]])

file_in.close()

for idx, country in enumerate(country_list):
    country_name=country[0].replace('#','')
    id=country[1]
    style=country[2]
    url = str(country[3]).strip()  # Convertit en chaîne et supprime les espaces en trop
    if(country_name==country_name_args):
        print(f"Update {country_name}, ID={id}, Style={style}, URL={url}")
        #Get contours
        get_contours(country_name, url)
        #Launch script
        subprocess.run(["bash", "download_osm.sh",country_name,id,style,url])
        subprocess.run(["bash", "create_map.sh",country_name,id,style])

