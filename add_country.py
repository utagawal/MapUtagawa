#!/usr/bin/python
import sys
import os
import subprocess
from get_contours import get_contours
import os, shutil, fnmatch
import subprocess
import time

country_name_args=sys.argv[1]
style=sys.argv[2]
url=sys.argv[3]
 
start_time = time.perf_counter()
country_name_lower_case = country_name_args.lower().replace(" ", "_")
country_name_upper_case = country_name_lower_case.capitalize()


os.makedirs("dem/"+country_name_lower_case, exist_ok=True)

os.makedirs("carte_"+country_name_lower_case, exist_ok=True)

 
#Get Id
country_list=[]

#File country
file_in = open("country.txt", "rt")


lines = file_in.readlines()
for line in lines:
    result = line.split(";")
    country_list.append([result[0],result[1],result[2]])
file_in.close()



for idx, country in enumerate(country_list):
    country_name=country[0].replace('#','')
    if(country_name==country_name_args):
        print("The country already exists")
        sys.exit()

id=f'{int(country_list[len(country_list)-1][1])+1:02d}'


#File country
file_in = open("country.txt", "rt")

file_source = file_in.read()
file_modif = file_source+'\n'+country_name_args+';'+id+';'+style+';'+url+';1'
file_in.close()

file_out = open("country.txt", "wt")
file_out.write(file_modif)
file_out.close()

print("Start Add country"+country_name_args+ " "+id+ " "+" "+style,url)

#Get contours
get_contours(country_name_args, url)

#Launch script
subprocess.run(["bash", "update_map.sh",country_name_args,id,style,url])
stop_time = time.perf_counter()

print("End Add country in "+time.strftime('%H:%M:%S', time.gmtime(stop_time - start_time)))
