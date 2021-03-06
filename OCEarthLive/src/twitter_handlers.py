'''
Created on Apr 21, 2016

@author: neil
'''
import json
from osgeo import ogr
from EONet_json import EONet
from database import DBEONet, DBTweets, DBPhotos, DBSession, PythonDBObject


def place_centroid(tweet):
    '''
    Returns the centroid of the bounding box of the place of the tweet.
    '''
    # If no location data at all, return None.
    geometry = tweet.place.bounding_box if tweet.place else None
    if geometry is None:
        return None
    
    # Build a geometry dictionary.  The first point needs to be added to
    # the end to form a closed figure.
    first_point = geometry.coordinates[0][0]
    geometry.coordinates[0].append(first_point)
    polygon = {u'type': 'Polygon', u'coordinates': geometry.coordinates}
    
    # Create an OGR polygon and calculate the centroid.
    json_geometry = json.dumps(polygon)
    ogr_geometry = ogr.CreateGeometryFromJson(json_geometry)
    centroid_point = ogr_geometry.Centroid()
    return centroid_point


class TweetConsumer(object):
    '''
    Consumes the results of a Twitter search.  To use this class, create a
    subclass and implement the _save() method.
    '''

    # Counters, so we can gauge if it's working.
    title_matches = 0
    geo_enabled_matches = 0
    geo_matches = 0
    
    # More output to standard out if this is True.  Should be off for the
    # search because that returns so much.  For streaming it's helpful.
    verbose = False

    def __in_polygons(self, point):
        '''
        Determines if the point is in one of the polygons or near one of the
        points associated with a hashtag.  If true, then returns the hashtag.
        If false, returns None.
        '''
        hashtag = self.__hashtag_table.get_hashtag_from_point(point)
        return hashtag

    def __filter(self, tweet):
        '''
        Checks for the presence of geodata and if the coordinates are near
        the EONet event.  If yes to both, then returns True.
        '''
        self.title_matches += 1
        hashtag = None
        
        # If the hashtag matches the EONET ID, accept it unconditionally.
        records = self.__hashtag_table.records()
        for record in records:
            eohash = '#'+record.eonet_id
            if eohash in tweet.text:
                hashtag = record.hashtag
                return hashtag
        
        # Use the price coordinates first.  This is a point.
        if tweet.coordinates is not None:
            self.geo_enabled_matches += 1
            geojson_point = json.dumps(tweet.coordinates)
            point = ogr.CreateGeometryFromJson(geojson_point)
            hashtag = self.__in_polygons(point)
            
        else:
            point = place_centroid(tweet)
            if point is not None:
                hashtag = self.__in_polygons(point)
            
        if hashtag is not None:
            self.geo_matches += 1

        return hashtag

    # The search is done on the EONet table.
    def set_search_table(self, tbl):
        self.__hashtag_table = tbl

    def reset_counters(self):
        '''Sets the number of title and geo matches to zero.'''
        self.title_matches = 0
        self.geo_matches = 0
        self.geo_enabled_matches = 0

    def process(self, tweets):
        '''
        Iterate through the tweets, filtering out the relevant ones and then
        send them to a save method.
        '''
        for tweet in tweets:
            if self.verbose:
                print('Tweet: %s.' % tweet.text.encode('utf8', 'replace'))
            hashtag = self.__filter(tweet)
            if hashtag is not None:
                self._save(tweet, hashtag)


# This class is useful for initial development and detailed debugging.
class RawDump(TweetConsumer):
    '''Dumps the tweet, in raw json, to standard out.'''
    def _save(self, tweet, hashtag=None):
        print tweet


# This class presents refined output to standard out.  It's useful for
# high-level troubleshooting. 
class PrettyDump(TweetConsumer):
        '''
        Presents the most interesting parts of a tweet in formatted text to
        standard out.
        '''
        def _save(self, tweet, hashtag=None):
            msg = tweet.text.encode('utf8', 'replace')
            name = tweet.user.name.encode('utf8', 'replace')
            msg_date = tweet.created_at
            if tweet.place is not None:
                place = tweet.place.name.encode('utf8', 'replace')
            else:
                place = 'Unknown'
            print('Written to the database.  [Name: %s][Place: %s][At: %s] %s' %
                  (name, place, msg_date, msg))


