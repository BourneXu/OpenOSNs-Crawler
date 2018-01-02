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
	headers = {'referer':'https://www.instagram.com/accounts/login/','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_22_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',\
				'x-csrftoken':'oIkLGMiMb2XoPTivKSa3j5JPPDlPpm4i', 'cookie':'mid=WXNN5gAEAAEWpAn7qlqwD7CJ2GQ6; ig_or=landscape-primary; ig_vw=1301; ig_pr=2; ig_vh=776; rur=FTW; csrftoken=oIkLGMiMb2XoPTivKSa3j5JPPDlPpm4i; urlgen="{\"time\": 1508462885\054 \"97.64.41.151\": 25820}:1e5SFg:kML_LSDUIJbJiFmaBIADzv4RaEI"'}
	s = requests.session()
	ck = {'username': uname, 'password': psw}
	url = 'https://www.instagram.com/accounts/login/ajax/'
	r = s.post(url, headers=headers, data=ck)
	print r.text

def crawler_liker(uid, media_id):
	global s
	query_id = '17864450716183058'
	url = 'https://www.instagram.com/graphql/query/?query_id=%s&id=%s&shortcode=%s&first=5000' % (query_id, uid, media_id)
	data = s.get(url)
	data = data.json()
	# print data
	if data['status'] == 'ok':
		count = data['data']['shortcode_media']['edge_liked_by']['count']
		likers = extract_edges(data)
		while data['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']:
			end_cursor = data['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']
			url += '&after=%s' % end_cursor
			data = s.get(url)
			data = data.json()
			if data['status'] == 'ok':
				likers.extend(extract_edges(data))
			else:
				break
	else:
		if data['message'] == 'rate limited':
			print 'Rate limited... Sleep 2 min...'
			time.sleep(120)
			return crawler_liker(uid, media_id)
	return {'media_id': media_id, 'count': count, 'nodes': likers}

def extract_edges(data):
	likers = []
	if data['status'] == 'ok':
		for edge in data['data']['shortcode_media']['edge_liked_by']['edges']:
			liker = {}
			liker['id'] = edge['node']['id']
			liker['username'] = edge['node']['username']
			liker['full_name'] = edge['node']['full_name']
			liker['is_verified'] = edge['node']['is_verified']
			likers.append(liker)
	return likers

def load_crawl_list():
	global done_set
	global id_list
	global num_input
	global num_input_sub
	done_set = set([])
	id_list = []
	# infile = codecs.open('user_list_ins_uid_media_%s_%s.txt', 'r')
	# s = infile.readlines()
	# infile.close()
	with codecs.open('user_list_ins_media_code_%s' % machine_id, 'r') as infile:
		for ss in infile:
			# ss = unicode.strip(ss)
			listx = json.loads(ss)
			id_list.append(listx)

	if os.path.exists("user_info_ins_liker_%s.txt" % machine_id):
		infile = codecs.open("user_info_ins_liker_%s.txt" % machine_id, "r" )
		output = codecs.open("temp.txt", "w")
		xx = 0
		while True:
			s = infile.readline()
			if not s:
				break
			try:
				# s = unicode.strip(s)
				listx = json.loads(s)
				if listx['Aboutme_id'] not in done_set:
					if listx['likers'] == []:
						continue
					output.write("%s\n" % json.dumps(listx))
					done_set.add(listx['Aboutme_id'])
					xx += 1
			except:
				print 1
		infile.close()
		output.close()
		os.remove("user_info_ins_liker_%s.txt" % machine_id)
		os.rename("temp.txt", "user_info_ins_liker_%s.txt" % machine_id)
		print xx

def load_uid():
	# infile = codecs.open('user_list_ins_uid.txt', 'r')
	uid_list = {}
	# for line in infile.readlines():
	with codecs.open('user_list_ins_uid.txt', 'r') as infile:
		for line in infile:
			user = json.loads(line)
			uid_list[user[0]] = user[1]
	print 'UID loaded ...'
	return uid_list


if __name__ == '__main__':
	login_in()
	time.sleep(0.1)
	load_crawl_list()
	print 'List loaded ...'
	uid_list = load_uid()
	fout = codecs.open("user_info_ins_liker_%s.txt" % machine_id, 'a')
	num = 0
	num_done = 0
	num_err = 0
	for (aboutme_id, media_ids) in id_list:
		num += 1
		num_media = 1
		if aboutme_id not in done_set and uid_list.has_key(aboutme_id):
			uid = uid_list[aboutme_id]
			info = {}
			# info['media_id'] = media_id
			info['Aboutme_id'] = aboutme_id
			info['likers'] = []
			print num, ': ', aboutme_id
			try:
				for media_id in media_ids:
					try:
						info['likers'].append(crawler_liker(uid, media_id))
					except Exception as e:
						num_err += 1
						print 'User: %d Media_Count: %s Error: ' %(num, num_media), e
						pass
					else:
						print 'User: %d Media_Count: %s Done: ' %(num, num_media)
					if num_media > 10000:
						break
					num_media += 1
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