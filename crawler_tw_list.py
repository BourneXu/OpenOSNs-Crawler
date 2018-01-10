#!/usr/bin/env python
# encoding: utf-8

import tweepy  # https://github.com/tweepy/tweepy
import codecs
import json
import time
import random
import os
import csv
import sys
from tw_keys import *

num_input1 = sys.argv[1]
# num_input2 = sys.argv[2]

# Twitter API credentials
consumer_key = consumer_key_list[int(num_input1) - 1]
consumer_secret = consumer_secret_list[int(num_input1) - 1]
access_key = access_key_list[int(num_input1) - 1]
access_secret = access_secret_list[int(num_input1) - 1]

MAX_TRYTIMES = 4  # 30mins+5mins


def do_something():
    time.sleep(5 * 60 + 10)


def get_all(screen_name):
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
    # cur = []
    tryTimes = 0
    try:
        cur = api.lists_all(screen_name=screen_name, cursor=-1)
        # print cur
    except tweepy.error.RateLimitError:
        tryTimes += 1
        if tryTimes > MAX_TRYTIMES:
            print('MAX_TRYTIMES exceeded')
            return []  # todo: should raise this exception?
        print('15/15min limit exceeded, wait 15 mins, tryTime: %d' % tryTimes)
        do_something()
        # time.sleep(15*60)
        # return get_all(screen_name)
    except Exception as e:
        print e
        pass
    try:
        n_cur = len(cur)
    except:
        outlist = [{'subscriber_count': cur.subscriber_count, 'member_count': cur.member_count, 'name': cur.name,\
                   'created_at': str(cur.created_at), 'uri': cur.uri, 'mode': cur.mode, 'id': cur.id,\
                   'owner': {'id': cur.user.id, 'name': cur.user.name, 'screen_name': cur.user.screen_name,\
                    'followers_count':cur.user.followers_count, 'listed_count':cur.user.listed_count, \
                    'statuses_count':cur.user.statuses_count, 'location': cur.user.location}, 'full_name':cur.full_name, 'slug':cur.slug,\
                    'description': cur.description}]
    else:
        outlist = [{'subscriber_count': u_list.subscriber_count, 'member_count': u_list.member_count, 'name': u_list.name,\
                   'created_at': str(u_list.created_at), 'uri': u_list.uri, 'mode': u_list.mode, 'id': u_list.id,\
                   'owner': {'id': u_list.user.id, 'name': u_list.user.name, 'screen_name': u_list.user.screen_name,\
                    'followers_count':u_list.user.followers_count, 'listed_count':u_list.user.listed_count, \
                    'statuses_count':u_list.user.statuses_count, 'location': u_list.user.location}, 'full_name':u_list.full_name, 'slug':u_list.slug,\
                    'description': u_list.description} for u_list in cur]
    # print('Lists', len(cur[0]))
    return outlist


def load_crawl_list():
    global done_set
    global id_list
    done_set = set([])
    id_list = []
    infile = codecs.open('28w_user_list_tw_%s.txt' % num_input1, 'r')
    s = infile.readlines()
    infile.close()

    for ss in s:
        # ss = unicode.strip(ss)
        listx = json.loads(ss)
        id_list.append(listx)

    if os.path.exists("user_info_tw_list_%s.txt" % num_input1):
        infile = codecs.open("user_info_tw_list_%s.txt" % num_input1, "r")
        output = codecs.open("temp.txt", "w")
        xx = 0
        while True:
            s = infile.readline()
            if not s:
                break
            try:
                # s = unicode.strip(s)
                listx = json.loads(s)
                output.write("%s\n" % json.dumps(listx))
                done_set.add(listx['url'])
                xx += 1
            except:
                pass
                # print 1
        infile.close()
        output.close()

        os.remove("user_info_tw_list_%s.txt" % num_input1)
        os.rename("temp.txt", "user_info_tw_list_%s.txt" % num_input1)

        # print xx


if __name__ == '__main__':

    load_crawl_list()
    fout = codecs.open('user_info_tw_list_list_%s.txt' % num_input1, 'a')
    num = 0
    num_done = 0
    num_err = 0

    for (aboutme_id, url) in id_list:
        num += 1
        print num
        if url not in done_set:
            info = {}
            info['url'] = url
            info['Aboutme_id'] = aboutme_id
            # print num, ': ', url
            try:
                username = url.split('/')[3]
            except:
                # print 'No UserName'
                continue
            else:
                try:
                    tmp = get_all(username)
                    # info['followings'] = tmp[0]
                    info['list'] = tmp
                except Exception as e:
                    print e
                    num_err += 1
                # print 'Error', e
                else:
                    num_done += 1
                    fout.write(json.dumps(info) + '\n')
                    print 'Done'

    print ('Done Number: ', num_done)
    print ('Error Number: ', num_err)
