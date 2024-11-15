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

stop_time = time.perf_counter()

print("End Add country in "+time.strftime('%H:%M:%S', time.gmtime(stop_time - start_time)))
