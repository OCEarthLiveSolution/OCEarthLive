'''
Created on Apr 21, 2016

@author: neil
'''
from osgeo import ogr


x = (-95.980224609375 - 94.64599609375)/2
y = (29.213727993972313 + 30.36072451862922)/2
print ('%f %f' % (x, y))

geojson_poly = """{
                    "date": "2016-04-17T00:00:00Z",
                    "type": "Polygon", 
                    "coordinates": [[ [-95.980224609375, 29.213727993972313], [-95.980224609375, 30.36072451862922], [-94.64599609375, 30.36072451862922], [-94.64599609375, 29.213727993972313], [-95.980224609375, 29.213727993972313] ]]
                }"""
                
yabba = """{"date": "2016-04-13T00:00:00Z", "type": "Polygon", "coordinates": [[44.4140625, 30.877888118431578], [44.4140625, 38.9142723125973], [49.912109375, 38.9142723125973], [49.912109375, 30.877888118431578], [44.4140625, 30.877888118431578]]}"""
dabba = """{
                    "date": "2016-04-13T00:00:00Z",
                    "type": "Polygon", "coordinates": [[ [44.4140625, 30.877888118431578], [44.4140625, 38.9142723125973], [49.912109375, 38.9142723125973], [49.912109375, 30.877888118431578], [44.4140625, 30.877888118431578] ]]
                }"""
anotherjson = """{
                    u'date': u'2016-04-20T00:00:00Z',
                    u'type': u'Point',
                     u'coordinates': [-178.2, -13.1]},
                {
                    u'date': u'2016-04-20T06:00:00Z',
                    u'type': u'Point',
                    u'coordinates': [-178.8, -12.9]},
                {
                    u'date': u'2016-04-20T12:00:00Z',
                    u'type': u'Point',
                    u'coordinates': [-178.8, -12.8]},
                {
                    u'date': u'2016-04-20T18:00:00Z',
                    u'type': u'Point',
                    u'coordinates': [-179.6, -12.6]},
                {
                    u'date': u'2016-04-21T00:00:00Z',
                    u'type': u'Point',
                    u'coordinates': [-179.5, -12.5]},
                {
                    u'date': u'2016-04-21T06:00:00Z',
                    u'type': u'Point',
                    u'coordinates': [-179.3, -13.0]}, {u'date': u'2016-04-21T12:00:00Z', u'type': u'Point', u'coordinates': [-178.9, -12.7]}, {u'date': u'2016-04-21T18:00:00Z', u'type': u'Point', u'coordinates': [-178.3, -12.7]}, {u'date': u'2016-04-22T00:00:00Z', u'type': u'Point', u'coordinates': [-177.4, -12.4]}, {u'date': u'2016-04-22T06:00:00Z', u'type': u'Point', u'coordinates': [-177.0, -12.5]}"""
#geojson_point = """{"type":"Point","coordinates":[108420.33,753808.59]}"""
geojson_point = """{"type":"Point","coordinates":[-95.313,29.787]}"""


it = '''{"date": "2016-04-17T00:00:00Z", "type": "Polygon", "coordinates": [[[-78.907470703125, 38.0603639807185], [-78.907470703125, 38.44255951354092], [-78.47412109375, 38.44255951354092], [-78.47412109375, 38.0603639807185], [-78.907470703125, 38.0603639807185]]]}
'''
point = ogr.CreateGeometryFromJson(geojson_point)
poly = ogr.CreateGeometryFromJson(yabba)
poanothely = ogr.CreateGeometryFromJson(it)
omg = ogr.CreateGeometryFromJson(geojson_poly)
print "%d,%d" % (point.GetX(), point.GetY())
#if point.Within(poly):
#    print 'Yep.'
#else:
#    print 'Nope.'