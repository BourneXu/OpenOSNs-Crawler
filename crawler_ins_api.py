# coding: utf-8

import os
import sys
import json
import codecs
import time
import requests
import random

num_input1 = sys.argv[1]

def get_data(username):
	info = requests.get('https://www.instagram.com/%s/?__a=1' % username)
	profile = json.loads(info.text)
	# print profile
	return profile['user']['followed_by']['count']

def load_crawl_list():
	global done_set
	global id_list
	done_set = set([])
	id_list = []
	infile = codecs.open('user_list_ins_follower_%s' %num_input1, 'r')
	s = infile.readlines()
	infile.close()

	for ss in s:
		# ss = unicode.strip(ss)
		listx = json.loads(ss)
		id_list.append(listx)

	if os.path.exists("user_info_ins_follower_profile_%s.txt" %num_input1):
		infile = codecs.open("user_info_ins_follower_profile_%s.txt" %num_input1, "r")
		output = codecs.open("temp.txt", "w")
		xx = 0
		while True:
			s = infile.readline()
			if not s:
				break
			try:
				# s = unicode.strip(s)
				listx = json.loads(s)
				if listx['username'] not in done_set:
					output.write("%s\n" % json.dumps(listx))
					done_set.add(listx['username'])
					xx += 1
			except:
				print 1
		infile.close()
		output.close()

		os.remove("user_info_ins_follower_profile_%s.txt" %num_input1)
		os.rename("temp.txt", "user_info_ins_follower_profile_%s.txt" %num_input1)

		print xx

num_done = 0
num_err = 0
if __name__ == '__main__':
	load_crawl_list()
	fout = codecs.open('user_info_ins_follower_profile_%s.txt' %num_input1, 'a')
	num = 0

	for username in id_list:
		num += 1
		if username not in done_set:
			info = {}
			info['username'] = username
			print num, ': ', username
			try:
				info['follower_count'] = get_data(username)
			except Exception as e:
				num_err += 1
				print 'Error: ', e
			else:
				num_done += 1
				fout.write(json.dumps(info) + '\n')
				print 'Done'
				if num_done % 20 == 0:
					print "Sleep some time ..."
					time.sleep(60 + 120 * random.random())

	print 'Done Number: ', num_done
	print 'Error Number: ', num_err


