'''
Created on Apr 22, 2016

@author: neil
'''
import pickle
import base64
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

# A simple database with just one table is all that is needed.
# The engine can take an additional parameter, echo=True to see the SQL going
# to the server.
engine = create_engine('sqlite:////tmp/tweets.db')
Base = declarative_base()
meta = MetaData(bind=engine)


# The geometries can't be saved in the database.  A geometry is a list of
# dictionaries.
class PythonDBObject(object):
    '''
    Converts objects to base64 strings and back, so that python objects can
    be stored in the sqlite database.
    
    Most noteable, the geometries are lists of dictionaries.
    '''     
    def __init__(self, obj):
        
        # If it's a string, assume it's in base64 format.
        if isinstance(obj, basestring):
            self.__obj = pickle.loads(base64.b64decode(obj))
        else:
            self.__obj = obj
    
    def encode(self):
        '''The base64 encoded representation of the object.'''
        return base64.b64encode(pickle.dumps(self.__obj))
    
    def decode(self):
        '''The python object.'''
        return self.__obj


# The session object exchanges data with the database.  The methods commit()
# and close() write the changes to the database and kill the connection.
class DBSession(object):
    
    def __init__(self):
        self.session = sessionmaker(bind=engine)
    
    def session(self):
        return self.session


# The EONet events
class DBEONet(Base):
    '''Contains the EONet events'''
    __table__ = Table('EONet', meta,
#                      Column('eonet_id', String, primary_key=True),
#                      Column('title', String),
#                      Column('hashtag', String),
#                      Column('geometries', String),
                      autoload=True,
                      autoload_with=engine)

    tweets = relationship('DBTweets', backref='DBEONet')


# The tweets
class DBTweets(Base):
    '''Contains parsed data from the tweet'''
    __table__ = Table('Tweet', meta,
#                      Column('tweet_id', String, primary_key=True),
#                      Column('eonet_id', String, ForeignKey('DBEONet.eonet_id')),
#                      Column('name', String),
#                      Column('createDate', DateTime),
#                      Column('place', String),
#                      Column('msg', String),
#                      Column('coordinates', LargeBinary),
                      autoload=True,
                      autoload_with=engine)

    photos = relationship('DBPhotos', backref = 'DBTweets')

# The photos in the tweets.
class DBPhotos(Base):
    '''Contains photos from the tweets.'''
    __table__ = Table('Photo', meta,
#                      Column('photo_id', Integer, primary_key=True),
#                      Column('tweet_id', String, ForeignKey('DBTweets.tweet_id')),
#                      Column('media_url', String),
                      autoload=True,
                      autoload_with=engine)
