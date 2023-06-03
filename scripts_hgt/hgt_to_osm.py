#!/usr/bin/python

import sys
import os
from optparse import OptionParser

from scripts_hgt import hgt
from scripts_hgt import osmUtil


def parseCommandLine():
	"""parses the command line.
	"""
	parser = OptionParser(usage="%prog [options] [<hgt or GeoTiff file>] [<hgt or GeoTiff files>]"
    "\nphyghtmap generates contour lines from NASA SRTM and smiliar data"
		"\nas well as from GeoTiff data"
		"\nin OSM formats.  For now, there are three ways to achieve this. First,"
		"\nit can be used to process existing source files given as arguments"
		"\non the command line.  Note that the filenames must have the format"
		"\n[N|S]YY[W|E]XXX.hgt, with YY the latitude and XXX the longitude of the"
		"\nlower left corner of the tile.  Second, it can be used with an area"
		"\ndefinition as input.  The third way to use phyghtmap is to specify a"
		"\npolygon definition.  In the last two cases, phyghtmap will look for a"
		"\ncache directory (per default: ./hgt/) and the needed SRTM files.  If"
		"\nno cache directory is found, it will be created.  It then downloads"
		"\nall the needed NASA SRTM data files automatically if they are not cached"
		"\nyet.  There is also the possibility of masking the NASA SRTM data with"
		"\ndata from www.viewfinderpanoramas.org which fills voids and other data"
		"\nlacking in the original NASA data set.  Since the 3 arc second data available"
		"\nfrom www.viewfinderpanoramas.org is complete for the whole world,"
		"\ngood results can be achieved by specifying --source=view3.  For higher"
		"\nresolution, the 1 arc second SRTM data in version 3.0 can be used by"
		"\nspecifying --source=srtm1 in combination with --srtm-version=3.0. "
		"\nSRTM 1 arc second data is, however, only available for latitudes"
		"\nbetween 59 degrees of latitude south and 60 degrees of latitude north.")

	parser.add_option("-s", "--step", help="specify contour line step size in"
		"\nmeters or feet, if using the --feet option. The default value is 20.",
		dest="contourStepSize", metavar="STEP", action="store", default='10')
	parser.add_option("-0", "--no-zero-contour", help="say this, if you don't want"
		"\nthe sea level contour line (0 m) (which sometimes looks rather ugly) to"
		"\nappear in the output.", action="store_true", default=False, dest="noZero")
	parser.add_option("--start-node-id", help="specify an integer as id of"
		"\nthe first written node in the output OSM xml.  It defaults to 10000000"
		"\nbut some OSM xml mergers are running into trouble when encountering non"
		"\nunique ids.  In this case and for the moment, it is safe to say"
		"\n10000000000 (ten billion) then.", dest="startId", type="int",
		default=10000000, action="store", metavar="NODE-ID")
	parser.add_option("--start-way-id", help="specify an integer as id of"
		"\nthe first written way in the output OSM xml.  It defaults to 10000000"
		"\nbut some OSM xml mergers are running into trouble when encountering non"
		"\nunique ids.  In this case and for the moment, it is safe to say"
		"\n10000000000 (ten billion) then.", dest="startWayId", type="int",
		default=10000000, action="store", metavar="WAY-ID")
	parser.add_option("--max-nodes-per-tile", help="specify an integer as a maximum"
		"\nnumber of nodes per generated tile.  It defaults to 1000000,"
		"\nwhich is approximately the maximum number of nodes handled properly"
		"\nby mkgmap.  For bigger tiles, try higher values.  For a single file"
		"\noutput, say 0 here.",
		dest="maxNodesPerTile", type="int", default=1000000, action="store")
	parser.add_option("--max-nodes-per-way", help="specify an integer as a maximum"
		"\nnumber of nodes per way.  It defaults to 2000, which is the maximum value"
		"\nfor OSM api version 0.6.  Say 0 here, if you want unsplitted ways.",
		dest="maxNodesPerWay", type="int", default=2000, action="store")
	parser.add_option("--gzip", help="turn on gzip compression of output files."
		"\nThis reduces the needed disk space but results in higher computation"
		"\ntimes.  Specifiy an integer between 1 and 9.  1 means low compression and"
		"\nfaster computation, 9 means high compression and lower computation.",
		dest="gzip", action="store", default=1, metavar="COMPRESSLEVEL",
		type="int")
	parser.add_option("--corrx", help="correct x offset of contour lines."
		"\n A setting of --corrx=0.0005 was reported to give good results."
		"\n However, the correct setting seems to depend on where you are, so"
		"\nit is may be better to start with 0 here.",
		metavar="SRTM-CORRX", dest="srtmCorrx", action="store",
		type="float", default=0)
	parser.add_option("--corry", help="correct y offset of contour lines."
		"\n A setting of --corry=0.0005 was reported to give good results."
		"\n However, the correct setting seems to depend on where you are, so"
		"\nit may be better to start with 0 here.",
		metavar="SRTM-CORRY", dest="srtmCorry", action="store",
		type="float", default=0)
	parser.add_option("--void-range-max", help="extend the void value range"
		"\nup to this height.  The hgt file format uses a void value which is"
		"\n-0x8000 or, in terms of decimal numbers, -32768.  Some hgt files"
		"\ncontain other negative values which are implausible as height values,"
		"\ne. g. -0x4000 (-16384) or similar.  Since the lowest place on earth is"
		"\nabout -420 m below sea level, it should be safe to say -500 here in"
		"\ncase you encounter strange phyghtmap behaviour such as program aborts"
		"\ndue to exceeding the maximum allowed number of recursions.",
		default=-0x8000, type="int", metavar="MINIMUM_PLAUSIBLE_HEIGHT_VALUE",
		action="store", dest="voidMax")
	opts, args = parser.parse_args()
	return opts

