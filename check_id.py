#!/usr/bin/python
import sys
import os
import os, shutil, fnmatch
import subprocess
import time

country_list_id=[]

#File country
file_in = open("country.txt", "rt")

lines = file_in.readlines()
for line in lines:
    result = line.split(";")
    for element in country_list_id:
        if(element[1]==result[1]):
            print(result[0])
    country_list_id.append([result[0],result[1]])


file_in.close()

