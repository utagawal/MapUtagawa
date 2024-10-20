#!/usr/bin/python
import sys
import os
import subprocess
import os, shutil, fnmatch
import subprocess
import time
import pathlib

country_list=[]

#File country
file_in = open("country.txt", "rt")

lines = file_in.readlines()
for line in lines:
    result = line.split(";")
    country_list.append([result[0],result[1],result[2],result[3]])

file_in.close()

for idx, country in enumerate(country_list):
    hasFilesDem=False
    hasFilesDemWithId=False
    country_name=country[0].replace("#",'')
    id=country[1]
    style=country[2]
    url=country[3]
    country_dir =  "carte_"+country_name.replace(' ','_').lower()
    isDir = os.path.isdir(country_dir)
    if(isDir==False):
        print("Dir "+country_name+" missing")



