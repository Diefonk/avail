from flask import Flask, render_template, redirect, request
from time import time_ns, strftime
from datetime import datetime, timedelta
from random import choice
from uuid import uuid4
from json import dump, load
from os.path import exists

app = Flask(__name__)

@app.route("/")
def index():
	titles = ["D&D", "movie marathon", "video hangout", "project meeting", "playing games", "picnic"]
	today = strftime("%Y-%m-%d")
	with open("static/timezones.json", "r") as file:
		timezones = load(file)
	return render_template("index.html", title_example = choice(titles), today = today, timezones = timezones)

@app.route("/post-new", methods = ["POST"])
def post_new():
	data = {}
	data["title"] = request.form["title"]
	data["start"] = request.form["start"]
	data["length"] = int(request.form["length"]) * 24 * int(request.form["resolution"])
	data["timezone"] = int(request.form["timezone"])
	data["interval"] = 60 / int(request.form["resolution"])
	data["replies"] = []
	id = str(uuid4())
	with open("data/schedule/" + id + ".json", "w") as file:
		dump(data, file, separators = (',', ':'))
	return redirect("/" +  id)

@app.route("/<uuid:id>")
def schedule(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		return render_template("error.html", error = "Invalid ID!")
	with open(path, "r") as file:
		data = load(file)
	return render_template("schedule.html", data = data, id = str(id), has_replies = len(data["replies"]) > 0)

@app.route("/<uuid:id>/reply")
def reply(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		return render_template("error.html", error = "Invalid ID!")
	with open(path, "r") as file:
		data = load(file)
	data["replyTimezone"] = data["timezone"]
	data["format"] = "24"
	#data["name"]
	with open("static/timezones.json", "r") as file:
		timezones = load(file)
	times = []
	timestamp = datetime.strptime(data["start"], "%Y-%m-%d")
	timestamp = timestamp + timedelta(minutes = data["timezone"] - data["replyTimezone"])
	date = ""
	for index in range(data["length"]):
		time = {}
		time["index"] = index
		if data["format"] == "12":
			time["label"] = datetime.strftime(timestamp, "%I:%M %p")
		else:
			time["label"] = datetime.strftime(timestamp, "%H:%M")
		#time["checked"]
		next_date = datetime.strftime(timestamp, "%B %d, %A")
		if date != next_date:
			time["date"] = next_date
			date = next_date
		times.append(time)
		timestamp = timestamp + timedelta(minutes = data["interval"])
	return render_template("reply.html", data = data, id = str(id), timezones = timezones, times = times)

@app.route("/<uuid:id>/edit")
def edit(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		return render_template("error.html", error = "Invalid ID!")
	with open(path, "r") as file:
		data = load(file)
	return render_template("edit.html", data = data, id = str(id))

@app.route("/<uuid:id>/post-reply", methods = ["POST"])
def post_reply(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		return render_template("error.html", error = "Invalid ID!")
	with open(path, "r") as file:
		data = load(file)
	reply = {}
	reply["key"] = uuid4().hex
	reply["name"] = request.form["name"]
	reply["timezone"] = request.form["timezone"]
	times = ""
	for index in range(data["length"]):
		if str(index) in request.form:
			times += "1"
		else:
			times += "0"
	reply["times"] = times
	data["replies"].append(reply)
	with open(path, "w") as file:
		dump(data, file, separators = (',', ':'))
	return redirect("/" + str(id) + "/replied?key=" + reply["key"])

@app.route("/feedback")
def feedback():
	return render_template("feedback.html", title = "Feedback")

@app.route("/post-feedback", methods = ["POST"])
def post_feedback():
	with open("data/feedback/" + str(time_ns()) + ".txt", "w") as file:
		text = request.form["useful"] + "\n"
		text += request.form["useful-comment"] + "\n"
		text += request.form["easy"] + "\n"
		text += request.form["easy-comment"]
		file.write(text)
	return redirect("/thanks")

@app.route("/thanks")
def thanks():
	return render_template("thanks.html", title = "Feedback")

if __name__ == "__main__":
	app.run()
