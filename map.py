import csv
from math import radians, cos, sin, asin, sqrt

class Loop:
	def __init__(self, day, start_time): 
		self.day = day
		self.start_time = start_time
		self.data = []

def csv_to(file):
	template = []
	with open(file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			template.append(row)
	return template

def date_spliter(date):
	vec = date.split(',')
	day = vec[0]
	time = vec[1].split()
	n = time[0].split(':')
	secs = (3600 * int(n[0])) + (60 * int(n[1])) + int(n[2])
	if int(n[0]) >= 1 and int(n[0]) < 12 and time[1] == 'PM':
		secs += 60 * 60 * 12
	return day, secs

def position_spliter(position):
	loco = position.split()
	lat = float(loco[0][1:3])
	lat += float(loco[1][0:6])/60
	if loco[0][0] == 'S':
		lat *= -1
	lon = float(loco[2][1:3])
	lon += float(loco[3][0:6])/60
	if loco[2][0] == 'W':
		lon *= -1
	return lat, lon

def garmin_to(file):
	#date, time, lat, lon
	data = []
	with open(file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0 or row[6] == '':
				line_count += 1
			else:
				day, secs = date_spliter(row[1])
				lat, lon = position_spliter(row[7])
				heading = row[6].split("°")
				data.append([day, secs, lat, lon, int(heading[0])])
				line_count += 1
	return data

def distance(lat1, lat2, lon1, lon2):
	lon1 = radians(float(lon1))
	lon2 = radians(float(lon2))
	lat1 = radians(float(lat1))
	lat2 = radians(float(lat2))
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * asin(sqrt(a))
	r = 6371000
	return(c * r)

def match(template, template_index, data, data_index):
	#find the index of the data point that matches the cordinates of the template point
	#starting at the data index, go through the data points until one is found within 25 meters
	for i in range(60):
		if data_index >= len(data):
			print("out of points")
			return data_index
		if distance(data[data_index][2], template[template_index][0], data[data_index][3], template[template_index][1]) < 28:
			return data_index
		data_index += 1
	print("miss")
	return data_index

def avg(master):
	average = []
	for p in range(len(master[0].data)):
		a = 0 
		for l in master:
			a += l.data[p]
		average.append(a)
	for i in range(len(average)):
		average[i] /= len(master)
	return average

def t_avg(master, t):
	time_average = []
	count = 0
	for p in range(len(master[0].data)):
		a = 0 
		for l in master:
			#if time is in the range
			if l.time > t - (60*30) and l.time < t + (60 * 30)
				count += 1
				a += l.data[p]
			if a == 0:
				print("Error, no matching time data")
		average.append(a)
	for i in range(len(average)):
		average[i] /= count
	return average

def main():
	master = []
	#FORMAT
	template = csv_to('output-2.csv')
	data = garmin_to('route1.csv')

	#find the start of the loop
	data_index = 0
	template_index = 0
	time_hold = 0
	loop = Loop('0', 0)
	#for each point in data
	while data_index < len(data):
		#find data_index of point matching the next template
		data_index = match(template, template_index, data, data_index)

		if (template_index == 0):
			loop = Loop(data[data_index][0], data[data_index][1])
			template_index += 1
			time_hold = data[data_index][1]
		elif template_index == len(template) - 1:
			loop.data.append(data[data_index][1] - time_hold)
			master.append(loop)
			template_index = 0
		else: 
			loop.data.append(data[data_index][1] - time_hold)
			time_hold = data[data_index][1]
			template_index += 1
		data_index += 1

	#get data from avg, most recent, and avg at the same time
	average = avg(master)
	most_recent = master[-1].data
	time_average = t_avg(master)
	#TRAIN


	
if __name__ == "__main__": 
	main()
