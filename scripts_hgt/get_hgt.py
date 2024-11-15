#!/usr/bin/python
import sys
import urllib.request
import os
import os.path
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import shutil
from tqdm import tqdm
import logging
from urllib.error import URLError
from typing import List, Set, Tuple

def setup_logging(country_name: str) -> None:
    """Configure le système de logging."""
    os.makedirs(f"dem/{country_name}/logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"dem/{country_name}/logs/get_hgt.log"),
            logging.StreamHandler()
        ]
    )

def download_polygon(url_poly: str) -> List[Point]:
    """Télécharge et parse le fichier polygon."""
    try:
        logging.info(f"Téléchargement du polygon depuis {url_poly}")
        with urllib.request.urlopen(url_poly) as file:
            polygon = file.read().decode('utf8')
        
        point_list = []
        for line in polygon.splitlines():
            if line not in ('none', '1', 'END') and (line.startswith("   ") or line.startswith("\t")):
                splitString = line.split("   ")
                if len(splitString) == 1:
                    splitString = splitString[0].split("\t")    
                try:
                    longitude = float(splitString[1])
                    latitude = float(splitString[2])
                    point_list.append(Point(longitude, latitude))
                except (IndexError, ValueError) as e:
                    logging.warning(f"Ligne ignorée - format incorrect: {line}. Erreur: {str(e)}")
        
        logging.info(f"Polygon chargé avec succès: {len(point_list)} points")
        return point_list
    except URLError as e:
        logging.error(f"Erreur lors du téléchargement du polygon: {str(e)}")
        raise

def calculate_intersecting_points(polygon: Polygon) -> List[Point]:
    """Calcule les points d'intersection avec la grille."""
    logging.info("Calcul des points d'intersection...")
    hgt_list = []
    total_points = 360 * 180
    
    with tqdm(total=total_points, desc="Calcul des intersections") as pbar:
        for x in range(-180, 180):
            for y in range(90, -90, -1):
                poly_hgt = Polygon([(x,y), (x+1,y), (x+1,y+1), (x,y+1)])
                if poly_hgt.intersects(polygon):
                    hgt_list.append(Point(x,y))
                pbar.update(1)
    
    logging.info(f"Nombre de points d'intersection trouvés: {len(hgt_list)}")
    return hgt_list

def format_coordinates(longitude: int, latitude: int) -> Tuple[str, str]:
    """Formate les coordonnées selon le format requis."""
    longitude_export = f"E{abs(longitude):03d}" if longitude >= 0 else f"W{abs(longitude):03d}"
    latitude_export = f"N{abs(latitude):02d}" if latitude >= 0 else f"S{abs(latitude):02d}"
    return longitude_export, latitude_export

def get_hgt(country_name: str, url_poly: str) -> None:
    """Fonction principale pour récupérer les données HGT."""
    try:
        setup_logging(country_name)
        logging.info(f"Démarrage du traitement pour {country_name}")
        
        # Création du répertoire de sortie
        output_dir = f"dem/{country_name}/"
        os.makedirs(output_dir, exist_ok=True)
        
        # Téléchargement et traitement du polygon
        point_list = download_polygon(url_poly)
        if not point_list:
            logging.error("Aucun point trouvé dans le polygon")
            return
        
        polygon = Polygon(point_list)
        hgt_list = calculate_intersecting_points(polygon)
        
        # Traitement des fichiers HGT
        urls = []
        files_processed = 0
        
        with tqdm(total=len(hgt_list), desc="Traitement des fichiers") as pbar:
            for hgt in hgt_list:
                longitude, latitude = int(hgt.x), int(hgt.y)
                longitude_export, latitude_export = format_coordinates(longitude, latitude)
                
                file = f"{latitude_export}{longitude_export}.SRTMGL1.hgt.zip"
                dest_file = f"{output_dir}{latitude_export}{longitude_export}.hgt"
                
                # Vérification des fichiers existants
                lidar_file = f"dem/lidar_europe/{latitude_export}{longitude_export}.hgt"
                
                if os.path.isfile(lidar_file):
                    try:
                        shutil.copy(lidar_file, dest_file)
                        logging.info(f"Fichier copié depuis lidar_europe: {file}")
                    except IOError as e:
                        logging.error(f"Erreur lors de la copie du fichier {file}: {str(e)}")
                elif not os.path.isfile(dest_file):
                    urls.append(f"https://e4ftl01.cr.usgs.gov//DP109/SRTM/SRTMGL1.003/2000.02.11/{file}")
                
                files_processed += 1
                pbar.update(1)
        
        # Écriture des URLs dans un fichier
        if urls:
            try:
                with open(f"{output_dir}hgt_urls.txt", "wt") as file_out:
                    file_out.write("\n".join(urls) + "\n")
                logging.info(f"{len(urls)} URLs sauvegardées dans hgt_urls.txt")
            except IOError as e:
                logging.error(f"Erreur lors de l'écriture du fichier URLs: {str(e)}")
        
        logging.info(f"Traitement terminé. {files_processed} fichiers traités, {len(urls)} URLs générées")
        
    except Exception as e:
        logging.error(f"Erreur critique lors du traitement: {str(e)}")
        raise

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python get_hgt.py <country_name> <url_poly>")
        sys.exit(1)
    
    country_name = sys.argv[1]
    url_poly = sys.argv[2]
    get_hgt(country_name, url_poly)