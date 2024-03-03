# Création d'une carte Garmin personnalisée 
## Environnement
Mes scripts sont utilisé surtout sur MacOsX et testé sur Ubuntu

Pour télécharger les outils et commande nécessaire 
```bash
bash download_require.sh
```
> Sous Mac OS X il faut installer les commandes avec votre outils préferé, il vous faut ``curl``, ``python3``, ``java``, ``unzip`` moi j'utilise Homebrew

## Digital Elevation Model (dem)
Si vous voulez avoir des lignes de niveaux il vous faudra des fichiers hgt, pour l'europe je conseille les fichiers de sonny en arc 1° pour le reste du monde la nasa (https://search.earthdata.nasa.gov/search).

Les scripts utilisent par défault les fichiers de la nasa, pour cela il faut créer un fichier ``password.txt``
où un l'intérieur vous aller indiquer
```txt
machine urs.earthdata.nasa.gov login MON_LOGIN password MON_PASSWORD
```
- MON_LOGIN : votre login de connection à (https://search.earthdata.nasa.gov/search)
- MON_PASSWORD : votre password à (https://search.earthdata.nasa.gov/search)
  
Si vous souhaitez utiliser votre propre fichier déposez les dans ``dem/NOM_DE_LA_REGION``

## Ajouter une région
```python
python add_country.py NOM_DE_LA_REGION TYPE URL_OSM_GEOFABRIK
```
- NOM_DE_LA_REGION : Nom de la carte dans la montre mais aussi pour les répertoires.
- TYPE : rando ou route, le style rando est celui que je partage sur le site mais un autre style existe pour le vélo de route 
- URL_OSM_GEOFABRIK :  url du fichier de votre région sur le site http://download.geofabrik.de

exemple pour ajouter la France pour le type rando:
```python
cd /var/data/garminmaps
source .venv/bin/activate
python add_country.py France utagawa http://download.geofabrik.de/europe/france-latest.osm.pbf
deactivate
```

Cette commande permet de récupérer la région, de récupérer les hgt ou d'utiliser les hgt si présent et de générer le fichier qui sera déposé dans  ``~/Documents/Mega/Open_Garmin_Map/``, oui le script est pour mon usage du coup il y a des routes qui me sont utiles vous pouvez modifier le fichier ``create_map.sh`` pour modifier cette route.

## Mettre à jour mes cartes
Rien de plus simple un fichier ``country.txt`` est créé lorsqu'on utilise le script ``add_country.py`` qui permet de garder vos régions avec les paramètres utilisés, ce qui permet de lancer la commande:

```python
python update_all.py
```
Cette commande télécharger le fichier osm sur geofabrik mais aussi télécharger les fichiers hgt.
Sauf que les fichiers hgt sont rarement mis à jour du coup la commande:

```python
python update_only_osm.py
```
Cette commande permet de juste télécharger les fichiers osm sur geofabrik et reprendre le fichier hgt qui sont déja chez vous.

## Possible problème d'utilisation des scripts
 - J'ai une machine avec 64 go de ram et du coup dans les commandes java j'ai utilisé 32go de ram. Pour modifier rechercher dans les scripts ``java -Xmx32768m`` et remplacer par la valeur de ram que vous souhaitez.


## Détails des scripts
Si vous avez besoin vous pouvez executer les différents script manuellement un part un, je ne recommande pas cette méthode mais si il y a des erreurs ca permet de relancer que celle qui échoue.

#### `download_require.sh`
Le script `download_require.sh` permet de télécharger les logiciels splitter et mkgmap ainsi que sous Linux les commandes nécessaires au bon fonctionnement des scripts. Il execute aussi la commande `pip install -r requirements.txt` pour télécharger les librairies python.
> Attention, il est possible que les versions ne mkgmap ou/et splitter doivent être mise à jour pour que leurs téléchargement.
```bash
bash download_require.sh
```

#### `get_contours.py`
Le script `get_contours.py` permet de télécharger les fichiers hgt contenu sur le site https://urs.earthdata.nasa.gov/ et de les convertirs au format osm pour être utilisé par les autres scripts. 
```python
python get_contours.py NOM_DE_LA_REGION URL_OSM_GEOFABRIK
```
- NOM_DE_LA_REGION : Nom de la carte dans la montre mais aussi pour les répertoires.
- URL_OSM_GEOFABRIK :  url du fichier de votre région sur le site http://download.geofabrik.de
Pour notre exemple:
```bash
python get_contours.py France http://download.geofabrik.de/europe/france-latest.osm.pbf
```
 
#### `update_map.sh`
Le script `update_map.sh` permet de télécharger le fichier osm et de lancer le script `create_map.sh`.

Ce script considère que le répertoire carte_NOM_DE_LA_REGION existe, dans notre exemple carte_france

```bash
bash update_map.sh NOM_DE_LA_REGION ID TYPE URL_OSM_GEOFABRIK
```
- NOM_DE_LA_REGION : Nom de la carte dans la montre mais aussi pour les répertoires.
- ID :  Identifiant de la carte sur la montre, celui-ci doit être unique entre toute les cartes sinon il risque d'avoir des cartes non disponible sur la montre. Ne connaissant pas les identifiants des autres il est possible que vous devriez modifier si vous utilisez le même qu'une carte que vous avez deja sur votre montre.
- TYPE : rando ou route, le style rando est celui que je partage sur le site mais un autre style existe pour le vélo de route 
- URL_OSM_GEOFABRIK :  url du fichier de votre région sur le site http://download.geofabrik.de

Pour notre exemple:
```bash
bash update_map.sh France 00 rando http://download.geofabrik.de/europe/france-latest.osm.pbf
```
#### `create_map.sh`
Le script `create_map.sh` permet de créer un fichier pour votre appareil Garmin.

Ce script considère que le répertoire carte_NOM_DE_LA_REGION existe dans notre exemple carte_france

En fonction de vos besoins si vous souhaitez les courbes les fichiers osm des courbes doivent être présent dans le répertoire carte_NOM_DE_LA_REGION si ils ne sont pas présent la génération se fera sans l'intégration des courbes.

```bash
bash create_map.sh NOM_DE_LA_REGION ID TYPE
```
- NOM_DE_LA_REGION : Nom de la carte dans la montre mais aussi pour les répertoires.
- ID :  Identifiant de la carte sur la montre, celui-ci doit être unique entre toute les cartes sinon il risque d'avoir des cartes non disponible sur la montre. Ne connaissant pas les identifiants des autres il est possible que vous devriez modifier si vous utilisez le même qu'une carte que vous avez deja sur votre montre.
- TYPE : rando ou route, le style rando est celui que je partage sur le site mais un autre style existe pour le vélo de route 

Pour notre exemple:
```bash
bash create_map.sh France 00 rando
```
>Attention à la fin du script il déplace le fichier réaliser dans ~/Documents/Mega/Open_Garmin_Map/ cela est utile pour moi mais peut être pas pour vous. Modifier pour vos besoins si besoin.

>La RAM disponible pour java est indiqué à 32768m (32go) en fonction de votre ordinateur modifié cette valeur.

## Si vous voulez personnaliser la carte

Doc pour le style:

https://www.mkgmap.org.uk/doc/pdf/style-manual.pdf

TYPViewer pour éditer le fichier TYP:

https://sites.google.com/site/sherco40/


## Pour aller plus loin
Comme je gère plusieurs régions j'ai donc réaliser des scripts car je ne connais pas les commandes sur le bout des doigts.

Dans les lignes qui suit j'explique pour une carte de la france.

## Téléchargement des outils
```bash
bash download_require.sh
```

## Téléchargement des fichiers pour les courbes

https://search.earthdata.nasa.gov/search

Vous allez récupérer les fichiers en format tif il faudra le changer en hgt puis en OSM
```
gdal_translate -of SRTMHGT mon_fichier.tif mon_fichier.hgt
```
Sinon pour l'europe vous avez ce site qui permet de récupérer les fichiers en hgt directement.

http://viewfinderpanoramas.org/dem1d.html

ou 

https://sonny.4lima.de/

Le lien pour la france est ici:

https://drive.google.com/drive/folders/1MQqQe3VeFuUM9hRlXIz-uM0wvBNXBM2U

Pour passer du format hgt au format OSM nous allons utiliser le logiciel hgt2osm que vous pouvez télécharger ici:
https://github.com/FSofTlpz/Hgt2Osm2/tree/master/bin

La commande est la suivante:
```
hgt2osm.exe --HgtPath=. --WriteElevationType=false --FakeDistance=-0.5 --MinVerticePoints=3 --MinBoundingbox=0.00016 --DouglasPeucker=0.05 --MinorDistance=10 --OutputOverwrite=true
```

Maintenant que les courbes sont aux formats OSM je vous recommande de les sauvegarder car cette étape ne sera rarement refaite vu que les fichies de courbes ne changent presque jamais.

## Téléchargement de la carte
Sur le site http://download.geofabrik.de/ vous pouvez récupérer la région que vous souhaitez réaliser.

Pour la france le lien est : http://download.geofabrik.de/europe/france-latest.osm.pbf

## Découper les fichiers
Nous allons utiliser l'application splitter

Pour les courbes comme c'est au format OSM vous pouvez lancer la commande suivante:

```bash
java -Xmx32768m -jar splitter.jar --mapid=73240100 --max-nodes=1600000 --keep-complete=false *.OSM

mv template.args courbes.args
```

Pour découper le fichier de la france vous pouvez lancer la commande suivante:

```bash
java -Xmx32768m -jar splitter.jar --mapid=63240101 --max-nodes=1000000 --keep-complete=true --route-rel-values=foot,hiking --overlap=0 france-latest.osm.pbf

mv template.args france-latest.args
```

## Générer le fichier IMG pour votre montre
Vous devez récuper le répertoire style qui se trouve sur ce github, il contient le fichier TYP et les style pour mkgmap.

```bash
java -Xmx32768m -jar ../mkgmap-r4802/mkgmap.jar --road-name-pois --add-pois-to-areas --add-pois-to-lines --remove-short-arcs --precomp-sea=../sea.zip --x-check-precomp-sea=0  --style-file=../style/rando ../style/rando.TYP --family-name="Test" --description="Test" --mapname=94240105 --family-id=1 --product-id=1 --latin1 --net --route --road-name-pois --gmapsupp -c france-latest.args -c courbes.args
```

Il ne vous reste plus qu'a copier le fichier gmapsupp.img dans montre appareil Garmin

> Attention il est possible qu'un fichier se porte déja ce nom, si c'est le cas renommer votre fichier autrement cela n'a pas d'importance. 




