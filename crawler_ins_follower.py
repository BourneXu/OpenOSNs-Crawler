# coding: utf-8

import os
import sys
import json
import codecs
import time
import requests
import random
from keys_ins import *

machine_id = sys.argv[1]
uname = username[int(machine_id) - 1]
psw = password[int(machine_id) - 1]

def login_in():
	global s
	headers = {'referer':'https://www.instagram.com/accounts/login/','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',\
				'x-csrftoken':'oIkLGMiMb2XoPTivKSa3j5JPPDlPpm4i', 'cookie':'mid=WXNN5gAEAAEWpAn7qlqwD7CJ2GQ6; ig_or=landscape-primary; ig_vw=1301; ig_pr=2; ig_vh=776; rur=FTW; csrftoken=oIkLGMiMb2XoPTivKSa3j5JPPDlPpm4i; urlgen="{\"time\": 1508462885\054 \"97.64.41.151\": 25820}:1e5SFg:kML_LSDUIJbJiFmaBIADzv4RaEI"'}
	s = requests.session()
	ck = {'username': uname, 'password': psw}
	url = 'https://www.instagram.com/accounts/login/ajax/'
	r = s.post(url, headers=headers, data=ck)
	print r.text

def crawler_follower(uid):
	global s
	query_id = '17851374694183129'
	url = 'https://www.instagram.com/graphql/query/?query_id=%s&id=%s&first=5000' % (query_id, uid)
	data = s.get(url)
	data = data.json()
	# print data
	if data['status'] == 'ok':
		count = data['data']['user']['edge_followed_by']['count']
		followers = extract_edges(data)
		while data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
			end_cursor = data['data']['user']['edge_followed_by']['page_info']['end_cursor']
			url += '&after=%s' % end_cursor
			data = s.get(url)
			data = data.json()
			if data['status'] == 'ok':
				followers.extend(extract_edges(data))
			else:
				break
	else:
		if data['message'] == 'rate limited':
			print 'Rate limited... Sleep 2 min...'
			time.sleep(120)
			return crawler_follower(uid)
	return {'count': count, 'nodes': followers}

def extract_edges(data):
	followers = []
	if data['status'] == 'ok':
		for edge in data['data']['user']['edge_followed_by']['edges']:
			follower = {}
			follower['id'] = edge['node']['id']
			follower['username'] = edge['node']['username']
			follower['full_name'] = edge['node']['full_name']
			follower['is_verified'] = edge['node']['is_verified']
			followers.append(follower)
	return followers

def load_crawl_list():
	global done_set
	global id_list
	done_set = set([])
	id_list = []
	infile = codecs.open('user_list_ins_uid_%s' %machine_id, 'r')
	s = infile.readlines()
	infile.close()
	for ss in s:
		# ss = unicode.strip(ss)
		listx = json.loads(ss)
		id_list.append(listx)

	if os.path.exists("user_info_ins_follower_%s.txt" % machine_id):
		infile = codecs.open("user_info_ins_follower_%s.txt" % machine_id, "r")
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
		os.remove("user_info_ins_follower_%s.txt" % machine_id)
		os.rename("temp.txt", "user_info_ins_follower_%s.txt" % machine_id)
		print xx


if __name__ == '__main__':
	login_in()
	time.sleep(0.1)
	load_crawl_list()
	fout = codecs.open("user_info_ins_follower_%s.txt" % machine_id, 'a')
	num = 0
	num_done = 0
	num_err = 0
	for (aboutme_id, uid) in id_list:
		num += 1
		if uid not in done_set:
			info = {}
			info['uid'] = uid
			info['Aboutme_id'] = aboutme_id
			print num, ': ', uid
			try:
				info['followers'] = crawler_follower(uid)
			except Exception as e:
				num_err += 1
				print 'Error: ', e
				continue
			else:
				fout.write(json.dumps(info) + '\n')
				num_done += 1
				print 'Done'

	print 'Done Number: ', num_done
	print 'Error Number: ', num_err