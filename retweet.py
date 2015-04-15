#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ConfigParser
import os

import tweepy


parser = argparse.ArgumentParser(description="Retweet a user's tweets matching search terms.")
parser.add_argument('--config', default='default.conf', dest='config', help='Configuration file')

def main(config_file):
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)

    screen_name = config.get('settings', 'screen_name')

    # Build savepoint file path
    last_id_filename = 'last_id.' + config_file
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file = os.path.join(rt_bot_path, last_id_filename)

    auth = tweepy.OAuthHandler(config.get('twitter', 'consumer_key'), config.get('twitter', 'consumer_secret'))
    auth.set_access_token(config.get('twitter', 'access_token'), config.get('twitter', 'access_token_secret'))
    api = tweepy.API(auth)

    timeline_kwargs = {
        'count': config.get('settings', 'number_tweets_to_retrieve'),
        'include_rts': False,
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

    for status in statuses:
        if not any([term for term in search_terms if term in status.text]):
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

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.config)

