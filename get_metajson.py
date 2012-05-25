#!/opt/local/bin/python
import requests
import json
import sys
import cgi, cgitb

def api_input ():
	# Create instance of FieldStorage 
	form = cgi.FieldStorage() 

	# Get data from fields
	q = form.getvalue('q')
	try:
		if len(q) > 2 :
			return q
	except:   							#if No parameters are passed Return q='False'
		q = 'False'
		return q
	

def searchcall (search_data):
	try:		
		req_param =  'https://api.mercadolibre.com/sites/MLA/search?q=' + search_data
		print req_param
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
	metadata_list = []
	jitem_id = {}
	jpicture_id = {}
	jpicture_url = {}
	jhistogram = {}
	data = []

	for i in pictures:
		try:
			req_param = 'https://api.mercadolibre.com/pictures/'+ i[0] + '/metadata'
			r = requests.get(req_param)
			content = json.loads(r.content)
			jpicture_id['picture_id'] = i[0]
			jpicture_url['url'] = i[1]
			jhistogram['histogram'] = content ["histogram"]
			data = [jpicture_id, jpicture_url,jhistogram]

		except:
			pass

		metadata_list.append(data)
		
	return metadata_list


def JsonBuild (metadata_list):
	print 'Content-Type: application/json'  
	print
	print json.dumps(metadata_list, separators=(',',':'), sort_keys=True, indent=4)
	
def exit_json ():
	print 'Content-Type: application/json'  
	print
	print 'No Data Received ...'
	print 'use ?q=somedata'



#Main Code

q = api_input ()
if q == "False":
	exit_json ()
else:	
	items_id = searchcall (q)
	pictures = itemscall (items_id)
	metadata_list = metadatacall (pictures)
	print metadata_list
	JsonBuild (metadata_list)





