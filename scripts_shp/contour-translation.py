'''
A translation class for contour data
'''

import ogr2osm

class ContourTranslation(ogr2osm.TranslationBase):
    def filter_tags(self, attrs):
        if not attrs:
            return
        
        tags={}
        
        if 'ALTITUDE' in attrs:
            height = int(float(attrs['ALTITUDE']))
            tags['ele'] = str(height)
            tags['contour'] = 'elevation'

            
            if height % 500 == 0:
                tags['contour_ext'] = 'elevation_major'
            elif height % 100 == 0:
                tags['contour_ext'] = 'elevation_medium'
            elif height % 10 == 0:
                tags['contour_ext'] = 'elevation_minor'
            else:
                return
        return tags