'''
Created on Apr 21, 2016

@author: neil
'''
#import json
import tweepy
from twitter_handlers import SQLDump
from config import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                    CONSUMER_KEY, CONSUMER_SECRET)
from config import MAX_SEARCH_TWEETS


class TweetFetcher(object):
    '''
    Receives the tweets matching the search terms and forwards them to a
    consumer for processing.
    '''
    consumer = None
    
    __max_tweets = MAX_SEARCH_TWEETS
    
    def __init__(self, api):
        self.__api = api
        
    def fetch(self):
        '''
        Executes a search on Twitter tweets using a search term and forwards
        the tweets to a consumer for processing.
        ''' 
        # The consumer has the search string.
        query = self.consumer.query
        
        # Execute the search and page through the results. 
        last_id = -1
        count = 0
        while count < self.__max_tweets:
    
            try:
                new_tweets = self.__api.search(q=query, count=count, max_id=str(last_id - 1))
                if not new_tweets:
                    break
                count += len(new_tweets)
                self.consumer.process(new_tweets)
                
                last_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # depending on TweepError.code, one may want to retry or wait
                # to keep things simple, we will give up on an error
                print e
                break        


def search_tweets(eonet):
    
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    api = tweepy.API(auth)
    tweetfetcher = TweetFetcher(api)
    consumer = SQLDump()
    tweetfetcher.consumer = consumer
    
    # Loop through the events in EONet.
    print('Searching for recent tweets related to EONet events.')
    events = eonet.records()
    for event in events:
        
        # So we can watch the progress on the console.
        print('Event %s: %s' % (event.eonet_id, event.title))
        
        # The Twitter search is on the title and then the results are filtered
        # against the polygon.
        consumer.query = event.title
        consumer.set_search_table(eonet)
        tweetfetcher.fetch()
        
        # Done.
        print('Done.  Tweets matching title: %d.  Tweets matching geometry: %d of %d enabled.' %
              (consumer.title_matches, consumer.geo_matches, consumer.geo_enabled_matches))
        consumer.reset_counters()
