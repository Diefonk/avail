from flask import Flask, render_template, redirect, request
import time

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/feedback")
def feedback():
	return render_template("feedback.html", title = "Feedback")

@app.route("/post-feedback", methods = ["POST"])
def post_feedback():
	with open("data/feedback/" + str(time.time_ns()) + ".txt", "w") as file:
		text = request.form["useful"] + "\n"
		text += request.form["useful-comment"] + "\n"
		text += request.form["easy"] + "\n"
		text += request.form["easy-comment"]
		file.write(text)
	return redirect("/thanks")

@app.route("/thanks")
def thanks():
	return render_template("thanks.html", title = "Feedback submitted")

if __name__ == "__main__":
	app.run()
