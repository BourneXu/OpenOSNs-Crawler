# coding: utf-8

import json
import codecs
import time
import requests
import sys
import os

num_input1 = sys.argv[1]

def get_data(userid, api_key):
	info = requests.get('https://www.googleapis.com/plus/v1/people/%s?key=%s' %(userid, api_key))
	time.sleep(0.2)
	return info.json()

def load_crawl_list():
    global done_set
    global id_list
    done_set = set([])
    id_list = []
    infile = codecs.open('user_list_g_%s' % num_input1, 'r')
    s = infile.readlines()
    infile.close()

    for ss in s:
        # ss = unicode.strip(ss)
        listx = json.loads(ss)
        id_list.append(listx)

    if os.path.exists("user_info_g_%s.txt" % num_input1):
        infile = codecs.open("user_info_g_%s.txt" % num_input1, "r")
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
                    output.write("%s\n" % json.dumps(listx))
                    done_set.add(listx['Aboutme_id'])
                    xx += 1
            except:
                print 1
        infile.close()
        output.close()

        os.remove("user_info_g_%s.txt" % num_input1)
        os.rename("temp.txt", "user_info_g_%s.txt" % num_input1)

        print xx

if __name__ == '__main__':

	load_crawl_list()
	fout = codecs.open('user_info_g_%s.txt' % num_input1, 'a')

	key = ['AIzaSyCLwRM5zXxdSqCJjdxtMMU1ckF7C0Wyff8', 'AIzaSyA_BMOXu_HR1nnV3XxWXrxhMPE_NtaoHGE', \
		   'AIzaSyD2hKG4oVk5TOxFxQ1zDqkBqi0XFcnCOAw', 'AIzaSyCjXqXB-aOvkeKIxyGgr9B3bbzwWklhvMs', \
		   'AIzaSyDsmScloJKe2UEEFsMQ-zcGjmNWFtfpBlM', 'AIzaSyBygOufM0upTOlE_TSue45CpDj-b9LGOAg', \
		   'AIzaSyDN1jb0XRI-MI-WKILvsbFrjbj5OaGDLZ8', 'AIzaSyAPXj-IcXZLwpkwegyAEEMeaxL3loyTgIQ', \
		   'AIzaSyBQu-9N9cziagU0ScaIHIO-UeqW5i_Rusc', 'AIzaSyBcs8LpA4Yc6dYf8Ijxyuk4QZ0jOhNk-00', \
		   'AIzaSyCnBj1OiJVi6CivrCrRdegJmS_ez1NUkA8', 'AIzaSyDVlDek5qhFHfDmE8TzvgpRpqBwUoC1QlU',\
		   'AIzaSyAWULqTJHwfUcvCad60H1GmpiuUHw9ALgM', 'AIzaSyBVWz6x6tQPoczpMyLSma9R9Ro9nfExb2U',\
		   'AIzaSyAEUwm9VpqasUxy-wMmzikCslevCndOwyo', 'AIzaSyDiK6wJoscynYgc50-b92iBLAkwngLERv8',\
		   'AIzaSyCkKRlMVI2VzMYIAnAroIZdkTaMn7E6SL4', 'AIzaSyB05tu6s-QvgJFs9NicfcNhevwMuoVfrbI',\
		   'AIzaSyBgY9kKXuFku3U7pLidlIbJJGx3v5qB8a8', 'AIzaSyDk07mE82ZbReoAFM9kIA6wvagK7D9mfns', \
		   'AIzaSyDOd-BNa5BLgK4ChOrz8lwBTTJ74X0n0f0', 'AIzaSyAEfv3A0uTluy511jm8Cp8F3Muj2cKOFKM',\
		   'AIzaSyAEcUagOCSlCIy7vxQTerGaynvPOW5ptNI', 'AIzaSyDdmjPjTK1_OSJeZm705OSlMOc0LNmdrlI', \
		   'AIzaSyAKoQIz3aXZaF8lczv8v_JCYHwMPovDIqg', 'AIzaSyANm_rXQOeuLV7JP3TWqm4gNMa4GJgGa-k', \
		   'AIzaSyDo6cDLqvxUxRMfU1ARax8oiod5R1gtw68', 'AIzaSyCq1TwPrYkkPDscakA5srY4K69_MeRRTeI',\
		   'AIzaSyAhMe0HE5Gzys3BbhcmAVyeUOuC2UxzqmI', 'AIzaSyDAJUHMfCSN-TZ8f0IF-Qs8N2dl9tSZhEU',\
		   'AIzaSyBCxg4LrjdwgBDWJ2VZoQAhDbuAAHy40Is', 'AIzaSyAy4l1G8OY1mILc8U_hS6UkVRsqb9Ffsg8',\
		   'AIzaSyB37pq4YCypu6vRvK-OrG4BGy1pwP028mg', 'AIzaSyDNhjhmtZcJ5zBwkkBmwoetp-ZGQDQJDUU',\
		   'AIzaSyB-qsI9KmniOoP3DI5LZSeYhKn7S7rRdik', 'AIzaSyBpT_t8xqF_zK9thousKVGYbgCEoYAYhsg']
	num = 0
	n = 0

	for (aboutme_id, url) in id_list:
		num += 1
		if aboutme_id not in done_set:
			info = {}
			info['Aboutme_id'] = aboutme_id
			try:
				print num, ': ', url
			except:
				continue
			try:
				userid = url.split('/')[3]
				if userid == 'u':
					userid = url.split('/')[5]
					if userid == 'b':
						userid = url.split('/')[6]
				elif userid == 'b':
					userid = url.split('/')[4]
			except:
				print 'No UserID'
				continue
			else:
				api_key = key[int(num_input1) - 1]
				info['about'] = get_data(userid, api_key)
			fout.write(json.dumps(info) + '\n')
			print 'Done'


