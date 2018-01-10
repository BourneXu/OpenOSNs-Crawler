# -*- coding: utf-8 -*-
from pyvirtualdisplay import Display      #For Linux
from selenium import webdriver
import codecs
import random
import json
import time
import os
import sys
from keys_fb import *

error_ids = {}

machine_id = sys.argv[1]
uname = username[int(machine_id) - 1]
psw = password[int(machine_id) - 1]

def getend(s, s1, s2, x, i):
    y = x
    while True:
        x1 = s.find(s1, y)
        x2 = s.find(s2, y)
        if x1 == -1:
            x1 = 10000000
        if x2 == -1:
            x2 = 10000000
        x1 += 1
        x2 += 1
        if x1 < x2:
            i += 1
            y = x1
        else:
            i -= 1
            y = x2
        if i == 0:
            break
    return y


def load_cookies():
    global browser
    infile = codecs.open("cookies.txt", "r", "utf-8-sig")
    cookies = json.loads(infile.readline())
    infile.close()

    for cookie in cookies:
        browser.add_cookie(cookie)


def save_cookies():
    global browser
    cookies = browser.get_cookies()
    output = codecs.open("cookies.txt", "w", "utf-8-sig")
    output.write("%s\n" % json.dumps(cookies))
    output.close()


def start_browser():
    global browser
    # headers = {
    #     'accept-language': 'en-US;q=8.6,en;q=0.6',
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:36.0) Gecko/20100101 Firefox/36.0 WebKit'
    # }

    # for key, value in headers.iteritems():
    #     webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

    # browser = webdriver.PhantomJS(executable_path='./phantomjs')
    # browser = webdriver.PhantomJS()
    browser = webdriver.Firefox(executable_path='/root/geckodriver')
    browser.get("https://www.facebook.com")
    # browser.save_screenshot("bb.jpg")
    browser.find_element_by_css_selector("input[type='email']").send_keys(uname)
    browser.find_element_by_css_selector("input[type='password']").send_keys(psw)
    browser.find_element_by_css_selector("label[class='uiButton uiButtonConfirm']").click()
    time.sleep(3)
    # browser.set_page_load_timeout(5)
    # browser.set_script_timeout(3)
    # load_cookies()
    cookie_time = time.time()


def restart_browser():
    global browser
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
    start_browser()


def load_crawl_list():
    global done_set
    global id_list
    done_set = set([])
    id_list = []
    infile = codecs.open("user_list_fb_%s" % machine_id, "r", "utf-8-sig")
    s = infile.readlines()
    infile.close()

    for ss in s:
        ss = unicode.strip(ss)
        listx = json.loads(ss)
        id_list.append(listx)

    if os.path.exists("user_info_fb_%s.txt" % machine_id):
        infile = codecs.open("user_info_fb_%s.txt" % machine_id, "r", "utf-8-sig")
        output = codecs.open("temp.txt", "w", "utf-8-sig")
        xx = 0
        while True:
            s = infile.readline()
            if not s:
                break
            try:
                s = unicode.strip(s)
                listx = json.loads(s)
                output.write("%s\n" % json.dumps(listx))
                done_set.add(listx['url'])
                xx += 1
            except:
                print 1
        infile.close()
        output.close()

        os.remove("user_info_fb_%s.txt" % machine_id)
        os.rename("temp.txt", "user_info_fb_%s.txt" % machine_id)

        print xx
    random.shuffle(id_list)


def get_url(url):
    global browser
    error_time = 0
    while True:
        try:
            browser.get(url)
            time.sleep(10+random.random()*3.0)
            html = browser.page_source
            return html
        except:
            error_time += 1
            if error_time > 2:
                return 'Error'


def get_about(url):
    global done_set
    global id_list
    global browser
    error_time = 0
    while True:
        try:
            if error_time == 0:
                browser.find_element_by_css_selector("a[data-tab-key='about']").click()
                time.sleep(3+random.random()*3.0)
            titles = {}

            html = browser.page_source
            x = html.find('data-testid="info_section_left_nav"')
            if x == -1:
                return 'about is nothing'
            else:
                y = getend(html, "<ul", "</ul", x, 1)
                while True:
                    x = html.find("<li", x)
                    if x == -1 or x > y:
                        break
                    x = html.find("title", x)
                    while html[x-1] != '"':
                        x += 1
                    title = ''
                    while html[x] != '"':
                        title += html[x]
                        x += 1

                    x = html.find("data-testid", x)
                    while html[x-1] != '"':
                        x += 1
                    testid = ''
                    while html[x] != '"':
                        testid += html[x]
                        x += 1

                    titles.setdefault(title, testid)

            about = {}
            x = html.find('class="_4ms4"')
            y = getend(html, "<div", "</div", x, 1)
            while html[x] != '<':
                x -= 1
            while html[y - 1] != '>':
                y += 1
            block = html[x:y]
            about.setdefault('Overview', block)

            out1 = codecs.open("error_exmaple.html", "w", "utf-8-sig")
            out1.write(html)
            out1.close()

            for title in titles:
                if title != 'Overview':
                    testid = titles[title]
                    browser.find_element_by_css_selector("a[data-testid='%s']" % testid).click()
                    time.sleep(random.random()*2+4)

                    html = browser.page_source
                    x = html.find('class="_4ms4"')
                    y = getend(html, "<div", "</div", x, 1)
                    while html[x] != '<':
                        x -= 1
                    while html[y - 1] != '>':
                        y += 1
                    block = html[x:y]
                    about.setdefault(title, block)
            return json.dumps(about)
        except Exception as e:
            print e, url, 'About Error'
            error_time += 1
            if error_time >= 2:
                return 'Error'
            time.sleep(10)


