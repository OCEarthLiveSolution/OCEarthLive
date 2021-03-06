'''
Created on Apr 22, 2016

@author: neil
'''
import sqlite3

con = sqlite3.connect('/tmp/tweets.db')

with con:
    cursor = con.cursor()
    
    # EONet -- the EONet events.
    cursor.execute('''
        DROP TABLE IF EXISTS EONet
    ''')
    cursor.execute('''
        CREATE TABLE EONet(
            eonet_id TEXT PRIMARY KEY,
            title TEXT,
            hashtag TEXT,
            geometries BLOB,
            json_geometries TEXT
        )''')
    
    # Tweet - parsed data from the tweet.
    cursor.execute('''
        DROP TABLE IF EXISTS Tweet
    ''')
    cursor.execute('''
        CREATE TABLE Tweet(
            tweet_id TEXT PRIMARY KEY,
            eonet_id INTEGER,
            name TEXT,
            createDate TEXT,
            place TEXT,
            msg TEXT,
            coordinates BLOB,
            json_coordinates TEXT,
            hashtag TEXT,
            media_url TEXT,
            screen_name TEXT,
            profile_pic TEXT,
            FOREIGN KEY(eonet_id) REFERENCES EONet(eonet_id)
        )''')
    
    # Photo -- photos attached to the tweets.
    cursor.execute('''
        DROP TABLE IF EXISTS Photo
    ''')
    cursor.execute('''
        CREATE TABLE Photo(
            photo_id INTEGER PRIMARY KEY,
            tweet_id TEXT,
            media_url TEXT,
            FOREIGN KEY(tweet_id) REFERENCES Tweet(tweet_id)
        )''')
    
    # Commit saves the changes.
    con.commit()
            