# -*- coding: utf-8 -*-
import json
import codecs

fin = codecs.open('user_info_fb_test.txt', 'r')
fout = codecs.open('user_info_fb.txt', 'w')

num = 1
num_done = 0
num_error = 0

def getinfo(s, s1, s2, x):
	if x == -1:
		return None
	else:
	    x1 = s.find(s1, x)
	    x2 = s.find(s2, x1+len(s1)+1)
	    try:
		    if x1 != -1:
			    while s[x1-1] != '>':
			    	x1 += 1
			    info = s[x1: x2]
			    return info
		    else:
		    	return None
	    except:
		    return None

for line in fin.readlines():
	user_info = {}
	# user = json.loads(line)
	try:
		user = eval(line)
	except:
		continue
	print num
	num += 1

	if user['status'] == 'ok':
		user_info['Aboutme_id'] = user['Aboutme_id']
		# user_info['name']= user['name']
		about = {}
		# intro = {}
		if user['about'] == 'about is nothing' or user['about'] == 'Error':
			about = None
		else:
			user_about = eval(user['about'])
			user_info['name'] = getinfo(line, r'class=\\\"_h72 lfloat _ohe _50f7\\\">About', '</span>', 1)[6:]
			# -----------Family and Relationships---------
			try:
				info = user_about['Family and Relationships']
			except:
				num_error += 1
				continue
			about['Relationship'] = getinfo(info, '_vb- _50f5', '</div', 1)
			# about['Family Members'] = getinfo(info, r'class=\\\"_3-91 _8o lfloat _ohe\\\"', '</span')

			# ------------Contact and Basic Info----------
			try:
				info = user_about['Contact and Basic Info']
			except:
				continue
			x = info.find('Gender')
			about['Gender'] = getinfo(info, '_50f4', '</span', x)
			x = info.find('Interested In')
			about['Interested In'] = getinfo(info, '_50f4', '</span', x)
			x = info.find('Birthday')
			about['Birthday'] = getinfo(info, '_50f4', '</span', x)
			# x = info.find('Religious Views')
			# about['Religious Views'] = getinfo(info, '<li', '</li', x)
			# x = info.find('Political Views')
			# about['Political Views'] = getinfo(info, '<li', '</li', x)

			x = info.find('swap(this, &quot;')
			if x == -1:
				about['links'] = None
			else:
				links = []
				x2 = x - 1
				for i in range(1, 10):
					x1 = info.find('swap(this, &quot;', x2)
					if x1 == -1:
						break
					else:
						x2 = info.find(r'&quot;);" onclick', x1)
						link_tmp = info[x1+len('swap(this, &quot;'): x2-1].strip('\\')
						link = ''
						for l in link_tmp.split('\\'):
							link += l 
						links.append(link)
				about['links'] = links
			user_info['about'] = about

			# --------------Work and Education-------------
			about['Education'] = []
			about['Work'] = []
			try:
				info = user_about['Work and Education']
			except:
				continue
			x = info.find('>Education<')
			if x == -1:
				about['Education'] = None
				x = len(info)
			else:
				x2 = info.find(r'_2lzr _50f5 _50f7', x)
				for i in range(1,10):
					edu = {}
					if x2 == -1:
						break
					else:
						edu['place'] = getinfo(info, r'data-hovercard-prefer-more-content-show="1"', '<', x2)
						edu['detail'] = getinfo(info, 'fsm fwn fcg', '<', x2)
						x3 = info.find('</span>', x2)
						detail_more = ''
						for j in range(1, 10):
							if x3 == -1:
								break
							else:
								if getinfo(info, '</span', '<', x3) != detail_more:
									detail_more = getinfo(info, '</span', '<', x3)
									try:
										edu['detail'] += ', ' + detail_more
									except:
										break
							x3 = info.find('</span>', x3 + 1)
					x2 = info.find(r'_2lzr _50f5 _50f7', x2+1)
					about['Education'].append(edu)

			x_w = info.find('>Work<')
			if x_w == -1:
				about['Work'] = None
			else:
				info_w = info[x_w : x]
				x2 = info_w.find(r'_2lzr _50f5 _50f7', x_w)
				for i in range(1,10):
					work = {}
					if x2 == -1:
						break
					else:
						work['place'] = getinfo(info_w, r'data-hovercard-prefer-more-content-show="1"', '<', x2)
						work['detail'] = getinfo(info_w, 'class="fsm fwn fcg"', '<', x2)
						x3 = info_w.find('</span', x2)
						detail_more = ''
						for j in range(1, 10):
							if x3 == -1:
								break
							else:							
								if getinfo(info_w, '</span', '<', x3) != detail_more:
									detail_more = getinfo(info_w, '</span', '<', x3)
									try:
										work['detail'] += ', ' + detail_more
									except:
										break
							x3 = info_w.find('</span>', x3 + 1)
						x2 = info_w.find(r'_2lzr _50f5 _50f7', x2+1)
					about['Work'].append(work)
			# ---------------Place lived-----------------
			place = {}
			try:
				info = user_about['Places She\'s Lived']
			except:
				try:
					info = user_about['Places He\'s Lived']
				except:
					try:
						info = user_about['Places You\'ve Lived']
					except:
						info = user_about['Places They\'ve Lived']

			x1 = info.find(r'id="current_city"')

			x2 = info.find('>Current city<', x1)
			info_tmp = info[x1: x2]
			place['Current city'] = getinfo(info_tmp, r'data-hovercard-prefer-more-content-show="1"', '<', 1)

			x1 = info.find(r'id="hometown"')
			x2 = info.find('>Hometown<', x1)
			info_tmp = info[x1: x2]
			place['Hometown'] = getinfo(info_tmp, r'data-hovercard-prefer-more-content-show="1"', '<', 1)
				
			about['Places Lived'] = place
			user_info['about'] = about
			num_done += 1

	else:
		num_error += 1

	fout.write(json.dumps(user_info) + '\n')

print 'Done Number:', num_done
print 'Error Number:', num_error

	



					






