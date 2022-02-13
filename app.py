from flask import Flask, render_template, redirect, request
from time import time_ns, strftime
from random import choice
from uuid import uuid4
from json import dump, load
from os.path import exists

app = Flask(__name__)

@app.route("/")
def index():
	titles = ["D&D", "movie marathon", "video hangout", "project meeting", "playing games", "picnic"]
	today = strftime("%Y-%m-%d")
	return render_template("index.html", title_example = choice(titles), today = today)

@app.route("/post-new", methods = ["POST"])
def post_new():
	data = {}
	data["title"] = request.form["title"]
	data["start"] = request.form["start"]
	data["length"] = request.form["length"]
	data["resolution"] = request.form["resolution"]
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
	return render_template("schedule.html", data = data)

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
