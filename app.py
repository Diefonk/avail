from flask import Flask, render_template, redirect, request, make_response, abort
from time import time_ns, strftime
from datetime import datetime, timedelta
from random import choice
from uuid import uuid4
from json import dump, load
from os.path import exists
import traceback
from os import listdir

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
		abort(404)
	with open(path, "r") as file:
		data = load(file)
	times = []
	if len(data["replies"]) > 0:
		previous_time = False
		timestamp = datetime.strptime(data["start"], "%Y-%m-%d")
		date = ""
		for index in range(data["length"]):
			next_time = True
			for reply in data["replies"]:
				if reply["times"][index:index + 1] != "1":
					next_time = False
					break
			if not previous_time and next_time:
				date = datetime.strftime(timestamp, "%B %d, %A ")
				times.append(date + datetime.strftime(timestamp, "%H:%M - "))
			elif previous_time and not next_time:
				next_date = datetime.strftime(timestamp, "%B %d, %A ")
				if date != next_date:
					times[-1] += next_date
				times[-1] += datetime.strftime(timestamp, "%H:%M")
			previous_time = next_time
			timestamp = timestamp + timedelta(minutes = data["interval"])
		if previous_time:
			next_date = datetime.strftime(timestamp, "%B %d, %A ")
			if date != next_date:
				times[-1] += next_date
			times[-1] += datetime.strftime(timestamp, "%H:%M")
	with open("static/timezones.json", "r") as file:
		timezones = load(file)
	return render_template("schedule.html", data = data, id = str(id), has_replies = len(data["replies"]) > 0, reply_range = range(len(data["replies"])), times = times, has_overlap = len(times) > 0, timezones = timezones)

@app.route("/<uuid:id>/reply")
def reply(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		abort(404)
	with open(path, "r") as file:
		data = load(file)
	edit_reply = None
	if "key" in request.args:
		for reply in data["replies"]:
			if reply["key"] == request.args["key"]:
				edit_reply = reply
				break
		if edit_reply is None:
			return redirect("/" + str(id) + "/edit?invkey=" + request.args["key"])
		data["key"] = request.args["key"]
		data["name"] = edit_reply["name"]
		data["replyTimezone"] = edit_reply["timezone"]
		data["format"] = edit_reply["format"]
	else:
		data["replyTimezone"] = data["timezone"]
		data["format"] = "24"
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
		if edit_reply and edit_reply["times"][index:index + 1] == "1":
			time["checked"] = True
		next_date = datetime.strftime(timestamp, "%B %d, %A")
		if date != next_date:
			time["date"] = next_date
			date = next_date
		times.append(time)
		timestamp = timestamp + timedelta(minutes = data["interval"])
	return render_template("reply.html", data = data, id = str(id), timezones = timezones, times = times)

@app.route("/<uuid:id>/post-reply", methods = ["POST"])
def post_reply(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		abort(404)
	with open(path, "r") as file:
		data = load(file)
	reply = {}
	if "key" in request.form:
		reply["key"] = request.form["key"]
	else:
		reply["key"] = uuid4().hex
	reply["name"] = request.form["name"]
	reply["timezone"] = int(request.form["timezone"])
	reply["format"] = request.form["format"]
	times = ""
	for index in range(data["length"]):
		if str(index) in request.form:
			times += "1"
		else:
			times += "0"
	reply["times"] = times
	if "key" in request.form:
		for index, existing_reply in enumerate(data["replies"]):
			if reply["key"] == existing_reply["key"]:
				data["replies"][index] = reply
				break
	else:
		data["replies"].append(reply)
	with open(path, "w") as file:
		dump(data, file, separators = (',', ':'))
	return redirect("/" + str(id) + "/replied?key=" + reply["key"])

@app.route("/<uuid:id>/replied")
def replied(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		abort(404)
	with open(path, "r") as file:
		data = load(file)
	if "key" in request.args:
		return render_template("replied.html", data = data, id = str(id), key = request.args["key"])
	else:
		return redirect("/" + str(id))

@app.route("/<uuid:id>/edit")
def edit(id):
	path = "data/schedule/" + str(id) + ".json"
	if not exists(path):
		abort(404)
	with open(path, "r") as file:
		data = load(file)
	invkey = None
	if "invkey" in request.args:
		invkey = request.args["invkey"]
	return render_template("edit.html", data = data, id = str(id), invkey = invkey)

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

@app.route("/rss/feedback.xml")
def rssFeedback():
	items = listdir("data/feedback")
	rss = render_template("rss.xml", title = "avail feedback", folder = "feedback", items = items)
	response = make_response(rss)
	response.mimetype = "application/rss+xml"
	return response

@app.route("/rss/error.xml")
def rssError():
	items = listdir("data/logs")
	rss = render_template("rss.xml", title = "avail error logs", folder = "logs", items = items)
	response = make_response(rss)
	response.mimetype = "application/rss+xml"
	return response

@app.errorhandler(404)
def page_not_found(error):
	return render_template("error.html", title = "404 - Page not found", text = "This page may have been deleted, or it may have never existed."), 404

@app.errorhandler(500)
def internal_server_error(error):
	with open("data/logs/" + str(time_ns()) + ".txt", "w") as file:
		file.write(traceback.format_exc())
	return render_template("error.html", title = "500 - Internal server error", text = "An error log was sent to the developer."), 500

if __name__ == "__main__":
	app.run()
