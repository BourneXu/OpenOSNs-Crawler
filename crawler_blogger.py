 # -*- coding: utf-8 -*-
from selenium import webdriver
from pyvirtualdisplay import Display		#For Linux
import codecs
import random
import json
from collections import OrderedDict
import time
import os
import sys

num_input1 = sys.argv[1]

def start_browser():
	global browser
	# ----------For Linux---------
	global display
	display = Display(visible=0, size=(1024, 768))
	display.start()
	browser = webdriver.Firefox(executable_path='/root/geckodriver')
	# browser.set_page_load_timeout(5)
	# browser.set_script_timeout(3)

def restart_browser():
    try:
        browser.quit()
    except:
        browser = None
        output = os.popen('ps -ef|grep firefox')
        result = output.read()
        output.close()

        listx = result.split("\n")
        kid_list = []
        for i in listx:
            if 'firefox' in i and 'grep' not in i:
                listy = i.split(" ")
                x = 0
                for j in range(len(listy)):
                    if listy[j] != '':
                        x += 1
                        if x == 2:
                            kid = listy[j]
                            kid_list.append(kid)
                            break
        for kid in kid_list:
            os.system("kill -9 %s" % kid)
        print 'Killed wrong browser'
    try:
        display.stop()
    except:
        pass
    try:
        os.popen('killall Xvfb')
    except:
        pass
    start_browser()
    print 'Restarted'

def crawl_data(aboutme_id, url):
	global num_done
	global num_err
	# global browser
	info = {}
	info['Aboutme_id'] = aboutme_id
	try:
		browser.get(url)
	except:
		pass
	# 	print 'Time out'
	# 	return {'error':'Time out'}
	time.sleep(2 + random.random()*2)
	try:
		profile_link = browser.find_element_by_xpath(r'//*[@class="profile-link"]')
	except:
		print 'No profile link'
		raise Exception('No profile link')
	else:
		try:
			if (profile_link.get_attribute('href')).find(r'www.blogger.com/profile') != -1:
				profile_link.click()
				time.sleep(1 + random.random())
			else:
				num_err += 1
				print 'Other link'
				return {'Aboutme_id': aboutme_id, 'error':'Other link'}
		except:
			print 'Link error'
			return {'Aboutme_id': aboutme_id, 'error':'Link error'}
	# -----------------------------About--------------------------------
	try:
		info['name'] = browser.find_element_by_xpath(r'//*[@class="vcard"]').text
	except:
		info['name'] = None
	# Gender, Industry, Occupation, Location, Introduction, Interests...
	for i in range(1, 10):
		try:
			title = browser.find_element_by_xpath('//*[@class="contents-after-sidebar"]/table/tbody/tr[%d]/th' % i).text
		except Exception as e:
			# print e
			break
		else:
			if title == 'Gender' or title == 'Introduction':
				info[title] = browser.find_element_by_xpath('//*[@class="contents-after-sidebar"]/table/tbody/tr[%d]/td' % i).text
			else:
				# info[title] = browser.find_element_by_xpath('//*[@class="contents-after-sidebar"]/table/tbody/tr[%d]/td/span/a' % i).text
				info[title] = []
				for j in range(1, 10):
					try:
						info[title].append(browser.find_element_by_xpath('//*[@class="contents-after-sidebar"]/table/tbody/tr[%d]/td/span[%d]/a' %(i, j)).text)
					except:
						break
					else:
						for k in range(2, 10):
							try:
								info[title].append(browser.find_element_by_xpath('//*[@class="contents-after-sidebar"]/table/tbody/tr[%d]/td/span[%d]/a[%d]' %(i, j, k)).text)
							except:
								break
	num_done += 1
	print 'Done'
	# print info
	return info
	# -------------------------------------------------------------------

def load_crawl_list():
    global done_set
    global id_list
    done_set = set([])
    id_list = []
    infile = codecs.open('user_list_blogger_%s' % num_input1, 'r')
    s = infile.readlines()
    infile.close()

    for ss in s:
        # ss = unicode.strip(ss)
        listx = json.loads(ss)
        id_list.append(listx)

    if os.path.exists("user_info_blogger_%s.txt" % num_input1):
        infile = codecs.open("user_info_blogger_%s.txt" % num_input1, "r")
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

        os.remove("user_info_blogger_%s.txt" % num_input1)
        os.rename("temp.txt", "user_info_blogger_%s.txt" % num_input1)

        print xx
    random.shuffle(id_list)

def control(url_list):
	fout = codecs.open('user_info_blogger_%s.txt'% num_input1, 'a')
	start_browser()
	count = 0
	for (aboutme_id, url) in url_list:
		count += 1
		if count%5 == 0:
			restart_browser()
			print 'Restarting browser......'
		print url
		try:
			info = crawl_data(aboutme_id, url)
		except:
			continue
		fout.write(json.dumps(info) + '\n')

	browser.quit()
	display.stop()


if __name__ == '__main__':
	load_crawl_list()
	url_list = []
	num_done = 0
	num_err = 0
	for item in id_list:
		if item[0] not in done_set:
			url_list.append(item)
	# for line in fin.readlines():
	# 	l = json.loads(line)
	# 	url_list.append(l)
	control(url_list)

	print 'Done Number: ', num_done
	print 'Error Number: ', num_err




		

