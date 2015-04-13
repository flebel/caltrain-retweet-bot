#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import hashlib
import inspect
import os

import tweepy

from itertools import product


path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(path, 'config'))

screen_name = config.get('settings', 'screen_name')

user_blacklist = []
word_blacklist = ['RT']

# Build savepoint path + file
hashed_screen_name = hashlib.md5(screen_name).hexdigest()
last_id_filename = 'last_id_screen_name_%s' % hashed_screen_name
rt_bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(rt_bot_path, last_id_filename)

auth = tweepy.OAuthHandler(config.get('twitter', 'consumer_key'), config.get('twitter', 'consumer_secret'))
auth.set_access_token(config.get('twitter', 'access_token'), config.get('twitter', 'access_token_secret'))
api = tweepy.API(auth)

timeline_kwargs = {
    'count': config.get('settings', 'number_tweets_to_retrieve'),
}

# Retrieve last savepoint if available
try:
    with open(last_id_file, 'r') as file:
        savepoint = file.read()
    timeline_kwargs['since_id'] = savepoint
except IOError:
    savepoint = ''
    print 'No savepoint found. Trying to get as many results as possible.'

statuses = api.user_timeline(screen_name, **timeline_kwargs)

try:
    last_tweet_id = statuses[0].id
except IndexError:
    last_tweet_id = savepoint

search_terms = filter(None, config.get('settings', 'search_terms').split(','))

tw_counter = 0
err_counter = 0

for status, search_term in product(statuses, search_terms):
    if not search_term in status.text:
        continue
    try:
        print 'Retweeted (%(date)s) %(name)s: %(message)s\n' % \
            { 'date' : status.created_at,
            'name' : status.author.screen_name.encode('utf-8'),
            'message' : status.text.encode('utf-8') }

        api.retweet(status.id)
        tw_counter += 1
    except tweepy.error.TweepError as e:
        # Just in case tweet got deleted in the meantime or already retweeted
        err_counter += 1
        continue

print 'Finished. %d Tweets retweeted, %d errors occured.' % (tw_counter, err_counter)

# Persist savepoint
with open(last_id_file, 'w') as file:
    file.write(str(last_tweet_id))

