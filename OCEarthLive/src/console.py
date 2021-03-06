'''
Created on Apr 21, 2016

@author: neil
'''
from EONet_json import EONet
from twitter_search import search_tweets
from twitter_streaming import monitor_tweets


# Main entry point of the system.
def main():
    '''
    Does a search through past tweets on the titles in the EONet JSON, and then
    filters by tweets with geodata and the geolocation within the polygon
    given in the EONet JSON.  These are saved to a SQLite database.
    '''
    # Retrieve the data from EONet (Earth Observatory Natural Event Tracker).
    eonet = EONet()
    
    # Search for recent tweets relating to the events provided by EONet.
    # This is done before monitoring the Twitter stream or listening for REST
    # requests.
    search_tweets(eonet)
    
 
    # Monitor the Twitter live stream for tweets relating to the EONet events.
    monitor_tweets(eonet)

    
if __name__ == '__main__':
    '''
    Run the main program.  Catch a Ctrl-C and shutdown if entered at the
    keyboard.
    '''
    try:
        main()
    except KeyboardInterrupt:
        print('Ctrl-C from keyboard.  Shutting down.')
    except Exception as err:
        print('Exception: %s' % (err))
        raise