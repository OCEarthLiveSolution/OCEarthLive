'''
Created on Apr 21, 2016

@author: neil
'''
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.models import SearchResults

from config import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                    CONSUMER_KEY, CONSUMER_SECRET)
from twitter_handlers import SQLDump


class MyListener(StreamListener):
    
    consumer = None
     
    def on_status(self, status):
        tweets = SearchResults()
        tweets.append(status)
        self.consumer.process(tweets)
    
    def on_error(self, status_code):
        print status_code


def monitor_tweets(eonet):

    # Authenticate and connect to the Twitter stream.
    l = MyListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    stream = Stream(auth, l)
    
    consumer = SQLDump()
    l.consumer = consumer

    # The event dictionary contains all the hash tags to monitor and geometries
    # to filter on.
    hashtags = eonet.hashtags()
    l.consumer.set_search_table(eonet)
    
    # Not too many tweets found in the stream.  Set consumer.verbose to True
    # to get a better sense of what's not being picked up.
    l.consumer.verbose = True
    
    print('Listining to Twitter Stream, filtering on these keywords:')
    print hashtags
    stream.filter(track=hashtags)
#    stream.filter(track=['#EONET_376'])