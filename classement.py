#!/usr/bin/python
import sys
import os
import subprocess
from scripts_hgt.get_hgt import get_hgt
#from scripts_hgt.hgt_to_osm import hgt_to_osm
from get_contours import get_contours
import os, shutil, fnmatch
import subprocess
import time

country_dict={}

#File country
file_in = open("country.txt", "rt")

lines = file_in.readlines()
for line in lines:
    result = line.split(";")
    country_name=result[0].replace('#','')
    if(len(result)==4):
        if(result[0].startswith('#')):
            country_dict[country_name]=1  
        else:
            country_dict[country_name]=sys.maxsize
    else:
        if(result[0].startswith('#')):
            country_dict[country_name]=int(result[4])
        else:
            country_dict[country_name]=sys.maxsize

file_in.close()

sorted_dict=dict(sorted(country_dict.items(), key=lambda item: item[1],reverse=True))
for country in sorted_dict:
    if(sorted_dict[country]==sys.maxsize):
        print(country)
    else:
        print(country + " -> "+str(sorted_dict[country]))
