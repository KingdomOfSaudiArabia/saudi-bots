import os
import sys
import configparser
import inspect
import tweepy

# Setup config file
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(path, 'bots.config')
config = configparser.SafeConfigParser()
config.read(configfile)

# Get configs from file
consumer_key = config.get('Twitter', 'consumer_key')
consumer_secret = config.get('Twitter', 'consumer_secret')

# tweepy auth
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

def update_config(section, key, value):
    config.set(section, key, value)
    with open(configfile, 'w') as cf:
        config.write(cf)


def oauth(person):
    print('Setting up The ' + person + '...')
    try:
        redirect_url = auth.get_authorization_url()
        print('copy the follwoing link to your web browser, MAKE SURE to' +\
                ' login as the correct person!!.')
        print(redirect_url)
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
    
    verifier = input('Verifier for The ' + person + ':')

    try:
        auth.get_access_token(verifier)
        update_config(person, 'access_token', auth.access_token)
        update_config(person, 'access_token_secret', auth.access_token_secret)
        print('Done from The ' + person)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')


def run():
    print('starting tweepy config...')
    oauth('King')
    print('--------------------')
    oauth('Crown Prince')
    print('--------------------')
    oauth('Deputy Crown Prince')


if __name__ == "__main__":
    run()
