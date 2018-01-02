#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import codecs
import json
import time
import random
import os
import sys
from keys_tw import *

num_input1 = sys.argv[1]
# num_input2 = sys.argv[2]

# Twitter API credentials
consumer_key = consumer_key_list[int(num_input1) - 1]
consumer_secret = consumer_secret_list[int(num_input1) - 1]
access_key = access_key_list[int(num_input1) - 1]
access_secret = access_secret_list[int(num_input1) - 1]


def get_all_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method
	
	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)
	
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	
	#save most recent tweets
	alltweets.extend(new_tweets)
	
	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1
	
	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print "getting tweets before %s" % (oldest)
		
		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		
		#save most recent tweets
		alltweets.extend(new_tweets)
		
		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		print "...%s tweets downloaded so far" % (len(alltweets))
	
	# ------- csv --------
	# #transform the tweepy tweets into a 2D array that will populate the csv	
	# outtweets = [[tweet.id_str, tweet.created_at, tweet.retweet_count, tweet.favorite_count,\
	# 			  tweet.retweeted, tweet.source, tweet.text.encode("utf-8")] for tweet in alltweets]
	
	# #write the csv	
	# with open('%s_tweets.csv' % screen_name, 'wb') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(["id", "created_at", "retweet_count", "favorite_count", "retweeted", "source", "text"])
	# 	writer.writerows(outtweets)

	# pass
	# --------------------
	outtweets = [{'id_str': tweet.id_str, 'created_at': str(tweet.created_at), 'retweet_count': str(tweet.retweet_count),\
				  'favorite_count': str(tweet.favorite_count), 'retweeted': str(tweet.retweeted), 'source': tweet.source,\
				  'text': tweet.text.encode("utf-8")} for tweet in alltweets]

	# profile_obj = api.get_user(screen_name)
	# profile = profile_obj._json
	# for tweet in alltweets:
	# 	if tweet.user.screen_name == screen_name:
	# 		profile = tweet.user._json
	# 		break
	
	time.sleep(0.1 * random.random())	
	# return [profile, outtweets]
	return outtweets
	
	# f = open('%s_tweets.txt' % screen_name, 'w')
	# f.write(json.dumps(alltweets))
	# f.close()

def load_crawl_list():
	global done_set
	global id_list
	done_set = set([])
	id_list = []
	infile = codecs.open('user_list_list_member_1k_%s.txt' % num_input1, 'r')
	s = infile.readlines()
	infile.close()

	for ss in s:
		# ss = unicode.strip(ss)
		listx = json.loads(ss)
		id_list.append(listx)

	if os.path.exists("user_info_list_member_tweet_1k_%s.txt" % num_input1):
		infile = codecs.open("user_info_list_member_tweet_1k_%s.txt" % num_input1, "r")
		output = codecs.open("temp.txt", "w")
		xx = 0
		while True:
			s = infile.readline()
			if not s:
				break
			try:
				# s = unicode.strip(s)
				listx = json.loads(s)
				if listx['screen_name'] not in done_set:
					output.write("%s\n" % json.dumps(listx))
					done_set.add(listx['screen_name'])
					xx += 1
			except:
				print 1
		infile.close()
		output.close()

		os.remove("user_info_list_member_tweet_1k_%s.txt" % num_input1)
		os.rename("temp.txt", "user_info_list_member_tweet_1k_%s.txt" % num_input1)

		print xx

if __name__ == '__main__':
	#pass in the username of the account you want to download
	# get_all_tweets("J_tsar")

	load_crawl_list()
	fout = codecs.open('user_info_list_member_tweet_1k_%s.txt' % num_input1, 'a')
	num = 0
	num_done = 0
	num_err = 0

	for screen_name in id_list:
		num += 1
		if screen_name not in done_set:
			info = {}
			info['screen_name'] = screen_name
			print num, ': ', screen_name
			try:
				# tmp = get_all_tweets(screen_name)
				# info['profile'] = tmp[0]
				# info['tweets'] = tmp[1]
				info['tweets'] = get_all_tweets(screen_name)
			except Exception as e:
				num_err += 1
				print 'Error', e 
				if 'Rate limit exceeded' in str(e):
					print 'Sleep 14 mins'
					time.sleep(840)
			else:
				num_done += 1
				fout.write(json.dumps(info) + '\n')
				print 'Done'

	print 'Done Number: ', num_done
	print 'Error Number: ', num_err