#!/usr/bin/python
import sys
import os
import subprocess
from scripts_hgt.get_hgt import get_hgt
import os, shutil, fnmatch
import subprocess
from multiprocessing import Pool
import glob

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def process_shp_file(args):
    """Process a single shapefile with ogr2osm"""
    shp_file, script_path = args
    cmd = f'ogr2osm -t {script_path} --add-bounds "{shp_file}"'
    subprocess.run(cmd, shell=True)
    # Create gzip file
    osm_file = shp_file.replace('.shp', '.osm')
    if os.path.exists(osm_file):
        subprocess.run(f'gzip -c "{osm_file}" > "{osm_file}.gz"', shell=True)
        os.remove(osm_file)
    return shp_file

def get_contours(country_name, url):
    country_name_lower_case = country_name.lower().replace(" ", "_")

    os.makedirs(f"dem/{country_name_lower_case}", exist_ok=True)
    os.makedirs(f"carte_{country_name_lower_case}", exist_ok=True)

    #Get poly file
    if "-latest.osm.pbf" in url:
        url_poly = url.replace("-latest.osm.pbf", ".poly")
    else:
        url_poly = url.replace(".pbf", ".poly")

    if os.path.isdir(f"dem/{country_name_lower_case}/ign"):
        print("Folder IGN found")
        with cd(f"dem/{country_name_lower_case}/ign"):
            # Get list of shp files
            shp_files = glob.glob("*.shp")
            script_path = "../../../scripts_shp/contour-translation.py"
            
            # Prepare arguments for parallel processing
            args = [(shp_file, script_path) for shp_file in shp_files]
            
            # Process files in parallel using 8 CPUs
            with Pool(processes=8) as pool:
                pool.map(process_shp_file, args)

        # Move generated files
        for f in fnmatch.filter(os.listdir(f"dem/{country_name_lower_case}/ign/"), "*.osm.gz"):
            shutil.move(
                os.path.join(f"dem/{country_name_lower_case}/ign/", f),
                os.path.join(f"carte_{country_name_lower_case}/", f)
            )
    else:
        print("HGT")        
        # Get hgt
        get_hgt(country_name_lower_case, url_poly)
        
        # Download
        if os.path.isfile(f"dem/{country_name_lower_case}/hgt_urls.txt"):
            subprocess.run(["bash", "scripts_hgt/download_hgt.sh", f"dem/{country_name_lower_case}/hgt_urls.txt"])
        
        # Transform
        with cd(f"dem/{country_name_lower_case}"):
            # Note: pyhgtmap already supports parallel processing with --jobs=8
            subprocess.run("pyhgtmap --step=10 --no-zero-contour --simplifyContoursEpsilon=0 --jobs=8 --gzip=1 *.hgt", shell=True)    
        
        # Move generated files
        for f in fnmatch.filter(os.listdir(f"dem/{country_name_lower_case}/"), "*.osm.gz"):
            shutil.move(
                os.path.join(f"dem/{country_name_lower_case}/", f),
                os.path.join(f"carte_{country_name_lower_case}/", f)
            )

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: script.py country_name url")
        sys.exit(1)
    
    country_name = sys.argv[1]
    url = sys.argv[2]
    get_contours(country_name, url)