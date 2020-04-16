from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import Flask
from flask import request
from flask import jsonify
from flask import url_for
from flask import redirect
import json
from sqlalchemy import text
import requests
import pandas as pd
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import flask
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app,support_credentials = True)
app.config['SECRET_KEY'] = 'some secret string here'

userpass = 'mysql+pymysql://root:@'
basedir  = '127.0.0.1'
dbname   = '/jobs'
socket   = '?unix_socket=/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
dbname   = dbname + socket
app.config['SQLALCHEMY_DATABASE_URI'] = userpass + basedir + dbname

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
db.init_app(app)

try:
		with open('prev_num_rows.pickle', 'rb') as f:
				prev_num_rows = pickle.load(f)
except:
		prev_num_rows = 0

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

def write_pickle():
		global prev_num_rows
		with open('prev_num_rows.pickle', 'wb') as f:
				pickle.dump(prev_num_rows, f)

def isnumeric(string):
	try:
		num = int(string)
		return True
	except:
		return False

def check_sha1(string):
	if(len(string)!=40):
		return False
	for i in string:
		if(not(i=='a' or i=='b' or i=='c' or i=='d' or i=='e' or i=='f' or i=='A' or i=='B' or i=='C' or i=='D' or i=='E' or i=='F' or (isnumeric(i) and int(i)>=0 and int(i)<=9))):
			return False
	return True

def validate_date(datestr):
	try:
		now = datetime.strptime(datestr,'%d-%m-%Y:%S-%M-%H')
		return True
	except:
		return False

def editDistance(str1, str2, m, n): 

	if m == 0: 
		 return n 
  
	if n == 0: 
		return m 
  
	if str1[m-1]== str2[n-1]: 
		return editDistance(str1, str2, m-1, n-1) 
  
	return 1 + min(editDistance(str1, str2, m, n-1),    
				   editDistance(str1, str2, m-1, n),     
				   editDistance(str1, str2, m-1, n-1)   
				   ) 

@app.route('/api/v1/db/read', methods=['POST'])
def read_data():
	req_data = request.get_json()

	tabname = req_data['table']
	columns = req_data['columns']
	where = req_data['where']
	delete = req_data['delete']
	if(not(where=="None")):
		wcol = where.split("=")[0]
		wval = where.split("=")[1]
		where_string=""
		for i in range(len(where.split("AND"))):
			if("LIKE" not in where.split("AND")[i]):
				if(not(isnumeric(where.split("AND")[i].split("=")[1]))):
					where_string+=where.split("AND")[i].split("=")[0]
					where_string+="=\'"
					where_string+=where.split("AND")[i].split("=")[1]
					where_string+="\'"
				else:
					where_string+=where.split("AND")[i].split("=")[0]
					where_string+="="
					where_string+=where.split("AND")[i].split("=")[1]
			else:
				where_string += where.split("AND")[i]
			if(not(i==len(where.split("AND"))-1)):
					where_string+=" AND "

	else:
		where_string = "None"

	if(isinstance(columns,list)):
		column_string = ""
		for s in range(len(columns)):
			if(s!=len(columns)-1):
				column_string+=columns[s]+","
			else:
				column_string+=columns[s]
	else:
		column_string = columns

	if(delete == "False"):
		if(not(where_string=="None")):
			sql = text("SELECT "+column_string+" FROM "+tabname+" WHERE "+where_string)
		else:
			sql = text("SELECT "+column_string+" FROM "+tabname)
		#print(sql)
		result = db.session.execute(sql)
		li = []
		dic = {}
		nor = 0
		for row in result:
			nor += 1
			dic = {}
			for i in range(len(row)):
				if(columns[i] not in dic):
					dic[columns[i]]=row[i]
			li.append(dic)
		if(nor == 1 or nor==0):
			return jsonify(dic)
		else:
			return jsonify(li)

	elif(delete=="True"):
		sql = text("DELETE FROM "+tabname+" WHERE "+where_string)
		result = db.session.execute(sql)
		db.session.commit()
		return jsonify({})



@app.route('/api/v1/db/write', methods=['POST'])
def write_data():
	req_data = request.get_json()
	values = req_data['insert']
	columns = req_data['column']
	tabname = req_data['table']
	update = req_data['update']
	column_string = ""
	for s in range(len(columns)):
		if(s!=len(columns)-1):
			column_string+=columns[s]+","
		else:
			column_string+=columns[s]
	value_string = ""
	for s in range(len(values)):
		if(s!=len(values)-1):
			if(isnumeric(values[s])):
				value_string += values[s] + ","
			else:
				value_string += "\'" + values[s] + "\'" + ","
		else:
			if(isnumeric(values[s])):
				value_string += values[s]
			else:
				value_string += "\'" + values[s] + "\'"
	if(update=="False"):
		sql = text("INSERT INTO "+tabname+" ("+column_string+") VALUES ("+value_string+")")
		try:
			db.session.execute(sql)
			db.session.commit()
			return jsonify({}),201
		except:
			db.session.rollback()
			return jsonify({}),400
	elif(update=="True"):
		where_string = req_data['where']
		sql = text("UPDATE "+tabname+" SET "+column_string+" = "+value_string+" WHERE "+where_string)
		db.session.execute(sql)
		try:
			db.session.execute(sql)
			db.session.commit()
			return jsonify({}),200
		except:
			db.session.rollback()
			return jsonify({}),204

