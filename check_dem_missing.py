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
import glob
import pathlib

dirList = os.listdir()

for dir in dirList:
    if(dir.startswith("carte_")):
        hasFiles=False
        for file in pathlib.Path(dir).glob("*.img"):
            if(str(file).split("/")[1].startswith("88")):
                hasFiles=True
        if(hasFiles==False):
            print(dir)