def crawl_profile(output):
    global browser
    global done_set
    global id_list
    error_time = 0
    count_time = 0

    expire_time = 0
    for (Aboutme_id, url) in id_list:
        if url not in done_set:
            count_time += 1
            if count_time % 10 == 0:
                save_cookies()
                restart_browser()
            if count_time % (random.randint(0, 10) + 40) == 0:
                time.sleep(random.random()*30.0+30)
            print url

            start_time = time.time()
            # url = "https://www.facebook.com/%s" % fid
            html = get_url(url)
            if html == 'Error':
                error_time += 1
                if error_time > 3:
                    return
                if url not in error_ids:
                    error_ids.setdefault(url, 1)
                else:
                    error_ids[url] += 1
                if error_ids[url] >= 3:
                    output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'error1'}))
                    done_set.add(url)
                print url, 'Error1'
            elif html.find("only be visible to an audience you") != -1:
                error_time = 0
                expire_time += 1
                if expire_time >= 5:
                    print "Expire"
                    time.sleep(108000)
                    return
                output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'expired'}))
                done_set.add(url)
                print url, 'expired'
            elif html.find("link you followed may be broken") != -1:
                error_time = 0
                output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'broken'}))
                done_set.add(url)
                print url, 'broken'
            elif html.find('data-tab-key="about"') != -1 or html.find("pages_navigation") != -1:
                '''expire_time = 0
                error_time = 0
                if html.find('data-tab-key="about"') == -1 and html.find("intro_container_id") == -1:
                    output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'strange page'}))
                    done_set.add(url)
                    print url, 'Strange page', time.time() - start_time
                else:

                    x = html.find("fb-timeline-cover-name")
                    while html[x] != '>':
                        x += 1
                    x += 1
                    name = ""
                    while html[x] != '<':
                        name += html[x]
                        x += 1

                    x = html.find("fsl fcg")
                    if x == -1:
                        block = ""
                    else:
                        y = getend(html, "<span", "</span", x, 1)
                        block = html[x:y]
                    output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'ok', 'name': name, 'gender': block}))
                    done_set.add(url)

                    print url, 'Done', time.time()-start_time'''
                if html.find('data-tab-key="about"') == -1 and html.find("intro_container_id") == -1:
                    output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'strange page'}))
                    done_set.add(url)
                    print url, 'Strange page', time.time() - start_time
                else:
                    error_time = 0
                    x = html.find("intro_container_id")
                    if x == -1:
                        block = 'NULL'
                    else:
                        y = getend(html, "<div", "</div", x, 1)
                        while html[x] != '<':
                            x -= 1
                        while html[y-1] != '>':
                            y += 1
                        block = html[x:y]
                    about = get_about(url)

                    x = html.find("fb-timeline-cover-name")
                    while html[x] != '>':
                        x += 1
                    x += 1
                    name = ""
                    while html[x] != '<':
                        name += html[x]
                        x += 1

                    output.write("%s\n" % json.dumps({'name': name, 'url': url, 'Aboutme_id': Aboutme_id, 'status': 'ok', 'intro': block, 'about': about}))
                    done_set.add(url)

                    print url, 'Done', time.time()-start_time
            else:
                browser.save_screenshot("error.jpg")
                error_time += 1
                if error_time > 3:
                    return
                if url not in error_ids:
                    error_ids.setdefault(url, 1)
                else:
                    error_ids[url] += 1
                if error_ids[url] >= 3:
                    output.write("%s\n" % json.dumps({'url': url, 'Aboutme_id': Aboutme_id, 'status': 'error2'}))
                    done_set.add(url)
                out1 = codecs.open("error_exmaple.html", "w", "utf-8-sig")
                out1.write(html)
                out1.close()
                print url, 'error2'
                return


def control():
    global done_set
    global id_list
    global browser
    # ----------For Linux---------
    display = Display(visible=0, size=(1024, 768))
    display.start()
    # ----------------------------
    start_browser()
    output = codecs.open("user_info_fb_%s.txt" % machine_id, "a", "utf-8-sig")
    while True:
        crawl_profile(output)
        if len(done_set) == len(id_list):
            break
        else:
            restart_browser()
            random.shuffle(id_list)
            # print 'Sleep 3 hours'
            print 'Sleep 5 mins'
            time.sleep(300)
    output.close()
    browser.quit()
    display.stop() #Linux

if __name__ == '__main__':
    load_crawl_list()
    print len(id_list)
    control()
