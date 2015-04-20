Caltrain retweet bot
====================

Retweet a given account's tweets containing certain search terms.

Getting started
---------------
* `pip install -r requirements.txt`
* Copy `default.conf.sample` to `default.conf`
* Set search settings: `screen_name` and `search_terms`
* Set Twitter app tokens
* Run script frequently (e.g. every minute through a cron job) to retweet `number_of_tweets_to_retrieve` most recent tweets containing at least one of the search terms
