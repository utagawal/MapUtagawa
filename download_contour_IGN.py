#!/usr/bin/python


from urllib.request import urlopen
from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests
import os
import subprocess

def retrive_urls():
    urls=[]
    html = urlopen("https://geoservices.ign.fr/courbes-de-niveau").read()

    # Parse the html file
    soup = BeautifulSoup(html, 'html.parser')


    for x in soup.find_all('a'): 
        if(x.string is not None and x.string.startswith("https://wxs.ign.fr/")):
            urls.append(x.string)

    file_out = open("IGN_urls.txt", "wt")
    file_out.write("\n".join(urls))
    file_out.close()

def read_urls():
    urls=[]
    file_in = open("IGN_urls.txt", "rt")
    lines = file_in.readlines()
    for line in lines:
        urls.append(line.strip('\n'))
    file_in.close()
    return urls

def download(url):
    print(url)
    if url.find('/'):
        filename = url.rsplit('/', 1)[1]
        subprocess.run("curl -o 'download_IGN/"+filename+"' '"+url+"'", shell=True)

if __name__ == '__main__':
    #retrive_urls()
    os.makedirs("download_IGN/", exist_ok=True)
    #read_urls()
    with Pool(5) as pool:
        pool.map(download, read_urls())