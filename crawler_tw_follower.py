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

MAX_FRIENDS = 5000
MAX_FOLLOWERS = 5000
MAX_TRYTIMES = 4  # 30mins+5mins


def do_something():
    time.sleep(5 * 60 + 10)


def get_follower(screen_name):
    '''
    refer:

    api.get_user(screen_name=): 90/15min -> .friends_count .followers_count
    # https://github.com/tweepy/tweepy/blob/v3.5.0/tweepy/api.py#L288

    api.followers_ids(screen_name=, cursor=-1): 15/15min -> 5000
    #https://github.com/tweepy/tweepy/blob/v3.5.0/tweepy/api.py#L566

    api.friends_ids(screen_name=, cursor=-1): 15/15min -> 5000
    https://github.com/tweepy/tweepy/blob/v3.5.0/tweepy/api.py#L518


    api.lookup_users(user_ids=):  300/15min -> 100
    # https://github.com/tweepy/tweepy/blob/v3.5.0/tweepy/api.py#L311-L334

    '''
    print('getting', screen_name)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    userInfo = api.get_user(screen_name=screen_name)
    # https://github.com/tweepy/tweepy/blob/v3.5.0/tweepy/api.py#L288
    if userInfo.protected:
        raise Exception('Error Not authorized.')
    friends_count = userInfo.friends_count
    followers_count = userInfo.followers_count
    if followers_count > 1200000:
        fout_tmp = codecs.open('ErrorFollowersNumber_id.txt', 'a')
        fout_tmp.write(screen_name + ', ' + str(followers_count) + '\n')
        fout_tmp.close()
        raise Exception('Error Followers Number larger than 1.2M.')
    # friends = []
    followers = []

    # todo: api.followers_ids always get RateLimitError
    tryTimes = 0
    while (1):
        try:
            cur = api.followers_ids(screen_name=screen_name, cursor=-1)
            # print cur[0]
            break
        except tweepy.error.RateLimitError:
            tryTimes += 1
            if tryTimes > MAX_TRYTIMES:
                print('MAX_TRYTIMES exceeded')
                raise Exception('MAX_TRYTIMES exceeded')  # todo: should raise this exception?
            print('15/15min limit exceeded, wait 15 mins, tryTime: %d' % tryTimes)
            do_something()
            # time.sleep(15*60)
        except:
            pass

    followers += cur[0]
    tryTimes = 0
    while (len(followers) < followers_count and cur[1][1] != 0):
        print('get more followers')
        try:
            cur = api.followers_ids(screen_name=screen_name, cursor=cur[1][1])
            # print cur[0]
            followers += cur[0]
	    tryTimes = 0
        except tweepy.error.RateLimitError:
            tryTimes += 1
            if tryTimes > MAX_TRYTIMES:
                print('MAX_TRYTIMES exceeded')
                return followers  # todo: should raise this exception?
            print('15/15min limit exceeded, wait 15 mins, tryTime: %d' % tryTimes)
            do_something()
            # time.sleep(15*60)

    print('followers', len(followers))
    return followers

def ids_to_list(ids):
    ''' 300/15min -> 100, meaning that 30000 ids can be converted each 15 mins'''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    users = []
    for i in range((len(ids) + 99) // 100):
        res = api.lookup_users(user_ids=ids[i * 100:i * 100 + 100])
        users += [i.screen_name for i in res]
    return users


def load_crawl_list():
    global done_set
    global id_list
    done_set = set([])
    id_list = []
    infile = codecs.open('user_list_tw_follower_%s' % num_input1, 'r')
    s = infile.readlines()
    infile.close()

    for ss in s:
        # ss = unicode.strip(ss)
        listx = json.loads(ss)
        id_list.append(listx)

    if os.path.exists("user_info_tw_follower_%s.txt" % num_input1):
        infile = codecs.open("user_info_tw_follower_%s.txt" % num_input1, "r")
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

        os.remove("user_info_tw_follower_%s.txt" % num_input1)
        os.rename("temp.txt", "user_info_tw_follower_%s.txt" % num_input1)

        print xx

if __name__ == '__main__':

    load_crawl_list()
    fout = codecs.open('user_info_tw_follower_%s.txt' % num_input1, 'a')
    num = 0
    num_done = 0
    num_err = 0

    for (aboutme_id, screen_name) in id_list:
        num += 1
        if screen_name not in done_set:
            info = {}
            info['screen_name'] = screen_name
            info['Aboutme_id'] = aboutme_id
            print num, ': ', screen_name
            try:
                info['follower'] = get_follower(screen_name)
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