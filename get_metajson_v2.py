#!/opt/local/bin/python
import requests
import json
import sys
import cgi, cgitb
import copy

def api_input ():
	# Create instance of FieldStorage 
	form = cgi.FieldStorage() 

	# Get data from fields
	q = form.getvalue('q')
	category = form.getvalue('category')

	try:
		if len(q) > 1:
			return q   					#q search
	except:
		try:
			if len(category) >3:   		#seems like a category search, let's verify it with categories API.
				try:
					req_param =  'https://api.mercadolibre.com/categories/' + category
					print req_param
					r = requests.get(req_param)
					content = json.loads(r.content)
					data = content ["message"]
					q="False"
					return q
				except:
					print "Valid Category"
					category = "cat_" + category
					return category			#Category search
		except:
			q="False"
			return q

def searchcall (search_data):
	try:		
		if search_data[0:4] == 'cat_':			#Search category
			search_data = search_data[4:]		#Removing de cat_
			req_param =  'https://api.mercadolibre.com/sites/MLA/search?category=' + search_data
		else:
			req_param =  'https://api.mercadolibre.com/sites/MLA/search?q=' + search_data
	
		r = requests.get(req_param)
		content = json.loads(r.content)
		data = content ["results"]
		#print data[0]["id"]
		search_json=[]
		for i in data:
			search_json.append(i["id"])
	except:
		pass

	return search_json				#return a list with Items_ID for the first page

def itemscall (item_id):
	picture_id=[]
	req_param = ''
	pictures=[]
	base_url = 'https://api.mercadolibre.com/items?ids='

	for i in item_id:
		req_param = req_param + i + ','

	#removing the last ','
	req_param = req_param[:-1]
	url = base_url + req_param + '&attributes=pictures'
	r = requests.get(url)
	content = json.loads(r.content)  #content has pictures_id for the search	
									 #print content [2] ['pictures'] [0] ['id']
	for i in content:
		data = [i ['pictures'] [0] ['id'],i ['pictures'] [0] ['url']]
		pictures.append(data)		#pictures([picture_id,picture_url)
	return pictures

def metadatacall (pictures):
	results = {}
	results_list = []

	for i in pictures:
		req_param = 'https://api.mercadolibre.com/pictures/'+ i[0] + '/metadata'
		#print req_param
		r = requests.get(req_param)
		content = json.loads(r.content)
		
		try:	
			if content['histogram']:
				results ['picture_id'] = i[0]
				results ['url'] = i[1]
				results ['histogram'] = content ["histogram"]
				results_list.append(copy.deepcopy(results))
		except:
			pass

	return results_list


def JsonBuild (metadata_list):
	print 'Content-Type: application/json'  
	print
	print json.dumps(metadata_list, sort_keys=True, indent=2)
	
def exit_json ():
	print 'Content-Type: application/json'  
	print
	print 'No Data Received ...'
	print 'Please use http://hostname/cgi-bin/json?q=somedata'

	


#Main Code

q = api_input ()
if q == "False":
	exit_json ()
else:	
	items_id = searchcall (q)
	pictures = itemscall (items_id)
	metadata_list = metadatacall (pictures)
	JsonBuild (metadata_list)





