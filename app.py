from flask import Flask, render_template, request, Response
import jinja2
import os

import datetime
import pymongo
from pymongo import MongoClient
from functools import wraps

app = Flask(__name__)

MONGO_URL = os.environ.get('MONGOHQ_URL')
client = MongoClient(MONGO_URL)
db = client.app25605883
collection = db.points

def check_auth(password):
	return password == 'ihatefishsticks'

def authenticate():
	return Response('Could not verify your access level for that URL.\n'
		'You have to login with proper credentials',401,{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated
	
@app.route('/')
def index():
	#render_template will render the index.html found in the template folder
	green = 0
	yellow = 0
	red = 0
	blue = 0
	for event in collection.find():
		team = event['team']
		points = int(event['points'])
		if (team == "green"):
			green+= points
		elif (team == "yellow"):
			yellow+= points
		elif (team == "red"):
			red+=points
		else:
			blue+=points
	return render_template("index.html", blue=blue, red=red, yellow=yellow, green=green, events=collection.find())

@app.route('/change', methods=['GET', 'POST'])
def change():
	#returning redirect will cause it do go to the specificed URL
	if request.method == 'POST':

		team=request.form['team']
		event=request.form['event']
		points=request.form['points']
		if request.form['submit'] == "REMOVE":
			collection.remove({"event" : event})
			return redirect('/admin')
		print ("changed %s %s %s" % (team, event, points))
		collection.update({ "event" : event }, { "$set" : { "team": team, "event": event, "points": points }}, upsert=False)
		return redirect('/admin')
	return redirect('/admin')

@app.route('/admin', methods=['GET','POST'])
@requires_auth
def admin():
	if request.method == 'POST':
		team=request.form['team']
		event=request.form['event']
		points=request.form['points']


		event = {"event":event,"team":team,"points":points}
		event_id = collection.insert(event)

		return render_template('admin.html', events=collection.find())
	return render_template('admin.html', events=collection.find())

if __name__ == '__main__':
	#this code starts the web app, it can be found at http://localhost:8000
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port,debug=True)