def makeOsmFilename(borders, opts):
	"""generate a filename for the output osm file. This is done using the bbox
	of the current hgt file.
	"""
	osmName = hgt.makeBBoxString(borders) + ".osm"
	if opts.gzip:
		osmName += ".gz"
	return "dem/"+opts.country_name+"/"+osmName

def getOutput(opts, bounds):
	outputFilename = makeOsmFilename(bounds, opts)
	# standard XML output, possibly gzipped
	output = osmUtil.Output(outputFilename,boundsTag=hgt.makeBoundsString(bounds), gzip=opts.gzip)
	return output

def writeNodes(*args, **kwargs):
	opts = args[-1]
	return osmUtil.writeXML(*args, **kwargs)

def processHgtFile(srcName, opts,checkPoly=False):
	hgtFile = hgt.hgtFile(srcName, opts.srtmCorrx, opts.srtmCorry, None,checkPoly, opts.voidMax)
	hgtTiles = hgtFile.makeTiles(opts)
	for tile in hgtTiles:
		output = getOutput(opts, tile.bbox())
		try:
			elevations, contourData = tile.contourLines(
				stepCont=int(opts.contourStepSize),
				maxNodesPerWay=opts.maxNodesPerWay, noZero=opts.noZero)
		except ValueError: # tiles with the same value on every element
			continue
		# we have multiple output files, so we need to count nodeIds here
		opts.startId, ways = writeNodes(output, contourData,
				elevations, output.timestampString, opts)
		output.writeWays(ways, opts.startWayId)
		# we have multiple output files, so we need to count wayIds here
		opts.startWayId += len(ways)
		output.done()
	return [] # don't need to return ways, since output is already complete

def hgt_to_osm(country_name):
	opts = parseCommandLine()
	hgtDataFiles=[]
	opts.country_name = country_name
	for f in os.listdir("dem/"+country_name+"/"):
		if f.endswith('.hgt'): 
			hgtDataFiles.append("dem/"+country_name+"/"+f)
	opts.area = ":".join([str(i) for i in hgt.calcHgtArea(hgtDataFiles,
		opts.srtmCorrx, opts.srtmCorry)])

	ways = []
	for hgtDataFileName in hgtDataFiles:
		ways.extend(processHgtFile(hgtDataFileName, opts,checkPoly=False))

if __name__=="__main__":
	country_name=sys.argv[1]
	hgt_to_osm(country_name)
