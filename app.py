from flask import Flask, render_template, request, redirect, url_for, session, escape, flash
import database
import os, urllib2, json
import pymongo
import re
from pymongo import MongoClient
from urllib2 import urlopen
from pymongo import Connection


app=Flask(__name__)
app.secret_key = os.urandom(24)
abc = urllib2.Request("https://data.cityofnewyork.us/resource/mreg-rk5p.json")
sat = urllib2.Request("https://data.cityofnewyork.us/resource/zt9s-n5aj.json")
text = urlopen(abc)
sattext = urlopen(sat)
text2 = text.read()
sattext2 = sattext.read()
schoolslist = json.loads(text2)
schoolslist2 = json.loads(sattext2)
dbn_codes = []
c= Connection()
client = MongoClient()
db = client.leaf
c.drop_database(db)
users = db.users
schoolinfo=db.one
schoolinfo.insert(schoolslist)
schoolinfo.insert(schoolslist2)
shortened = schoolinfo.aggregate([{"$group": {
        "_id": "$dbn",
        "printed_school_name": {"$first": "$printed_school_name"},
        "program_name": {"$addToSet": "$program_name"},
        "program_code": {"$addToSet": "$program_code"},
        "directory_page_": {"$first": "$directory_page_"},
        "borough": {"$first": "$borough"},
        "interest_area": {"$addToSet": "$interest_area"},
        "writing_mean": {"$addToSet": "$writing_mean"},
        "critical_reading_mean": {"$addToSet": "$critical_reading_mean"},
        "mathematics_mean": {"$addToSet": "$mathematics_mean"},
        "number_of_test_takers": {"$addToSet": "$number_of_test_takers"},
        }}])
#schoolinfo.group(key={"dbn":1},
schoolinfo2 = db.two
schoolinfo2.insert(shortened['result'])
#for a in schoolslist:
#        dbn_codes.append(a['dbn'])


#highschools= urlopen(request)
#response = highschools.read()

@app.route("/",methods=["GET","POST"])
@app.route("/login",methods=["GET","POST"])
def login():

        if request.method=="GET":
                #print urlopen(abc).read()
                return render_template("login.html")
                #print response
        else:
                #print response
                username = request.form["username"]
                password = request.form["password"]
                button = request.form["b"]
                if button == "Login":
			user = users.find_one({'username': username})
                        if user == None:
                                flash("Not a username buddy")
                                return redirect(url_for('login'))
			elif user['password'] != password:
				flash("Password and username do not match")
				return redirect(url_for('login'))
			else:
				flash("Welcome to Leaf")
				return redirect(url_for('user_home', username=username))
		else: 
			return redirect(url_for('register'))
def add_user(username, password, emailaddress, gender) : #, age
	user = {
		'username' : username, 
		'password' : password,
        	'emailaddress' : emailaddress,
        	'gender' : gender,
		#'age' : age
	}
	return users.insert(user)
@app.route("/register",methods=["GET","POST"])
def register():
	if request.method=="GET":
                a = []
                for x in range(0,123):
                        a.append(x)
                return render_template("register.html", a = a)
	else: 
        	button = request.form["b"]
		if button == "Login":
        	        return redirect(url_for('login'))
         	username = request.form["username"]
        	password = request.form["password"]
		gender = request.form["gender"]
        	emailaddress = request.form["emailaddress"]
		if users.find_one({'username': username}) != None:
			flash("The username you submitted is already taken, please try again.")
			return redirect(url_for('register'))
		if users.find_one({'emailaddress': emailaddress}) != None:
			flash("The email you submitted already has an account tied to it, please try again.")
			return redirect(url_for('register'))

		add_user(username, password, emailaddress, gender) #, age
		session['username'] = username
		session['password'] = password
		session['gender'] = gender
		session['emailaddress'] = emailaddress
		flash("You've sucessfully registered, now login!")
		return redirect(url_for('login'))
@app.route("/user/<username>",methods=["GET","POST"])
def user(username):
        if request.method=="GET":
                return render_template("user.html", username = username)
        else:
                return render_template("user.html", username = username)

@app.route('/logout')
def logout():
    	session.pop('username', None)
    	session.pop('password', None)
    	session.pop('first_name', None)
    	session.pop('last_name', None)
	flash("You have successfully logged out")
    	return redirect(url_for('login'))

@app.route("/home/<username>",methods=["GET","POST"])
def user_home(username):
	if request.method=="GET":
		return render_template("home.html", username = username)
	else: 
		button = request.form["b"]
		if button=="Logout":
                	return redirect(url_for("logout"))
@app.route('/school/<code>', methods=["GET","POST"])
def school(code = None):
        if request.method == "GET":
                session.clear()
                #print "YES!"  
                #print schoolinfo.find_one({"dbn": code})
                a = schoolinfo2.find_one({"_id": code})
                print schoolinfo2     
                if a != None:
                        #print "YES! 2--------------------------------"
                        #name = schoolslist[n]['printed_school_name']
                        #program_code = schoolslist[n]['program_code']
                        return render_template('schools.html',name=a['printed_school_name'], 
                                dbn=a['_id'], 
                                program_code=a['program_name'],
                                critread=a['critical_reading_mean'],
                                mathematics= a['mathematics_mean'],
                                writing= a['writing_mean'],
                                Interest= a['interest_area']) #program_code=program_code, dbn=dbn)
                else:
                        return render_template('user.html')
        else:
                field = request.form['searchbar']
                return redirect(url_for("search", field=field ))

@app.route('/search/', methods=["GET","POST"])
def search(results=None):
        field = request.args.get('field')
        #print field
        results = []
        #print "2.0"
        fieldstring = ".*" + field + ".*"
        regx = re.compile(fieldstring, re.IGNORECASE)
        n = schoolinfo2.find({ "$or": [
                {"printed_school_name": {"$regex": regx}},
                {"program_code":{"$regex": regx}},
                {"directory_page_":{"$regex": regx}},
                {"dbn":{"$regex": regx}},
                {"urls":{"$regex": regx}},
                {"borough":{"$regex": regx}},
                {"selection_method":{"$regex": regx}},
                {"program_name":{"$regex": regx}}]})
        for x in n:
                if not (x in results):
                        results.append(x)
        #print "This is the array length" + str(len(results))
        #print "3.0--------------------------------------------------"
        #print results
        #print "4.0-----------------------------------------------------------"
        if request.method == "GET":
                #print "GOT TO THIS STEP-----------------"
        #results = request.args.get("results")
        #for x in results:
                #print x
                #print "\n"
        #print 'These are the session results'
        #print escape(session['results'])
                return render_template("search.html",results=results, Search="'"+field+"'")




if __name__=="__main__":
        app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
        app.debug = True
        app.run()
