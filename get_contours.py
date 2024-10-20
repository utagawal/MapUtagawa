#!/usr/bin/python
import sys
import os
import subprocess
from scripts_hgt.get_hgt import get_hgt
import os, shutil, fnmatch
import subprocess

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def get_contours(country_name, url):
    country_name_lower_case = country_name.lower().replace(" ", "_")

    os.makedirs("dem/"+country_name_lower_case, exist_ok=True)

    os.makedirs("carte_"+country_name_lower_case, exist_ok=True)

    #Get poly file
    if ("-latest.osm.pbf" in url):
        url_poly= url.replace("-latest.osm.pbf",".poly")
    else:
        url_poly= url.replace(".pbf",".poly")

    if(os.path.isdir("dem/"+country_name_lower_case+"/ign")):
        print("Folder IGN found")
        with cd("dem/"+country_name_lower_case+"/ign"):
            path = os.getcwd()
            #Transform shp to osm
            subprocess.run("for i in *.shp; do ogr2osm -t ../../../scripts_shp/contour-translation.py --add-bounds $i; done",shell=True)
            #Transform osm to osm.gz
            subprocess.run("for i in *.osm; do gzip -c $i > $i.gz; done",shell=True)
            #Remove .osm
            subprocess.run("rm *.osm",shell=True)
        #Move
        for f in fnmatch.filter(os.listdir("dem/"+country_name_lower_case+"/ign/"), "*.osm.gz"):
            shutil.move(os.path.join("dem/"+country_name_lower_case+"/ign/", f), os.path.join("carte_"+country_name_lower_case+"/", f))
    else:
        print("HGT")        
        #Get hgt
        get_hgt(country_name_lower_case, url_poly)
        #Download
        if ( os.path.isfile("dem/"+country_name_lower_case+"/hgt_urls.txt")): 
            subprocess.run(["bash", "scripts_hgt/download_hgt.sh","dem/"+country_name_lower_case+"/hgt_urls.txt"])
        #Transform
        with cd("dem/"+country_name_lower_case):
            path = os.getcwd()
            subprocess.run("pyhgtmap --step=10 --no-zero-contour --simplifyContoursEpsilon=0 --jobs=16 --gzip=1 *.hgt",shell=True)    
        #Move
        for f in fnmatch.filter(os.listdir("dem/"+country_name_lower_case+"/"), "*.osm.gz"):
            shutil.move(os.path.join("dem/"+country_name_lower_case+"/", f), os.path.join("carte_"+country_name_lower_case+"/", f))

if __name__ == '__main__':
    country_name=sys.argv[1]
    url=sys.argv[2]
    get_contours(country_name, url)

