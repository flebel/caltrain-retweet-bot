#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import hashlib
import inspect
import os

import tweepy

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(path, 'config'))

search_query = config.get('settings', 'search_query')
tweet_language = config.get('settings', 'tweet_language')

user_blacklist = []
word_blacklist = ['RT', u'♺']

# Build savepoint path + file
hashed_search_query = hashlib.md5(search_query).hexdigest()
last_id_filename = 'last_id_search_query_%s' % hashed_search_query
rt_bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(rt_bot_path, last_id_filename)

auth = tweepy.OAuthHandler(config.get('twitter', 'consumer_key'), config.get('twitter', 'consumer_secret'))
auth.set_access_token(config.get('twitter', 'access_token'), config.get('twitter', 'access_token_secret'))
api = tweepy.API(auth)

# Retrieve last savepoint if available
try:
    with open(last_id_file, 'r') as file:
        savepoint = file.read()
except IOError:
    savepoint = ''
    print 'No savepoint found. Trying to get as many results as possible.'

# Search query
timelineIterator = tweepy.Cursor(api.search, q=search_query, since_id=savepoint, lang=tweet_language).items()

timeline = list(timelineIterator)

try:
    last_tweet_id = timeline[0].id
except IndexError:
    last_tweet_id = savepoint

# Filter @replies/blacklisted words & users out and reverse timeline
timeline = filter(lambda status: status.text[0] != '@', timeline)
timeline = filter(lambda status: not any(word in status.text.split() for word in word_blacklist), timeline)
timeline = filter(lambda status: status.author.screen_name not in user_blacklist, timeline)
timeline.reverse()

tw_counter = 0
err_counter = 0

for status in timeline:
    try:
        print '(%(date)s) %(name)s: %(message)s\n' % \
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

