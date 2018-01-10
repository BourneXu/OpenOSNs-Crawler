# -*- coding: utf-8 -*-
# from pyvirtualdisplay import Display		#For Linux
from selenium import webdriver
# import variable
import codecs
import random
import json
from collections import OrderedDict
import time
import os

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def start_browser():
	global browser
	# global display
	# display = Display(visible=0, size=(2000, 2000))
	# display.start()
	# browser = webdriver.Firefox(executable_path='/root/geckodriver')
	browser = webdriver.Firefox()
	# browser.set_window_size(2000,2000)	#otherwise 'location' will miss
	# browser.set_page_load_timeout(5)
	# browser.set_script_timeout(3)

def load_crawl_list():
	global done_set
	global id_list
	done_set = set([])
	id_list = []
	infile = codecs.open('user_list_flickr.txt', 'r')
	s = infile.readlines()
	infile.close()

	for ss in s:
		# ss = unicode.strip(ss)
		listx = json.loads(ss)
		id_list.append(listx)

	if os.path.exists("user_info_flickr.txt"):
		infile = codecs.open("user_info_flickr.txt", "r")
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
				done_set.add(listx['about']['url'])
				xx += 1
			except:
				print 1
		infile.close()
		output.close()

		os.remove("user_info_flickr.txt")
		os.rename("temp.txt", "user_info_flickr.txt")

		print xx

def crawl_data(url):
	global browser
	info = OrderedDict()
	info['url'] = url
	try:
		browser.get(url)
		print url
	except Exception as e:
		print e
		pass
	time.sleep(2 + random.random()*3)
	# try:
	# 	browser.find_element_by_id('about').click()
	# except:
	# 	pass
	# time.sleep(2 + random.random()*3)

	# if html.find('error-explanation') != -1:
	# 	error = browser.find_element_by_class_name('error-background').text
	# 	return {'Error': error}
	try:
		flickr_name = browser.find_element_by_class_name('truncate').text 
	except Exception as e:
		flickr_name = None
	info['name'] = flickr_name
	# ----------Link to send user an FlickrMail(need sign in)-----------
	try:
		FlickrMail = browser.find_element_by_xpath(r'//*[@class="butt send-flickr-mail"]').get_attribute('href')
	except Exception as e:
		FlickrMail = None
	info['FlickrMail'] = FlickrMail
	# ------------------------------------------------------------------
	try:
		pro = browser.find_element_by_xpath(r'//*[@class="metadata-flexer"]/a')
	except Exception as e:
		pro_if = 'No'
	else:
		pro_if = 'Yes'
	info['pro'] = pro_if

	try:
		subtitle = browser.find_element_by_class_name(r'subtitle no-shrink truncate').text 
	except Exception as e:
		subtitle = None
	info['subtitle'] = subtitle

	try:
		image = browser.find_element_by_xpath(r'//*[@class="coverphoto"]/div[4]/div[1]').get_attribute('style').split(' ')[1].split('"')[1].lstrip('/')
	except Exception as e:
		image = None
	info['image'] = image		
	# ------------
	try:
		follower = browser.find_element_by_xpath(r'//*[@class="followers truncate no-shrink"]').text.split(' ')[0]
		try:
			following = browser.find_element_by_xpath(r'//*[@class="followers truncate no-shrink"]/a').text.split(' ')[0]
		except:
			try:
				following = browser.find_element_by_xpath(r'//*[@class="followers truncate no-shrink"]').text.split('•')[1].split(' ')[0]
			except:
				following = None

	except Exception as e:
		follower = None
		following = None
	info['follower'] = follower
	info['following'] = following
	# -------------
	try:
		photos = browser.find_element_by_xpath(r'//*[@class="metadata-item photo-count"]').text.split(' ')[0]
	except Exception as e:
		photos = None
	info['photos'] = photos
	# ---------------
	# try:
	# 	location = browser.find_element_by_xpath(r'//*[@class="metadata-item truncate cp-location loc"]').text
	# except Exception as e:
	# 	location = None
	# info['location'] = location
	# --------------
	try:
		join_year = browser.find_element_by_xpath(r'//*[@class="metadata-item joined"]').text.split(' ')[1]
	except Exception as e:
		join_year = None
	info['join_year'] = join_year
	# ----------------
	try:
		description = browser.find_element_by_xpath(r'//*[@class="description-container"]/div/p').text
	except Exception as e:
		description = None
	info['description'] = description
	# ------------------
	# ---------Bio Info------
	bio = OrderedDict()
	for i in range(1, 3):
		try:
			title = browser.find_element_by_xpath('//*[@class="infos-view-container"]/ul[%d]/li[1]/span[1]' % i).text
		except Exception as e:		
			# print e, '1'
			break
		else:
			bio[title] = browser.find_element_by_xpath('//*[@class="infos-view-container"]/ul[%d]/li/span[2]/a' % i).text
			for j in range(2, 10):
				try:
					title = browser.find_element_by_xpath('//*[@class="infos-view-container"]/ul[%d]/li[%d]/span[1]' % (i, j)).text
					bio[title] = browser.find_element_by_xpath('//*[@class="infos-view-container"]/ul[%d]/li[%d]/span[2]' % (i, j)).text
				except Exception as e:
					# print e, '2'
					break
	info['bio'] = bio
	# -------------------------------
	# --------General-Stats----------
	stats = OrderedDict()
	for i in range(1,10):
		try:
			title = browser.find_element_by_xpath('//*[@class="general-stats"]/ul/li[%d]' % i).text.split('\n')[1]
			stats[title] = browser.find_element_by_xpath('//*[@class="general-stats"]/ul/li[%d]/span/a' % i).text
		except Exception as e:
			break
	info['stats'] = stats
	# -------------------------------
	Most_popular_photo = {}
	try:
		# Most_popular_photo['favor_num'] = browser.find_element_by_xpath(r'//*[@class="view photo-list-view requiredToShowOnServer"]/div/div/div/div[2]/div[2]/a/span').text
		# Most_popular_photo['title'] = browser.find_element_by_xpath(r'//*[@class="view photo-list-view requiredToShowOnServer"]/div/div/div/div[2]/div/a').text
		Most_popular_photo['href'] = browser.find_element_by_xpath(r'//*[@class="view photo-list-view requiredToShowOnServer"]/div').get_attribute('style').split(' ')[8].split('"')[1].lstrip('/')
	except Exception as e:
		stats = 'None'
	info['Most_popular_photo'] = Most_popular_photo

	# print info, 'Done'
	print 'Done'
	return info


def control(url_list):	
	global browser
	output = codecs.open('user_info_flickr.txt', 'a')
	num = 0
	start_browser()
	count = 1
	for (aboutme_id, url) in url_list:
		if url not in done_set:
			count += 1
			if count > 7:
				count = 1
				try:
					browser.quit()
					# display.stop()
				except:
					pass
				try:
					os.popen('killall Xvfb')
				except:
					pass
				try:
					os.popen('killall firefox')
				except:
					pass
				start_browser()
			num += 1
			print num, url
			info = {}
			info['Aboutme_id'] = aboutme_id
			info['about'] = crawl_data(url)
			output.write(json.dumps(info) + '\n')
		try:
			browser.quit()
			# display.stop()
		except:
			pass

	# return info	


if __name__ == '__main__':
    fin = codecs.open('user_list_flickr.txt', 'r')
    load_crawl_list()
    control(id_list)