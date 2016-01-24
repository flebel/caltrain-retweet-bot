Caltrain retweet bot
====================

Retweet an account's tweets when certain search terms are found.

Getting started
---------------

* `pip install -r requirements.txt`.
* Copy the configuration file `default.conf.sample` to `default.conf`.
* Define search criteria, Twitter app tokens and, as required, ignored search terms in the configuration file.
* If necessary, update `number_tweets_to_retrieve` in the configuration file. This value indicates the number of tweets to lookup on every call. Increase or decrease depending on the account's tweeting frequency.
* Run script frequently (e.g. every minute through a cron job, dependent on volume and frequency of tweets) to retweet `number_of_tweets_to_retrieve` most recent tweets containing at least one of the comma-separated `search_terms`.

