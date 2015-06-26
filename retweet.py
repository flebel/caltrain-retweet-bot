#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ConfigParser
import os

import tweepy

from collections import defaultdict, namedtuple


COUNT_TYPES = namedtuple('COUNT_TYPES', ('errors', 'retweeted',))

parser = argparse.ArgumentParser(description="Retweet a user's tweets matching search terms.")
parser.add_argument('--config', default='default.conf', dest='config', help='Configuration file')
parser.add_argument('--dry-run', action='store_true', default=False, dest='dry_run', help='Do not perform retweet')


def construct_last_id_filename(config_filename):
    return config_filename + '.last_id'

def load_config(filename):
    config = ConfigParser.SafeConfigParser()
    config.read(filename)
    return config

def persist_last_seen_id(last_id_file_path, last_tweet_id):
    with open(last_id_file_path, 'w') as f:
        f.write(str(last_tweet_id))

def retrieve_last_seen_id(last_id_file_path):
    try:
        with open(last_id_file_path, 'r') as f:
            return f.read()
    except IOError:
        return ''
    except:
        raise

def construct_api(access_token, access_token_secret, consumer_key, consumer_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def run(api, last_id_filename, number_tweets_to_retrieve, retweet, screen_name, search_terms):
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file_path = os.path.join(rt_bot_path, last_id_filename)

    timeline_kwargs = {
        'count': number_tweets_to_retrieve,
        'include_rts': False,
    }

    last_tweet_id = retrieve_last_seen_id(last_id_file_path)
    if last_tweet_id:
        timeline_kwargs['since_id'] = last_tweet_id

    statuses = api.user_timeline(screen_name, **timeline_kwargs)
    counters = defaultdict(int)

    for status in statuses:
        if not any([term for term in search_terms if term in status.text]):
            continue
        try:
            print 'Retweeted (%(date)s) %(name)s: %(message)s\n' % \
                {
                    'date': status.created_at,
                    'message': status.text.encode('utf-8'),
                    'name': status.author.screen_name.encode('utf-8'),
                }
            if not retweet:
                api.retweet(status.id)
            counters[COUNT_TYPES.retweeted] += 1
        except (tweepy.error.TweepError,) as e:
            # Just in case tweet got deleted in the meantime or already retweeted
            counters[COUNT_TYPES.errors] += 1
            continue

    try:
        last_tweet_id = statuses[0].id
    except IndexError:
        pass

    # Only persist last seen tweet id if it has changed
    if timeline_kwargs.get('since_id') != last_tweet_id:
        persist_last_seen_id(last_id_file_path, last_tweet_id)

    print '%(retweeted)d retweeted, %(errors)d errors occurred.' % counters

if __name__ == '__main__':
    args = parser.parse_args()
    config = load_config(args.config)

    api = construct_api(access_token=config.get('twitter', 'access_token'),
                        access_token_secret=config.get('twitter', 'access_token_secret'),
                        consumer_key=config.get('twitter', 'consumer_key'),
                        consumer_secret=config.get('twitter', 'consumer_secret'))
    run(api,
        last_id_filename=construct_last_id_filename(args.config),
        number_tweets_to_retrieve=config.get('settings', 'number_tweets_to_retrieve'),
        retweet=not args.dry_run,
        screen_name=config.get('search', 'screen_name'),
        search_terms=filter(None, config.get('search', 'search_terms').split(',')))

