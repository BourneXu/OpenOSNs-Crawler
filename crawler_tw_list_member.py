# -*-coding: utf-8 -*-
import json
import codecs
import tweepy
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

def do_something():
    time.sleep(5 * 60 + 10)

# fout_test = codecs.open('test.txt', 'w')
def get_all(slug, owner, member_total):
    print('getting... slug:' + slug + ' owner: '+ owner + ' member_total:'+ str(member_total))
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    # api = tweepy.API(auth)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
    members = []
    for page in tweepy.Cursor(api.list_members, owner, slug).items():
    	members.append(page)
    print('members', len(members))
    return [m._json for m in members]

def load_crawl_list():
    global done_set
    global id_list
    done_set = set([])
    id_list = []
    infile = codecs.open('user_list_lists_%s.txt' % num_input1, 'r')
    s = infile.readlines()
    infile.close()

    for ss in s:
        # ss = unicode.strip(ss)
        listx = json.loads(ss)
        id_list.append(listx)

    if os.path.exists("user_info_list_member_%s.txt" % num_input1):
        infile = codecs.open("user_info_list_member_%s.txt" % num_input1, "r")
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
                done_set.add(listx['slug+owner'])
                xx += 1
            except:
                pass
                # print 1
        infile.close()
        output.close()

        os.remove("user_info_list_member_%s.txt" % num_input1)
        os.rename("temp.txt", "user_info_list_member_%s.txt" % num_input1)

        # print xx


if __name__ == '__main__':

    load_crawl_list()
    fout = codecs.open('user_info_list_member_%s.txt' % num_input1, 'a')
    num = 0
    num_done = 0
    num_err = 0

    for (slug, owner, member_total) in id_list:
        num += 1
        print num
        if (slug + '+' + owner) not in done_set:
            info = {}
            info['slug'] = slug
            info['owner'] = owner
            info['slug+owner'] = slug + '+' + owner
            try:
                tmp = get_all(slug, owner, member_total)
                # info['followings'] = tmp[0]
                info['member'] = tmp
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