# This class saves the tweets to a Sqlite database.
class SQLDump(TweetConsumer):
    '''
    Saves the parts of the tweet that the REST API requires to a database.
    '''
    def __init__(self):
        self.__session = DBSession().session()

    def _save(self, tweet, hashtag=None):

        # Obtain the event from the database.
        event = self.__session.query(DBEONet).filter(DBEONet.hashtag == hashtag).one_or_none()

        # No need to continue if the tweet is already in the database.
        db_tweet = self.__session.query(DBTweets).filter(DBTweets.tweet_id == tweet.id_str).one_or_none()
        if db_tweet is not None:
            return

        # the data fields to save.
        name = tweet.user.name
        create_date = tweet.created_at
        place = tweet.place.name if tweet.place else None
        text = tweet.text
        profile_pic = tweet.user.profile_image_url
        screen_name = tweet.user.screen_name
        try:
            tweet.extended_entities
        except AttributeError:
            media_url = None
        else:
            media_url = tweet.extended_entities['media'][0]['media_url'] if tweet.extended_entities['media'] and tweet.extended_entities['media'][0]['type'] == 'photo' else None
            
        # The coordinates of the tweet are either the specific long, lat
        # provided in the tweet, or the centroid of the place's bounding
        # box.
        # 
        # The coordinates is a list that must be saved as a string.  However
        # the list needs to be reconstituted when it's read.  The clients
        # consuming the REST API need the JSON version of the coordinates.
        if tweet.coordinates is not None:
            coordinates = PythonDBObject(tweet.coordinates)
            json_coordinates = json.dumps(tweet.coordinates)

        # Second choice is the centroid of the place
        elif tweet.place is not None:
            center = place_centroid(tweet)
            
            # Build the dictionary.
            l_coords = [center.GetX(), center.GetY()]
            d_coords = {u'type': 'Point', u'coordinates': l_coords}
            coordinates = PythonDBObject(d_coords)
            json_coordinates = json.dumps(d_coords)

        # Use the centroid of the event if we have that.
        elif hashtag is not None:
            e_json = event.json_geometries
            f_json = str(e_json)
            g_json = f_json[1:-1]
            ogr_geometry = ogr.CreateGeometryFromJson(g_json)
            geotype = ogr_geometry.GetGeometryName
            if 'Point' == geotype:
                coordinates = PythonDBObject(g_json)
                json_coordinates =g_json
            else:
                center = ogr_geometry.Centroid()

                # Build the dictionary.
                l_coords = [center.GetX(), center.GetY()]
                d_coords = {u'type': 'Point', u'coordinates': l_coords}
                coordinates = PythonDBObject(d_coords)
                json_coordinates = json.dumps(d_coords)
                
        # Commit to the database.
        tweet_record = DBTweets(tweet_id=tweet.id_str,
                                eonet_id=event.eonet_id,
                                name=name,
                                createDate=create_date,
                                place=place,
                                msg=text,
                                coordinates=coordinates.encode(),
                                hashtag=hashtag,
                                media_url=media_url,
                                screen_name=screen_name,
                                profile_pic=profile_pic,
                                json_coordinates=json_coordinates)
        self.__session.add(tweet_record)
        self.__session.commit()
                
        # Write the same to standard out to monitor the progress.  The terminal
        # requires the text to be encoded as utf8.
        text = text.encode('utf8', 'replace')
        name = name.encode('utf8', 'replace')
        place = place.encode('utf8', 'replace') if place else None
        media_url = media_url.encode('utf8', 'replace') if media_url else None
        print('Written to the database: [Name: %s][Place: %s][At: %s] %s %s.' %
              (name, place, create_date, text, media_url))
