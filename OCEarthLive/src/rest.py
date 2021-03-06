'''
Created on Apr 21, 2016

@author: neil
'''
from database import DBTweets, Base
from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy.decorators import registerSchema


# It appears that this creates the _eve_schema object.
registerSchema('tweets')(DBTweets)

SETTINGS = {
    'DEBUG': True,
    'X_DOMAINS': '*',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/tweets.db',
    'XML': False,
    'JSON': True,
    'PAGINATION': False,
    'DOMAIN': {
        'tweets': DBTweets._eve_schema['tweets'],
        
        }
}


def main():

    app = Eve(auth=None, settings=SETTINGS, validator=ValidatorSQL, data=SQL)
    
    # bind SQLAlchemy
    db = app.data.driver
    Base.metadata.bind = db.engine
    db.Model = Base
    db.create_all()

    app.run(host='0.0.0.0', debug=True, use_reloader=True)

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
