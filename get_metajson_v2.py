#!/opt/local/bin/python
import requests
import json
import sys
import cgi, cgitb
import copy

class geti:
	
	def api_input(self):
		# Create instance of FieldStorage 
		form = cgi.FieldStorage() 

		# Get data from fields
		q = form.getvalue('q')
		category = form.getvalue('category')
		color = form.getvalue('color')
		try:
			if len(q) > 1:
				return q,color   					#q search
		except:
			try:
				if len(category) >3:   				#seems like a category search, let's verify it with categories API.
					try:
						req_param =  'https://api.mercadolibre.com/categories/' + category
						r = requests.get(req_param)
						content = json.loads(r.content)
						data = content ["message"]
						q="False"
						return q,color
					except:
						#print "Valid Category"
						category = "cat_" + category
						return category,color		#Category search
			except:
				q="False"
				return q,color
	

	def searchcall (self,search_data):
		try:		
			if search_data[0:4] == 'cat_':			#Search category
				search_data = search_data[4:]		#Removing de cat_
				req_param =  'https://api.mercadolibre.com/sites/MLA/search?limit=200&category=' + search_data
				#print req_param
			else:
				req_param =  'https://api.mercadolibre.com/sites/MLA/search?limit=200&q=' + search_data
				
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

	def searchcall2 (self,search_data):		
		if search_data[0:4] == 'cat_':			#Search category
			search_data = search_data[4:]		#Removing de cat_
			req_param =  'https://api.mercadolibre.com/sites/MLA/search?limit=50&category=' + search_data
		else:
			req_param =  'https://api.mercadolibre.com/sites/MLA/search?limit=50&q=' + search_data
	
		r = requests.get(req_param)
		content = json.loads(r.content)
		data = content ["results"]
		search_json=[]
		for i in data:
			offset = i["thumbnail"].find("_f")
			picture_id = 'MLA'+ i["thumbnail"] [offset+3:len(i["thumbnail"])-4]
			items = i["id"],i["thumbnail"],picture_id
			search_json.append(items)
			
		return search_json				#return a list with Items_ID for the first page


	def itemscall (self,item_id):
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
		content = json.loads(r.content)  	#content has pictures_id for the search	
									 		#print content [2] ['pictures'] [0] ['id']
		for i in content:
			data = [i ['pictures'] [0] ['id'],i ['pictures'] [0] ['url']]
			pictures.append(data)		#pictures([picture_id,picture_url)
		return pictures



	def metadatacall (self,pictures):
		results = {}
		results_list = []
	
		for i in pictures:
			req_param = 'https://api.mercadolibre.com/pictures/'+ i[2] + '/metadata'
			r = requests.get(req_param)
			content = json.loads(r.content)
			try:	
				if content['histogram']:
					results ['picture_id'] = i[2]
					results ['url'] = i[1]
					results ['histogram'] = content ["histogram"]
					results_list.append(copy.deepcopy(results))
			except:
				pass
		return results_list

	def realtime_call (self,items):
		results = {}
		results_list = []

		for i in items:
			req_param = 'http://imagefront.mercadolibre.com/picture/colors?pictureURL='+ i[1]
			r = requests.get(req_param)
			content = json.loads(r.content)
			results ['picture_id'] = i[2]
			results ['url'] = i[1]
			results ['colors'] = content["colors"]
			results_list.append(copy.deepcopy(results))
		
		return results_list



	def JsonBuild (self,metadata_list):
		print 'Content-Type: application/json'  
		print
		print json.dumps(metadata_list, sort_keys=True, indent=2)
	
	def exit_json (self):
		print 'Content-Type: application/json'  
		print
		print 'No Data Received ...'
		print 'Please use http://hostname/cgi-bin/json?q=somedata'
		print 'http://hostname/cgi-bin/json?category=MLA1430'
		print 'http://hostname/cgi-bin/json?q=somedata&color=RED'


	def valid_color (self,color):
		if color == 'BLACK' or color == 'GRAY' or color == 'TEAL' or color == 'RED' or color == 'BLUE'or color == 'WHITE' or color == 'GREEN' or color == 'PURPLE' or color == 'PINK':
			#print 'valid color'
			ok = 'TRUE'
			return ok



	def match_color (self,metadata_list,color):
		new_metadata_list = []

		for i in metadata_list:
			pred_color = i ['histogram'] [0] ['id']
			if pred_color == color:
				new_metadata_list.append(i)

		return new_metadata_list		



#Main Code

if __name__ == "__main__":

	getvalues = geti()
	q=getvalues.api_input()
	
try:
	color = q[1]													#Color
	r = q[0]   														#Search value or Category
	if q[0] == "False":
		getvalues.exit_json ()
	else:
		items = getvalues.searchcall2 (r)
		metadata_list = getvalues.realtime_call (items)
		getvalues.JsonBuild (metadata_list)
		
		#metadata_list = getvalues.metadatacall (items)
		
		#if getvalues.valid_color (color) == 'TRUE':
		#	new_metadata_list = getvalues.match_color(metadata_list,color)
		#	getvalues.JsonBuild (new_metadata_list)					#Build Metadata with Color-tag
		#else:
		#	getvalues.JsonBuild (metadata_list)						#Build Metadata only
except:
	getvalues.exit_json()											#Going out
