'''
Created on Apr 21, 2016

@author: neil
'''
import string
import json
import urllib2
from osgeo import ogr
from config import EONET_URL, POINT_SEPARATION
from database import DBEONet, DBSession, PythonDBObject


TEST_EVENT = '''{
    "title": "Test Events",
    "description": "Fake Events for Testing.",
    "link": "http://52.39.3.16:5000/",
    "events": [{
            "id": "TEST_001",
            "title": "Test Earthquake, Irvine, California",
            "description": "A moderate earthquake of magitude 5.2 has produced minor damage.",
            "link": "http://52.39.3.16:5000/",
            "categories": [
                {
                    "id": 9,
                    "title": "Floods"
                }
            ],
            "sources": [
            
            ],
            "geometries": [
                {
                    "date": "2016-04-17T00:00:00Z",
                    "type": "Polygon", 
                    "coordinates": [[ [-118.195, 33.744], [-117.967, 33.853], [-117.739, 33.794], [-117.607, 33.673], [-117.725, 33.476], [-118.195, 33.744] ]]
                }
            
            ]
        }
    ]
}'''


# OGR uses units of degrees.  Miles are better understood by people.
def degree_to_mile(deg):
    return (5280.0/6076.0)*60.0*deg
     

class EONet(object):
    '''
    Object to contain the EONrepr(event['geometries']et events.  The event_id, a hashtag, the
    geometries and the event title are being retained.
    '''
    def __init__(self):
        self.__session = DBSession().session()
        self.__events = self.__session.query(DBEONet).all()
        
        # Update, for good measure.
        self.__update_table()
        
        # Add the test event.  Needed because it's located in Irvine so the
        # geolocation tweets will match.
        self.__update_table(TEST_EVENT)

    def __update_table(self, json_events=None):
        '''
        Makes a dictionary of geometries indexed by hashtags.  This supports
        monitoring the Twitter stream by hashtag and checking the geolocation.
        
        The hashtag is formed from each title by removing punctuation, and then
        combining the first three words.
        '''
        if json_events is None:
            eonet = json.load(urllib2.urlopen(EONET_URL))
        else:
            eonet = json.loads(json_events)
            
        self.events = eonet['events']
        print('Requested EONet data: "%s", %d events received.' %
              (eonet['description'], len(eonet['events']))
        )
        
        # Loop through the events saving them to the database.
        for event in self.events:
            
            # Check if the event is already in the database.
            eonet_id = self.__session.query(DBEONet).filter(DBEONet.eonet_id == event['id']).one_or_none()
            if eonet_id is None:
                self.__add_event(event)

    def __add_event(self, event):
        '''Add an EONet event to the database.'''
        # Clean up the title, removing spaces, punctuation and meaningless
        # words.
        title = event['title']
        exclude = set(string.punctuation)
        title = ''.join(ch for ch in title if ch not in exclude)
        wordlist = title.split()
        hashlist = wordlist[:3]
        
        # Assemble the hashtag.
        hashtag = '#'
        for keyword in hashlist:
            hashtag += keyword.capitalize()

        # The geometries is a list.  The python list object should be,
        # so it's pickled and base64 encoded and then reconstituted when it's
        # read later.
        #
        # The base64 version of the list however isn't meaningful to clients
        # of the REST API.  For that reason, the JSON string representing the
        # geometries is also saved.
        geometries = PythonDBObject(event['geometries'])
        json_geometries = json.dumps(event['geometries'])
        
        new = DBEONet(eonet_id = event['id'],
                      title = title,
                      hashtag = hashtag,
                      geometries = geometries.encode(),
                      json_geometries = json_geometries
                      )

        self.__session.add(new)
        self.__session.commit()
        
        print('Added "%s": %s (%s).' % (new.eonet_id, new.title, new.hashtag))

    def refresh(self):
        '''
        Requests another JSON document of events from EONet and updates the
        EONet table in the database.
        '''
        self.__update_table()

    def get_hashtag_from_point(self, point):
        '''
        Determine if the point either lies within any of the polygon boundaries
        or if it's near a point.  If yes, return the first the hashtag of the
        first matching entry.
        
        The OGR Distance() function returns the distance in the units of the
        coordinate system of the geometries, which in the present case are
        degree.  A degree = 60 nautical miles.
        '''
        results = self.__session.query(DBEONet.hashtag, DBEONet.geometries)
        for hashtag, b64geometries in results:
            
            list_geometries = PythonDBObject(b64geometries).decode()
            for dict_geometry in list_geometries:
                
                json_geometry = json.dumps(dict_geometry)
                ogr_geometry = ogr.CreateGeometryFromJson(json_geometry)
                geotype = ogr_geometry.GetGeometryName()
                if 'POLYGON' == geotype:
                    if point.Within(ogr_geometry):
                        return hashtag
                    
                # Separation is in degrees, which is converted to miles.
                if 'POINT' == geotype:
                    deg_separation = point.Distance(ogr_geometry)

                    # The international date line can make points look like
                    # they're almost 360 degrees apart.
                    if deg_separation > 180:
                        deg_separation = 360 - deg_separation
                    
                    sm_separation = degree_to_mile(deg_separation)
                    if sm_separation < POINT_SEPARATION:
                        return hashtag

        # If nothing's found, return None.
        return None
    
    def records(self):
        '''
        Returns the complete list of events (eonet_id, title), as a list of
        dictionaries.
        '''
        event_records = []
        records = self.__session.query(DBEONet)
        for record in records:
            event_records.append(record)
        return event_records

    def hashtags(self):
        '''Returns the complete list of the hashtags representing the events.''' 
        hashtags = []
        results = self.__session.query(DBEONet.hashtag)
        for result in results:
            hashtag = result[0].encode('utf8', 'replace')
            hashtags.append(hashtag)
        return hashtags
