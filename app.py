from flask import Flask, render_template, request, session, redirect, jsonify
import jinja2
import os

import datetime
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'A0Zr98jhigFASF553mN]LWX/,?RT'

MONGO_URL = os.environ.get('MONGOHQ_URL')
client = MongoClient(MONGO_URL)
db = client.app25605883
collection = db.points

@app.route('/')
def index():
	green = 0
	yellow = 0
	red = 0
	blue = 0

	for event in collection.find():
		team = event['team']
		points = int(event['points'])
		if (team == "Green"):
			green+= points
		elif (team == "Yellow"):
			yellow+= points
		elif (team == "Red"):
			red+=points
		else:
			blue+=points

	return render_template("index.html", blue=blue, red=red, yellow=yellow, green=green, events=collection.find().sort('_id',-1).limit(10))

@app.route('/scores')
def scores():
	green = 0
	yellow = 0
	red = 0
	blue = 0

	for event in collection.find():
		team = event['team']
		points = int(event['points'])
		if (team == "Green"):
			green+= points
		elif (team == "Yellow"):
			yellow+= points
		elif (team == "Red"):
			red+=points
		else:
			blue+=points	
	
	return jsonify(blue=blue,green=green,red=red,yellow=yellow, current=collection.count())

@app.route('/events', methods=['GET'])
def events():
	return render_template('events.html', events=collection.find().sort('_id',-1))

@app.route('/table')
def table():
	return render_template('table.html', events=collection.find().sort('_id',-1).limit(10))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'admin' in session:
		return redirect('/admin')

	if request.method == 'POST':
		password = request.form['password']
		if not password == 'ihatefishsticks':
			return redirect('/login')
		session['admin'] = password
		return redirect('/admin')
	
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('admin', None)

	return redirect('/login')

@app.route('/admin', methods=['GET','POST'])
def admin():
	if not 'admin' in session:
		return redirect('/login')

	if request.method == 'POST':
		team=request.form['team']
		event=request.form['event']
		points=request.form['points']
		
		#check if event exists
		if collection.find({ "event" : event}).count() > 0:
			return render_template('admin.html', events=collection.find().sort('_id',-1), error="That event already exists! Try again with a different name.")

		#check if user entered a number for points field
		try:
			int(points)
		except ValueError:
			return render_template('admin.html', events=collection.find().sort('_id',-1), error="You must use numbers for the points field.")

		event = {"event":event,"team":team,"points":points}
		event_id = collection.insert(event)

		return redirect('/admin')

	return render_template('admin.html', events=collection.find().sort('_id',-1))

@app.route('/change', methods=['GET', 'POST'])
def change():
	#returning redirect will cause it do go to the specificed URL
	if request.method == 'POST':
		team=request.form['team']
		event=request.form['event']
		points=request.form['points']
		try:
			int(points)
		except ValueError:
			return render_template('admin.html', events=collection.find().sort('_id',-1), error="You must use numbers for the points field.")
		
		if request.form['submit'] == "REMOVE":
			collection.remove({"event" : event})
			return redirect('/admin')
		
		print ("changed %s %s %s" % (team, event, points))
		
		collection.update({ "event" : event }, { "$set" : { "team": team, "event": event, "points": points }}, upsert=False)
		
		return redirect('/admin')

	return redirect('/admin')

@app.route('/testrun', methods=['GET','POST'])
def testrun():
	return render_template('testrun.html')
	
if __name__ == '__main__':
	#this code starts the web app, it can be found at http://localhost:8000
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port,debug=True)