@app.route('/api/v1/db/execute', methods=['POST'])
def execute_query():
	req_data = request.get_json()
	query = req_data['query']
	iswrite = req_data['write']
	if(iswrite == True):
		sql = text(query)
		try:
			db.session.execute(sql)
			db.session.commit()
			return jsonify({}),201
		except:
			db.session.rollback()
			return jsonify({}),400
	else:
		sql = text(query)
		result = db.session.execute(sql)
		li = []
		dic = {}
		nor = 0
		for row in result:
			nor += 1
			dic = {}
			dic = dict(row)
			li.append(dic)
		if(nor == 1 or nor==0):
			return jsonify(dic),200
		else:
			return jsonify(li),200

#Sign Up and Login
@app.route('/api/v1/users', methods=['POST','OPTIONS'])
@cross_origin(support_credentials = True)
def add_user():
	try:
		req_data = request.get_json()
		username = req_data['name']
		password = req_data['password']
		repeat_pass = req_data['repeat_pass']
		company_name = req_data['company_name']
		company_headquarters = req_data['company_headquarters']
		category = req_data['category']
		ceo = req_data['ceo']
		email = req_data['email']
		skills = req_data['skills']
		if(not(check_sha1(password))):
			return "Password in wrong format",200
		if(not(password == repeat_pass)):
			return "Password and repeat password do not match",200
		try:
			resp_data = {'table':"company",'columns':["company_id"],"where":"company_name="+company_name,"delete":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
			company_id = json.loads(response.text)['company_id']
			resp_data = {'table':"user",'columns':["user_id"],"where":"email="+email,"delete":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
			if(response.text != "{}\n"):
				return "Email already registered",200
			resp_data = {'insert':[username,email,password,"DEFAULT",company_name,str(company_id),skills],'column':["name","email","password","user_id","company","company_id","skills"],'table':"user","update":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
			return "Profile Created Successfully",200
		except:
			resp_data = {'insert':["DEFAULT",company_name,company_headquarters,category,ceo],'column':["company_id","company_name","headquarters","category","ceo"],'table':"company","update":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
			resp_data = {'table':"company",'columns':["company_id"],"where":"company_name="+company_name,"delete":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
			company_id = json.loads(response.text)['company_id']
			resp_data = {'table':"user",'columns':["user_id"],"where":"email="+email,"delete":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
			if(response.text != "{}\n"):
				return "Email already registered",200
			resp_data = {'insert':[username,email,password,"DEFAULT",company_name,str(company_id)],'column':["name","email","password","user_id","company","company_id"],'table':"user","update":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
			return "Profile Created Successfully",200
	except:
		try:
			req_data = request.get_json()
			password = req_data['password']
			email = req_data['email']
		except:
			return "Bad Request",400
		if(not(check_sha1(password))):
			return jsonify({"password in wrong format":True}),200
		resp_data = {'table':"user",'columns':["user_id"],"where":"email="+email,"delete":"False"}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
		if(response.text == "{}\n"):
			return "Email Not Registered",200
		resp_data = {'table':"user",'columns':["user_id"],"where":"email="+email+"AND password="+password,"delete":"False"}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
		if(response.text == "{}\n"):
			return "Invalid Password",200
		return "Login Successful",200


#Add Job
@app.route('/api/v1/jobs', methods=['POST','OPTIONS'])
@cross_origin(support_credentials = True)
def add_job():
	if(not(request.method=="POST" or request.method=="OPTIONS")):
		return jsonify({}),405
	try:
		req_data = request.get_json()
		company = req_data['company']
		username = req_data['username']
		city = req_data['city']
		country = req_data['country']
		specs = req_data['specs']
		term = req_data['term']
		lowsal = req_data['lowsal']
		highsal = req_data['highsal']
	except:
		return "Bad Request",400
	resp_data = {'table':"company",'columns':["company_id"],"where":"company_name="+company,"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	company_id = json.loads(response.text)['company_id']
	resp_data = {'table':"user",'columns':["user_id"],"where":"name="+username,"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	user_id = json.loads(response.text)['user_id']
	resp_data = {'insert':[city,country,specs,term,username,company,lowsal,highsal,str(user_id),str(company_id),"DEFAULT"],'column':["city","country","specs","term","publisher","company","lowsal","highsal","user_id","company_id","job_id"],'table':"job","update":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
	return "Job Created Successfully",200

#List Jobs Based on Search Parameters
@app.route('/api/v1/jobs', methods=['GET', 'OPTIONS'])
@cross_origin(support_credentials = True)
def list_jobs():
	try:
		location = request.args.get('location').replace("%20"," ")
		term = request.args.get('term').replace("%20"," ")
		specs = request.args.get('specs').replace("%20"," ")
	except:
		return "Bad Request",400
	print(location,term,specs)
	if(location != "Anywhere"):
		resp_data = {'table':"job",'columns':["city","country","specs","term","publisher","company","lowsal","highsal","user_id","company_id","job_id"],"where":"city="+location+"AND term="+term+"AND specs LIKE \'%"+specs+"%\'",'delete':"False"}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	else:
		resp_data = {'table':"job",'columns':["city","country","specs","term","publisher","company","lowsal","highsal","user_id","company_id","job_id"],"where":"term="+term+"AND specs LIKE \'%"+specs+"%\'",'delete':"False"}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	result = json.loads(response.text)
	if(isinstance(result,list)):
		num_records = str(len(result))
	else:
		num_records = str(1)
	s = "<div class=\"row mb-5 justify-content-center\"><div class=\"col-md-7 text-center\"><h2 class=\"section-title mb-2\">"+num_records+" Jobs Listed</h2></div></div>"
	if(isinstance(result,list)):
		for row in result:
			s += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <a href=\"job-single.html\"><img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\"></a>
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+term+"""</span>
			  <h2><a href=\"job-single.html\">"""+row['specs']+"""</a> </h2>
			  <p class=\"meta\">Publisher: <strong>"""+row['publisher']+"""</strong> In: <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-left\">
			  <h3>"""+row['city']+"""</h3>
			  <span class=\"meta\">"""+row['country']+"""</span>
			</div>
			<div class=\"col-md-3 text-md-right\">
			  <strong class=\"text-black\">"""+row['lowsal']+""" &mdash; """+row['highsal']+"""</strong>
			</div>
		  </div>"""
	else:
		row = result
		s += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <a href=\"job-single.html\"><img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\"></a>
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+term+"""</span>
			  <h2><a href=\"job-single.html\">"""+row['specs']+"""</a> </h2>
			  <p class=\"meta\">Publisher: <strong>"""+row['publisher']+"""</strong> In: <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-left\">
			  <h3>"""+row['city']+"""</h3>
			  <span class=\"meta\">"""+row['country']+"""</span>
			</div>
			<div class=\"col-md-3 text-md-right\">
			  <strong class=\"text-black\">"""+row['lowsal']+""" &mdash; """+row['highsal']+"""</strong>
			</div>
		  </div>"""
	return s,200

#Add Connection and Update Connection
@app.route('/api/v1/connections', methods=['POST'])
@cross_origin()
def add_connection():
	if(not(request.method=="POST")):
		return jsonify({}),405
	try:
		req_data = request.get_json()
		user2_email = req_data['email']
		user1_name = req_data['user1_name']
	except:
		try:
			req_data = request.get_json()
			approve_request_username = req_data['approve_request_username']
			username = req_data['username']
			query = "UPDATE connection SET is_approved=1 WHERE user1_name=\'"+approve_request_username+"\' AND user2_name=\'"+username+"\';"
			resp_data = {'query':query,'write':True}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
			return "Request Approved",200
		except:
			try:
				req_data = request.get_json()
				send_request_username = req_data['send_request_username']
				username = req_data['username']
				resp_data = {'table':"user",'columns':["user_id"],"where":"Name="+send_request_username,"delete":"False"}
				response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
				user2_id = json.loads(response.text)['user_id']
				resp_data = {'table':"user",'columns':["user_id"],"where":"name="+username,"delete":"False"}
				response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
				user1_id = json.loads(response.text)['user_id']
				resp_data = {'insert':[str(user1_id),str(user2_id),"DEFAULT",username,send_request_username,"0"],'column':["user1_id","user2_id","connection_id","user1_name","user2_name","is_approved"],'table':"connection","update":"False"}
				response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
				return "Request Sent",200
			except:
				return "Bad Request",400
	resp_data = {'table':"user",'columns':["user_id","Name"],"where":"email="+user2_email,"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	if(response.text == "{}\n"):
		return "Invalid Email",200
	user2_id = json.loads(response.text)['user_id']
	user2_name = json.loads(response.text)['Name']
	resp_data = {'table':"user",'columns':["user_id"],"where":"name="+user1_name,"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	user1_id = json.loads(response.text)['user_id']
	resp_data = {'insert':[str(user1_id),str(user2_id),"DEFAULT",user1_name,user2_name,"0"],'column':["user1_id","user2_id","connection_id","user1_name","user2_name","is_approved"],'table':"connection","update":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
	return "Connection Request Sent",200

#List Connections 
@app.route('/api/v1/connections', methods=['GET'])
@cross_origin()
def list_connections():
	if(not(request.method) == 'GET'):
		return jsonify({}),405
	try:
		fetchdata = request.args['fetchdata']
		username = request.args.get('username')
		query = "CREATE VIEW temp AS(SELECT user2_id as user_id FROM connection WHERE user1_name = \'"+username+"\' AND is_approved=1) UNION (SELECT user1_id as user_id FROM connection WHERE user2_name = \'"+username+"\' AND is_approved=1);"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name,email,company FROM user WHERE user_id IN (SELECT user_id FROM temp);"
		resp_data = {'query':query,'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		if(isinstance(result,list)):
			num_rows = str(len(result))
		else:
			if(response.text == "{}\n"):
				num_rows = str(0)
			else:
				num_rows = str(1)
		query = "DROP VIEW temp;"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		return_string = "<div class=\"row mb-5 justify-content-center\">\
		  <div class=\"col-md-7 text-center\">\
			<h2 class=\"section-title mb-2\">"+num_rows+" Connections Listed</h2>\
		  </div>\
		</div><div class=\"mb-5\">"
		if(isinstance(result,list)):
			for row in result:
				return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"send_message(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Message</strong>
			</div>
		  </div>"""
		elif(result):
			row = result 
			return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"send_message(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Message</strong>
			</div>
		  </div>"""
		return_string += "</div><hr>"
		query = "CREATE VIEW temp AS(SELECT user1_id as user_id FROM connection WHERE user2_name = \'"+username+"\' AND is_approved=0);"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name,email,company FROM user WHERE user_id IN (SELECT user_id FROM temp);"
		resp_data = {'query':query,'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		if(isinstance(result,list)):
			num_rows = str(len(result))
		else:
			if(response.text == "{}\n"):
				num_rows = str(0)
			else:
				num_rows = str(1)
		query = "DROP VIEW temp;"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		return_string += """<div class=\"row mb-5 justify-content-center\">
		  <div class=\"col-md-7 text-center\">
			<h2 class=\"section-title mb-2\">"""+num_rows+""" Pending Connection Requests</h2>
		  </div>
		</div><div class=\"mb-5\">"""
		if(isinstance(result,list)):
			for row in result:
				return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"approve_request(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Approve</strong>
			</div>
		  </div>"""
		elif(result):
			row = result 
			return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"approve_request(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Approve</strong>
			</div>
		  </div>"""
		return_string += "</div><hr>"
		query = "CREATE VIEW temp AS(SELECT user2_id as user_id FROM connection WHERE user1_name = \'"+username+"\' AND is_approved=0);"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name,email,company FROM user WHERE user_id IN (SELECT user_id FROM temp);"
		resp_data = {'query':query,'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		if(isinstance(result,list)):
			num_rows = str(len(result))
		else:
			if(response.text == "{}\n"):
				num_rows = str(0)
			else:
				num_rows = str(1)
		query = "DROP VIEW temp;"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		return_string += """<div class=\"row mb-5 justify-content-center\">
		  <div class=\"col-md-7 text-center\">
			<h2 class=\"section-title mb-2\">"""+num_rows+""" Connection Requests sent by you are Yet to Be Approved</h2>
		  </div>
		</div><div class=\"mb-5\">"""
		if(isinstance(result,list)):
			for row in result:
				return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
		  </div>"""
		elif(result):
			row = result 
			return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
		  </div>"""
		return_string += "</div><hr>"
		resp_data = {'table':"user",'columns':["skills","name","company","email"],"where":"None",'delete':"False"}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
		result = json.loads(response.text)
		resp_data = {'table':"company",'columns':["company_name","category"],"where":"None",'delete':"False"}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
		companies = json.loads(response.text)
		query = "CREATE VIEW temp AS (SELECT user1_name AS name FROM connection WHERE user2_name=\'"+username+"\') UNION (SELECT user2_name AS name FROM connection WHERE user1_name=\'"+username+"\');"
		resp_data = {"query":query,"write":True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name FROM user WHERE name NOT IN (SELECT * FROM temp);"
		resp_data = {"query":query,"write":False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		acc_names = json.loads(response.text)
		query = "DROP VIEW temp;"
		resp_data = {"query":query,"write":True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		li_names = []
		if(isinstance(acc_names,list)):
			for row in acc_names:
				li_names.append(row['name'])
		elif(acc_names):
			li_names.append(acc_names['name'])
		suggest_score = {}
		if(isinstance(result,list)):
			for row in result:
				if(row['name'] == username):
					user_company = row['company']
					user_skills = row['skills']
					#print(type(user_skills))
		else:
			user_company = result['company']
			user_skills = result['skills']
		if(isinstance(companies,list)):
			for row in companies:
				if(row['company_name'] == user_company):
					user_company_category = row['category']
		for row in result:
			if(row['name'] != username and len(li_names)!=0 and row['name'] in li_names):
				similar_score_skills = 0
				line = [word.strip() for word in list(map(str,row['skills'].split(",")))]
				user_skills_list = [word.strip() for word in list(map(str,user_skills.split(",")))]
				for i in user_skills_list:
					for j in line:
						#print(i,j)
						if(similar(i.lower(),j.lower()) > 0.8):
							similar_score_skills += 1
							break
				score = similar_score_skills
				for rowa in companies:
					if(rowa['company_name'] == row['company']):
						category = rowa['category']
				#^print(category,user_company_category)
				if(similar(category,user_company_category) > 0.8):
					score += 5
				if(row['company'] == user_company):
					score += 20
				suggest_score[row['name']] = score
		print(suggest_score)
		suggest_score_sorted = sorted(suggest_score, key = lambda k:-suggest_score[k])
		final_result = []
		if(len(suggest_score_sorted)!=0):
			for name in suggest_score_sorted:
				for row in result:
					if(row['name'] == name):
						final_result.append(row)
		num_of_rows = 0
		return_string += "<div class=\"row mb-5 justify-content-center\">\
			  <div class=\"col-md-7 text-center\">\
				<h2 class=\"section-title mb-2\">"+str(min(len(suggest_score_sorted),3))+" Connection Suggestions Listed</h2>\
			  </div>\
			</div><div class=\"mb-5\">"
		if(len(final_result)!=0):
			for row in final_result:
				if(num_of_rows<3):
					return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
					<div class=\"col-md-2\">
					  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
					</div>
					<div class=\"col-md-4\">
					  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
					  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
					  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
					</div>
					<div class=\"col-md-3 text-md-right\" onclick=\"send_request(\'"""+row['name']+"""\')\">
					  <strong class=\"text-black\">Send Request</strong>
					</div>
				  </div>"""
					num_of_rows += 1
				else:
					break
		return_string += "</div><hr>"
		return return_string,200
	except:
		search_tag = request.args.get('search_tag')
		username = request.args.get('username')
		query = "CREATE VIEW temp AS(SELECT user2_id as user_id FROM connection WHERE user1_name = \'"+username+"\' AND user2_name LIKE \'%"+search_tag+"%\' AND is_approved=1) UNION (SELECT user1_id as user_id FROM connection WHERE user2_name = \'"+username+"\' AND user1_name LIKE \'%"+search_tag+"%\' AND is_approved=1);"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name,email,company FROM user WHERE user_id IN (SELECT user_id FROM temp);"
		resp_data = {'query':query,'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		if(isinstance(result,list)):
			num_rows = str(len(result))
		else:
			if(response.text == "{}\n"):
				num_rows = str(0)
			else:
				num_rows = str(1)
		query = "DROP VIEW temp;"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		return_string = """<div class=\"row mb-5 justify-content-center\">
		  <div class=\"col-md-7 text-center\">
			<h2 class=\"section-title mb-2\">"""+num_rows+""" Connections Matched With Search Tag</h2>
		  </div>
		</div><div class=\"mb-5\">"""
		if(isinstance(result,list)):
			for row in result:
				return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"send_message(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Message</strong>
			</div>
		  </div>"""
		elif(result):
			row = result 
			return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"send_message(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Message</strong>
			</div>
		  </div>"""
		return_string += "</div><hr>"
		query = "CREATE VIEW temp AS(SELECT user1_id as user_id FROM connection WHERE user2_name = \'"+username+"\' AND user1_name LIKE \'%"+search_tag+"%\' AND is_approved=0);"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name,email,company FROM user WHERE user_id IN (SELECT user_id FROM temp);"
		resp_data = {'query':query,'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		if(isinstance(result,list)):
			num_rows = str(len(result))
		else:
			if(response.text == "{}\n"):
				num_rows = str(0)
			else:
				num_rows = str(1)
		query = "DROP VIEW temp;"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		return_string += """<div class=\"row mb-5 justify-content-center\">
		  <div class=\"col-md-7 text-center\">
			<h2 class=\"section-title mb-2\">"""+num_rows+""" Pending Connection Requests Matched With the Search Tag</h2>
		  </div>
		</div><div class=\"mb-5\">"""
		if(isinstance(result,list)):
			for row in result:
				return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"approve_request(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Approve</strong>
			</div>
		  </div>"""
		elif(result):
			row = result 
			return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
			<div class=\"col-md-3 text-md-right\" onclick=\"approve_request(\'"""+row['name']+"""\')\">
			  <strong class=\"text-black\">Approve</strong>
			</div>
		  </div>"""
		return_string += "</div><hr>"
		query = "CREATE VIEW temp AS(SELECT user2_id as user_id FROM connection WHERE user1_name = \'"+username+"\' AND user2_name LIKE \'%"+search_tag+"%\' AND is_approved=0);"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT name,email,company FROM user WHERE user_id IN (SELECT user_id FROM temp);"
		resp_data = {'query':query,'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		if(isinstance(result,list)):
			num_rows = str(len(result))
		else:
			if(response.text == "{}\n"):
				num_rows = str(0)
			else:
				num_rows = str(1)
		query = "DROP VIEW temp;"
		resp_data = {'query':query,'write':True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		return_string += """<div class=\"row mb-5 justify-content-center\">
		  <div class=\"col-md-7 text-center\">
			<h2 class=\"section-title mb-2\">"""+num_rows+""" Connection Requests sent by you that are Yet to Be Approved Matched With the Search Tag</h2>
		  </div>
		</div><div class=\"mb-5\">"""
		if(isinstance(result,list)):
			for row in result:
				return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
		  </div>"""
		elif(result):
			row = result 
			return_string += """<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">
			<div class=\"col-md-2\">
			  <img src=\"images/featured-listing-1.jpg\" alt=\"Image\" class=\"img-fluid\" onclick=\"showuserprofile(\'"""+row['email']+"""\')\">
			</div>
			<div class=\"col-md-4\">
			  <span class=\"badge badge-primary px-2 py-1 mb-3\">"""+row['email']+"""</span>
			  <h2 onclick=\"showuserprofile(\'"""+row['email']+"""\')\">"""+row['name']+"""</h2>
			  <p class=\"meta\"><strong>Company</strong> : <strong>"""+row['company']+"""</strong></p>
			</div>
		  </div>"""
		return_string += "</div><hr>"
		return return_string,200

#Send Message
@app.route('/api/v1/messages', methods=['POST'])
@cross_origin(support_credentials = True)
def add_message():
	if(not(request.method=="POST")):
		return jsonify({}),405
	try:
		req_data = request.get_json()
		user1_name = req_data['user1_name']
		user2_name = req_data['user2_name']
		content = req_data['content']
	except:
		return "Bad Request",400
	print(content)
	resp_data = {'table':"user",'columns':["user_id"],"where":"Name="+user1_name,"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	user1_id = json.loads(response.text)['user_id']
	resp_data = {'table':"user",'columns':["user_id"],"where":"Name="+user2_name,"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	if(response.text == "{}\n"):
		return "Invalid Username",200
	user2_id = json.loads(response.text)['user_id']
	resp_data = {'insert':[str(user1_id),str(user2_id),user1_name,user2_name,content.replace("\"",""),str(datetime.now()),"DEFAULT"],'column':["user1_id","user2_id","user1_name","user2_name","content","Date_Time","message_id"],'table':"messages","update":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
	resp = flask.Response("Message Sent Successfully")
	#resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp,200

#List Messages
@app.route('/api/v1/messages', methods=['GET'])
@cross_origin()
def list_messages():
	try:
		global prev_num_rows
		is_reload_needed = request.args['is_reload_needed']
		resp_data = {'query':"SELECT * FROM messages",'write':False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		result = json.loads(response.text)
		#return response.text,200
		if(isinstance(result,list)):
			curr_num_rows = len(result)
		else:
			if(response.text == "{}\n"):
				curr_num_rows = 0
			else:
				curr_num_rows = 1
		#return str(curr_num_rows),200
		if(curr_num_rows == prev_num_rows):
			return "No new message added",200
		else:
			prev_num_rows = curr_num_rows
			write_pickle()
			return "New Messages Added",200
	except:
		try:
			search_tag = request.args['search_tag']
			username = request.args.get('username')
			query = "select user1_name,content,Date_Time,max(message_id) from ((select f.user1_name, f.content, f.Date_Time,f.message_id from (SELECT user1_name, MAX(message_id) as mess_id FROM messages WHERE user2_name = \'"+username+"\' and (user1_name LIKE \'%"+search_tag+"%\' or content LIKE \'%"+search_tag+"%\') GROUP BY user1_name) as x inner join messages as f on f.user1_name = x.user1_name and f.message_id = x.mess_id and f.user1_name <> \'"+username+"\') UNION (select f.user2_name, f.content, f.Date_Time,f.message_id from (SELECT user2_name, MAX(message_id) as mess_id FROM messages WHERE user1_name = \'"+username+"\' and (user2_name LIKE \'%"+search_tag+"%\' or content LIKE \'%"+search_tag+"%\') GROUP BY user2_name) as x inner join messages as f on f.user2_name = x.user2_name and f.message_id = x.mess_id and f.user2_name <> \'"+username+"\') ORDER BY Date_Time DESC) as temp group by user1_name order by Date_Time"
			resp_data = {'query':query,'write':False}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
			if(response.text == "{}\n"):
				return "No Data to be Displayed",200
			result = json.loads(response.text)
			s = ""
			if(isinstance(result,list)):
				for row in result:
					s += """<div class=\"chat_list\" id=\""""+row['user1_name']+"""\" onclick=\"change_active(\'"""+row['user1_name']+"""\');\">
				<div class=\"chat_people\">
					<div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
					<div class=\"chat_ib\">
					<h5>"""+row['user1_name']+""" <span class=\"chat_date\">"""+row['Date_Time']+"""</span></h5>
					<p>"""+row['content']+"""</p>
					</div>
				</div>
				</div>"""
			else:
				row = result
				s += """<div class=\"chat_list\" id=\""""+row['user1_name']+"""\" onclick=\"change_active(\'"""+row['user1_name']+"""\');\">
				<div class=\"chat_people\">
					<div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
					<div class=\"chat_ib\">
					<h5>"""+row['user1_name']+""" <span class=\"chat_date\">"""+row['Date_Time']+"""</span></h5>
					<p>"""+row['content']+"""</p>
					</div>
				</div>
				</div>"""
			return s,200
		except:
			try:
				fetchdata = request.args['fetchdata']
				if(request.args.get('active_user')):
					active_user = request.args.get('active_user')
				else:
					active_user = ""
				username = request.args.get('username')
				query = "select user1_name,content,Date_Time,max(message_id) from ((select f.user1_name, f.content, f.Date_Time,f.message_id from (SELECT user1_name, MAX(message_id) as mess_id FROM messages WHERE user2_name = \'"+username+"\' GROUP BY user1_name) as x inner join messages as f on f.user1_name = x.user1_name and f.message_id = x.mess_id and f.user1_name <> \'"+username+"\') UNION (select f.user2_name, f.content, f.Date_Time,f.message_id from (SELECT user2_name, MAX(message_id) as mess_id FROM messages WHERE user1_name = \'"+username+"\' GROUP BY user2_name) as x inner join messages as f on f.user2_name = x.user2_name and f.message_id = x.mess_id and f.user2_name <> \'"+username+"\') ORDER BY Date_Time DESC) as temp group by user1_name order by Date_Time"
				resp_data = {'query':query,'write':False}
				response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
				if(response.text == "{}\n"):
					return "No Data to be Displayed",200
				result = json.loads(response.text)
				s = ""
				if(isinstance(result,list)):
					for row in result:
						if(active_user == row['user1_name']):
							s += """<div class=\"chat_list active_chat\" id=\""""+row['user1_name']+"""\" onclick=\"change_active(\'"""+row['user1_name']+"""\');\">
				<div class=\"chat_people\">
					<div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
					<div class=\"chat_ib\">
					<h5>"""+row['user1_name']+""" <span class=\"chat_date\">"""+row['Date_Time']+"""</span></h5>
					<p>"""+row['content']+"""</p>
					</div>
				</div>
				</div>"""
						else:
							s += """<div class=\"chat_list\" id=\""""+row['user1_name']+"""\" onclick=\"change_active(\'"""+row['user1_name']+"""\');\">
				<div class=\"chat_people\">
					<div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
					<div class=\"chat_ib\">
					<h5>"""+row['user1_name']+""" <span class=\"chat_date\">"""+row['Date_Time']+"""</span></h5>
					<p>"""+row['content']+"""</p>
					</div>
				</div>
				</div>"""

				else:
					row = result
					if(active_user == row['user1_name']):
						s += """<div class=\"chat_list active_chat\" id=\""""+row['user1_name']+"""\" onclick=\"change_active(\'"""+row['user1_name']+"""\');\">
				<div class=\"chat_people\">
					<div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
					<div class=\"chat_ib\">
					<h5>"""+row['user1_name']+""" <span class=\"chat_date\">"""+row['Date_Time']+"""</span></h5>
					<p>"""+row['content']+"""</p>
					</div>
				</div>
				</div>"""
					else:
						s += """<div class=\"chat_list\" id=\""""+row['user1_name']+"""\" onclick=\"change_active(\'"""+row['user1_name']+"""\');\">
				<div class=\"chat_people\">
					<div class=\"chat_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
					<div class=\"chat_ib\">
					<h5>"""+row['user1_name']+""" <span class=\"chat_date\">"""+row['Date_Time']+"""</span></h5>
					<p>"""+row['content']+"""</p>
					</div>
				</div>
				</div>"""
				return s,200
			except:
				try:
					display_messages = request.args['display_messages']
					active_user = request.args.get('active_user')
					username = request.args.get('username')
					query = "SELECT content,Date_Time,user1_name,user2_name FROM messages WHERE (user1_name = \'"+active_user+"\' and user2_name = \'"+username+"\') OR (user2_name = \'"+active_user+"\' and user1_name = \'"+username+"\') ORDER BY Date_Time"
					resp_data = {'query':query,'write':False}
					response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
					if(response.text == "{}\n"):
						return "No Data to be Displayed",200
					result = json.loads(response.text)
					s = ""
					if(isinstance(result,list)):
						for row in result:
							if(row['user1_name'] == active_user):
								s += """<div class=\"incoming_msg\">
			  <div class=\"incoming_msg_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
			  <div class=\"received_msg\">
				<div class=\"received_withd_msg\">
				  <p>"""+row['content']+"""</p>
				  <span class=\"time_date\">"""+row['Date_Time']+"""</span></div>
			  </div>
			</div>"""
							else:
								s += """<div class=\"outgoing_msg\">
			  <div class=\"sent_msg\">
				<p>"""+row['content']+"""</p>
				<span class=\"time_date\">"""+row['Date_Time']+"""</span> </div>
			</div>"""
								#print(row['content'])
					else:
						row = result
						if(row['user1_name'] == active_user):
							s += """<div class=\"incoming_msg\">
			  <div class=\"incoming_msg_img\"> <img src=\"https://ptetutorials.com/images/user-profile.png\" alt=\""""+row['user1_name']+"""\"> </div>
			  <div class=\"received_msg\">
				<div class=\"received_withd_msg\">
				  <p>"""+row['content']+"""</p>
				  <span class=\"time_date\">"""+row['Date_Time']+"""</span></div>
			  </div>
			</div>"""
						else:
							s += """<div class=\"outgoing_msg\">
			  <div class=\"sent_msg\">
				<p>"""+row['content']+"""</p>
				<span class=\"time_date\">"""+row['Date_Time']+"""</span> </div>
			</div>"""
					s += """<div class=\"type_msg\">
			<div class=\"input_msg_write\">
			  <input type=\"text\" class=\"write_msg\" placeholder=\"Type a message\" id=\"message_to_send\">
			  <button class=\"msg_send_btn\" type=\"button\" onclick=\"send_message();\"><i class=\"fa fa-paper-plane-o\" aria-hidden=\"true\"></i></button>
			</div>"""
					return s,200
				except:
					return "Bad Request",400

#Post Comment
@app.route('/api/v1/posts', methods=['POST'])
@cross_origin(support_credentials = True)
def add_post():
	if(not(request.method=="POST")):
		return jsonify({}),405
	try:
		req_data = request.get_json()
		username = req_data['username']
		content = req_data['content']
		post_id = req_data['post_id']
	except:
		try:
			req_data = request.get_json()
			username = req_data['username']
			query = "SELECT user_id FROM user WHERE name=\'"+username+"\';"
			resp_data = {"query":query,"write":False}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
			user_id = json.loads(response.text)['user_id']
			content = req_data['content']
			resp_data = {'insert':[content,"DEFAULT",str(user_id),"",str(datetime.now())],'column':["content","post_id","user_id","comments","Date_Time"],'table':"post","update":"False"}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=resp_data)
			return "Post Created",200
		except:
			return "Bad Request",400
	#print(content)
	resp_data = {"table":"post","columns":["comments"],"where":"post_id="+str(post_id),"delete":"False"}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=resp_data)
	comments = str(json.loads(response.text)['comments'])
	if(comments == ""):
		comments += username+"$$$"+str(datetime.now())+"$$$"+content
	else:
		comments += "+++"+username+"$$$"+str(datetime.now())+"$$$"+content
	query = "UPDATE post SET comments=\'"+comments+"\' WHERE post_id="+str(post_id)+";"
	resp_data = {'query':query,'write':True}
	response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
	return "Comment Posted Successfully",200

@app.route('/api/v1/posts', methods=['GET'])
@cross_origin()
def list_posts():
	try:
		fetchdata = request.args['fetchdata']
		username = request.args.get('username')
		query = "CREATE VIEW temp AS (SELECT user1_name AS name FROM connection WHERE user2_name=\'"+username+"\' AND is_approved=1) UNION (SELECT user2_name AS name FROM connection WHERE user1_name=\'"+username+"\' AND is_approved=1);"
		resp_data = {"query":query,"write":True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT user_id, name FROM user WHERE name IN (SELECT * FROM temp);"
		resp_data = {"query":query,"write":False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		if(response.text == "{}\n"):
			return "No Data to be Displayed",200
		acc_user_ids = json.loads(response.text)
		dic_user_ids = {}
		if(isinstance(acc_user_ids,list)):
			li_user_ids = [row['user_id'] for row in acc_user_ids]
			for row in acc_user_ids:
				dic_user_ids[row['user_id']] = row['name']
		else:
			li_user_ids = [acc_user_ids['user_id']]
			dic_user_ids[acc_user_ids['user_id']] = acc_user_ids['name']
		query = "DROP VIEW temp;"
		resp_data = {"query":query,"write":True}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		query = "SELECT post_id,user_id,content,comments,Date_Time FROM post;"
		resp_data = {"query":query,"write":False}
		response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
		if(response.text == "{}\n"):
			return "No Data to be Displayed",200
		result = json.loads(response.text)
		s = ""
		if(isinstance(result,list)):
			for row in result:
				if(row['comments'] == ""):
					num_com = str(0)
				else:
					num_com = str(len(list(map(str,row['comments'].split('+++')))))
				if(row['user_id'] in li_user_ids):
					if(len(row['content'])<50):
						content = row['content']
					else:
						content = row['content'][:50]+"..."
					s += """<div class=\"col-md-6 col-lg-4 mb-5\">
			<a href=\"post-single.html?post_id="""+str(row['post_id'])+"""\">"""+str(dic_user_ids[row['user_id']])+"""</a>
			<h3><a href=\"post-single.html?post_id="""+str(row['post_id'])+"""\" class=\"text-black\">"""+content+"""</a></h3>
			<div>"""+str(row['Date_Time'])+""" <span class=\"mx-2\">|</span> <a href=\"post-single.html?post_id="""+str(row['post_id'])+"""\">"""+num_com+""" Comments</a></div>
		  </div>"""
		else:
			row = result
			if(row['comments'] == ""):
				num_com = str(0)
			else:
				num_com = str(len(list(map(str,row['comments'].split('+++')))))
			if(row['user_id'] in li_user_ids):
				if(len(row['content'])<50):
					content = row['content']
				else:
					content = row['content'][:50]+"..."
				s += """<div class=\"col-md-6 col-lg-4 mb-5\">
			<a href=\"post-single.html?post_id="""+str(row['post_id'])+"""\">"""+str(dic_user_ids[row['user_id']])+"""</a>
			<h3><a href=\"post-single.html?post_id="""+str(row['post_id'])+"""\" class=\"text-black\">"""+content+"""</a></h3>
			<div>"""+str(row['Date_Time'])+""" <span class=\"mx-2\">|</span> <a href=\"post-single.html?post_id="""+str(row['post_id'])+"""\">"""+num_com+""" Comments</a></div>
		  </div>"""
		return s,200
	except:
		try:
			post_id = request.args['post_id']
			query = "SELECT user_id,content,comments,Date_Time FROM post WHERE post_id="+post_id+";"
			resp_data = {"query":query,"write":False}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
			result = json.loads(response.text)
			query = "SELECT name FROM user WHERE user_id="+str(result['user_id'])+";"
			resp_data = {"query":query,"write":False}
			response = requests.post("http://127.0.0.1:5000/api/v1/db/execute",json=resp_data)
			username = json.loads(response.text)['name']
			s = """<h3>"""+username+"""</h3>"""+result['content']
			row = result
			if(row['comments'] == ""):
				num_com = str(0)
			else:
				num_com = str(len(list(map(str,row['comments'].split('+++')))))
			s += """<div class=\"pt-5\"><h3 class=\"mb-5\">"""+str(num_com)+""" Comments</h3>
			  <ul class=\"comment-list\">"""
			if(num_com!=str(0)):
				li_comments = list(map(str,row['comments'].split('+++')))
				for comment in li_comments:
					row_comment = list(map(str,comment.split('$$$')))
					s += """<li class=\"comment\">
					  <div class=\"vcard bio\">
						<img src=\"images/person_2.jpg\" alt=\"Image placeholder\">
					  </div>
					  <div class=\"comment-body\">
						<h3>"""+row_comment[0]+"""</h3>
						<div class=\"meta\">"""+row_comment[1]+"""</div>
						<p>"""+row_comment[2]+"""</p>
					  </div>
					</li>"""
			s += "</ul></div>"
			return s,200
		except:
			return "Bad Request",400

if __name__ == "__main__":
	app.run(host = 'localhost', debug=True)