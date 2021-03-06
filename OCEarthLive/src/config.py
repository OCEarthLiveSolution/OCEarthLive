'''
Created on Apr 21, 2016

@author: neil
'''
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('conf')

# This file has the API keys.
config.read('/home/neil/.apikeys/twitter.keys')

# Twitter access keys and tokens.
ACCESS_TOKEN = config.get('TWITTER', 'access_token')
ACCESS_TOKEN_SECRET = config.get('TWITTER', 'access_token_secret')
CONSUMER_KEY = config.get('TWITTER', 'consumer_key')
CONSUMER_SECRET = config.get('TWITTER', 'consumer_secret')

MAX_SEARCH_TWEETS = config.get('TWITTER', 'max_search_tweets')

EONET_URL = config.get('EONET', 'url')

POINT_SEPARATION = int(config.get('GEOMETRY', 'separation'))