from flask import Flask, render_template, request, redirect
import jinja2
import os

import datetime
import pymongo
from pymongo import MongoClient

#making a new Flask app
app = Flask(__name__)
MONGO_URL = os.environ.get('MONGOHQ_URL')
client = MongoClient(MONGO_URL)
db = client.app25605883
collection = db.points
#@app.route binds a function to specific url
@app.route('/')
#this function tells the app what to do when it loads the main page
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

@app.route('/change')
def change():
	#returning redirect will cause it do go to the specificed URL
	if request.method == 'POST':
		team=request.form['team']
		event=request.form['event']
		points=request.form['points']
		collection.update({ event : event }, { $set : { team: team, event: event, points: points }})
		return redirect('/admin')
	return redirect('/admin')

#in this app.route we allow POST requests to be sent to /post
@app.route('/post', methods=['GET','POST'])
def post():
	#here we are checking if the request coming in is a post request
	if request.method == 'POST':
		return render_template('post.html')
	#this will run when the user simply goes to the URL
	return render_template('get.html')

@app.route('/admin', methods=['GET','POST'])
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