__author__ = "Adrian Dempwolff (phyghtmap@aldw.de)"
__version__ = "2.23"
__copyright__ = "Copyright (c) 2009-2021 Adrian Dempwolff"
__license__ = "GPLv2+"


def str2bytes(string, encoding="utf-8"):
	return bytes(string, encoding=encoding)

def writableString(string):
	return str2bytes(string)

bboxStringtypes = (type(str()), type(bytes()), type(bytearray()))

