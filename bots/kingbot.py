import os
import logging
import configparser
import inspect
import spa
import tweepy
import github

# Setup config file
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(path, 'bots.config')
config = configparser.SafeConfigParser()
config.read(configfile)

# Setup logging
logfile = os.path.join(path, 'bots.log')
logging.basicConfig(filename=logfile, level=logging.INFO, 
        format='%(asctime)s [%(levelname)s] (%(name)s): %(message)s')

# Get configs from file
access_token = config.get('King', 'access_token')
access_token_secret = config.get('King', 'access_token_secret')
consumer_key = config.get('Twitter', 'consumer_key')
consumer_secret = config.get('Twitter', 'consumer_secret')
last_arrival_id = config.get('King', 'last_arrival_id')
last_tweet_id = config.get('King', 'last_tweet_id')
last_cabinet_decision_id = config.get('King', 'last_cabinet_decision_id')

# tweepy auth
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def get_arrival():
    '''Return list of all arrival news after the last_id
    if there is no news empty list will be return
    '''
    new_news = []
    if int(last_arrival_id) > 0:
        new_news = spa.arrival_news(person = 1, last_id = int(last_arrival_id))
    return new_news
    

def get_leave():
    '''Return list of all leave news after last_id
    if there is no news empty list will be return
    '''
    new_news = []
    if int(last_arrival_id) > 0:
        new_news = spa.leave_news(person = 1, last_id = int(last_arrival_id))
    return new_news


def get_timeline(person, last_id):
    timeline = api.user_timeline(person, since_id=last_id)
    return timeline


def get_cabinet_decision():
    decisions = []
    if int(last_cabinet_decision_id) > 0:
        decisions = spa.cabinet_decision(last_id=int(last_cabinet_decision_id))
    return decisions


def update_config(section, key, value):
    config.set(section, key, value)
    with open(configfile, 'w') as cf:
        config.write(cf)


def tweet(text, url = ''):
    if url !=  '':
        _tweet = text + ' ' + url
        api.update_status(_tweet)
    else:
        api.update_status(text)


def retweet(tweet_id):
    api.retweet(tweet_id)


def retweet_with_comment(t_user, t_id, comment):
    url = 'https://twitter.com/{}/status/{}'.format(t_user, t_id)
    tweet(comment, url)

def update_twitter_location(clocation):
    api.update_profile(location=clocation)   


def run():
    # if there is arrival news update config file with the last id then loop 
    # and tweet the first one since it arrival news and person cann't be 
    # in two placess at the same time.
    logging.info('Running kingbot...')
    logging.info('Checking new arrival news...')
    arrival_news = get_arrival()
    if arrival_news:
        logging.info('Found new arrival to : ' + arrival_news[0][3])
        tweet_text = 'وصلت بحمد الله إلى ' + arrival_news[0][3]
        logging.info('tweeting: ' + tweet_text)
        tweet(tweet_text)
        logging.info('Updating location to: ' + arrival_news[0][3])
        update_twitter_location(arrival_news[0][3])
        logging.info('Updating config for arrival_last_id to: ' + arrival_news[0][0])
        update_config('King', 'last_arrival_id', arrival_news[0][0])

    # if there is leave news update config file with the last id then loop 
    # and tweet the first one since it leave news and person cann't be 
    # in two placess at the same time.
    logging.info('Checking new leave news...')
    leave_news = get_leave()
    if leave_news:
        logging.info('Found new leave to : ' + leave_news[0][3])
        tweet_text = 'غادرت بحفظ الله ورعايته ' + leave_news[0][3]
        logging.info('tweeting: ' + tweet_text)
        tweet(tweet_text)
        logging.info('Updating location to: ')
        update_twitter_location(' ')
        logging.info('Updating config for arrival_last_id to: ' + leave_news[0][0])
        update_config('King', 'last_arrival_id', leave_news[0][0])

    # if there is a new tweet retweet it and update the last_tweet_id
    logging.info('Checking new tweets to retweet...')
    timeline = get_timeline('KingSalman', int(last_tweet_id))
    if timeline:
        logging.info('Found new tweets: ' + str(len(timeline)))
        logging.info('Updating config for last_tweet_id to: ' + timeline[0].id_str)
        update_config('King', 'last_tweet_id', timeline[0].id_str)
        for _tweet in timeline:
            logging.info('retweeting: ' + _tweet.id_str)
            retweet_with_comment('KingSalman', _tweet.id, 'قمت بكتابة هذه التغريدة:')

    # if there is a new cabinet desision tweet it and add ticket on github repo
    # and update the last_cabinet_desisoin_id 
    logging.info('Checking new cabinet desison...')
    decisions = get_cabinet_decision()
    if decisions:
        logging.info('Found new cabinet decision: ' + str(len(decisions)))
        logging.info('Updating config for last_cabinet_decision_id to: ' + str(decisions[0][0]))
        update_config('King', 'last_cabinet_decision_id', decisions[0][0])
        for _decision in reversed(decisions):
            _title = _decision[1]
            if len(_title) > 107:
                _title = _title[:len(_title)-(len(_title)-104)]
                _title = _title + '...'
            _tweet_text = 'أمرت بـ: ' + _title
            logging.info('tweeting: ' + _tweet_text)
            tweet(_tweet_text, _decision[2])
            logging.info('Creating github issue for: ' + _decision[0])
            github.make_issue(title=_decision[1], body=_decision[3])
    logging.info('--------------- DONE -------------------')


if __name__ == "__main__":
    run()
