#!/usr/bin/python
import sys
import os
import subprocess
from scripts_hgt.get_hgt import get_hgt
from scripts_hgt.hgt_to_osm import hgt_to_osm
from get_contours import get_contours
import os, shutil, fnmatch
import subprocess
import time


country_name=sys.argv[1]
id = sys.argv[2]
style=sys.argv[3]
url=sys.argv[4]


print("Update "+country_name+ " "+id+" "+style+" "+url)
#Get contours
get_contours(country_name, url)
#Launch script
subprocess.run(["bash", "download_osm.sh",country_name,id,style,url])
subprocess.run(["bash", "create_map.sh",country_name,id,style])
