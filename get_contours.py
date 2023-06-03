#!/usr/bin/python
import sys
import os
import subprocess
from scripts_hgt.get_hgt import get_hgt
from scripts_hgt.hgt_to_osm import hgt_to_osm
import os, shutil, fnmatch
import subprocess

def get_contours(country_name, url):
    country_name_lower_case = country_name.lower().replace(" ", "_")

    os.makedirs("dem/"+country_name_lower_case, exist_ok=True)

    os.makedirs("carte_"+country_name_lower_case, exist_ok=True)

    #Get poly file
    url_poly= url.replace("-latest.osm.pbf",".poly")

    #Get hgt
    get_hgt(country_name_lower_case, url_poly)
    #Download
    if ( os.path.isfile("dem/"+country_name_lower_case+"/hgt_urls.txt")): 
        subprocess.run(["bash", "scripts_hgt/download_hgt.sh","dem/"+country_name_lower_case+"/hgt_urls.txt"])
    #Transform
    hgt_to_osm(country_name_lower_case)
    #Move
    for f in fnmatch.filter(os.listdir("dem/"+country_name_lower_case+"/"), "*.osm.gz"):
        shutil.move(os.path.join("dem/"+country_name_lower_case+"/", f), os.path.join("carte_"+country_name_lower_case+"/", f))

if __name__ == '__main__':
    country_name=sys.argv[1]
    url=sys.argv[2]
    get_contours(country_name, url)

