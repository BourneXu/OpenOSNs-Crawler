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

def get_favor(uid):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
	alltweets = []	
	#print out each favorited tweet
	for page in tweepy.Cursor(api.favorites,id=uid,count=200).pages():
	  	alltweets.extend(page)
	  	print "...%s tweets downloaded so far" % (len(alltweets))
	outtweets = [{'id_str': tweet.id_str, 'created_at': str(tweet.created_at), 'retweet_count': str(tweet.retweet_count),\
				  'favorite_count': str(tweet.favorite_count), 'retweeted': str(tweet.retweeted), 'source': tweet.source,\
				  'text': tweet.text.encode("utf-8"), 'user': {'id':tweet.user.id_str, 'screen_name':tweet.user.screen_name}} for tweet in alltweets]
	fout.write(str(alltweets[1]) + '\n') 
	return outtweets


def load_crawl_list():
	global done_set
	global id_list
	done_set = set([])
	id_list = []
	infile = codecs.open('user_list_tw_uid_%s' % num_input1, 'r')
	s = infile.readlines()
	infile.close()

	for ss in s:
		# ss = unicode.strip(ss)
		listx = json.loads(ss)
		id_list.append(listx)

	if os.path.exists("user_info_tw_favor_%s.txt" % num_input1):
		infile = codecs.open("user_info_tw_favor_%s.txt" % num_input1, "r")
		output = codecs.open("temp.txt", "w")
		xx = 0
		while True:
			s = infile.readline()
			if not s:
				break
			try:
				# s = unicode.strip(s)
				listx = json.loads(s)
				if listx['uid'] not in done_set:
					output.write("%s\n" % json.dumps(listx))
					done_set.add(listx['uid'])
					xx += 1
			except:
				print 1
		infile.close()
		output.close()

		os.remove("user_info_tw_favor_%s.txt" % num_input1)
		os.rename("temp.txt", "user_info_tw_favor_%s.txt" % num_input1)

		print xx

if __name__ == '__main__':
	#pass in the username of the account you want to download
	# get_all_tweets("J_tsar")

	load_crawl_list()
	fout = codecs.open('user_info_tw_favor_%s.txt' % num_input1, 'a')
	num = 0
	num_done = 0
	num_err = 0

	for aboutme_id,uid in id_list:
		num += 1
		if uid not in done_set:
			info = {}
			info['uid'] = uid
			info['Aboutme_id'] = aboutme_id
			print num, ': ', uid
			try:
				# tmp = get_all_tweets(uid)
				# info['profile'] = tmp[0]
				# info['tweets'] = tmp[1]
				info['favor_tweets'] = get_favor(uid)
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