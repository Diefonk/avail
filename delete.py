from datetime import datetime
from json import load
from os import listdir, remove, path

directory = path.dirname(path.abspath(__file__)) + "/data/schedule/"
schedules = listdir(directory)
for schedule in schedules:
	with open(directory + schedule, "r") as file:
		data = load(file)
	if (datetime.strptime(data["delete"], "%Y-%m-%d") - datetime.today()).days <= 0:
		remove(directory + schedule)
