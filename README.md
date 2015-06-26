Caltrain retweet bot
====================

Retweet an account's tweets when certain search terms are found.

Getting started
---------------

* `pip install -r requirements.txt`
* Copy `default.conf.sample` to `default.conf`
* Define search criteria and Twitter app tokens in configuration file
* If necessary, adjust `number_tweets_to_retrieve` on every call in configuration file
* Run script frequently (e.g. every minute through a cron job, dependent on volume and frequency of tweets) to retweet `number_of_tweets_to_retrieve` most recent tweets containing at least one of the comma-separated `search_terms`

