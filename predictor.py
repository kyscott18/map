import csv
import json
import socket
import threading
import garmin_format as gf
import template_format as tf
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from sklearn import linear_model

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
ROUTES_FILE =  "routes.csv"
ROUTES = []

class Loop:
	def __init__(self, day, start_time): 
		self.day = day
		self.start_time = start_time
		self.data = []

class Route:
	def __init__(self, route_num, template, data_files):
		self.route_num = int(route_num)
		self.template = tf.template_to(template)
		self.data_files = data_files
		self.master = data_to_loops(self.template, gf.garmin_to(self.data_files))
		self.reg = linear_model.LinearRegression()
		print("[FORMATTING FOR PREDICTION]")
		actual, df = format(self.master)
		print("[FITTING DATA]")
		self.reg.fit(df, actual)

class Bus:
	data_index = 0
	template_index = 0
	time_hold = 0
	loop = Loop('0', 0)

	def __init__(self, route_num):
		self.route = route_factory(route_num)

	def match(self, point):
		#find data_index of point matching the next template
		if distance(point[2], self.route.template[self.template_index][0], point[3], self.route.template[self.template_index][1]) < 28:
			# print("point matched")
			# if data_index >= len(data):
			# 	break
			#print(len(self.template), self.template_index)
			if (self.template_index == 0):
				self.loop = Loop(point[0], point[1])
				self.time_hold = point[1]
				self.predict()
				self.template_index += 1
			elif self.template_index == len(self.route.template) - 1:
				self.loop.data.append(point[1] - self.time_hold)
				#master.append(loop)
				self.predict()
				self.template_index = 0
			else: 
				self.loop.data.append(point[1] - self.time_hold)
				self.time_hold = point[1]
				self.predict()
				self.template_index += 1
			# else:
			# 	print("point not matched")

				#get ingredients for predictions
				# cc(reg, df, actual)
				# print(stder(reg, df, actual))
				#change size of message bytes

	def predict(self):
		if self.template_index == len(self.route.master[0].data):
			print(0)
			return
		average = single_avg(self.route.master, self.template_index)
		most_recent = self.route.master[-1].data[self.template_index]
		time_average = single_t_avg(self.route.master, self.time_hold, self.template_index)
		print(self.route.reg.predict([[average, most_recent, time_average]]))

class Server:
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def __init__(self):
		self.server.bind(ADDR)

	def start(self):
		self.server.listen()
		print(f"[LISTENING] server is listening on {SERVER}")
		while(True):
			conn, addr = self.server.accept()
			thread = threading.Thread(target=self.handle_client, args=(conn,addr))
			thread.start()
			#print(f"[ACTIVE CONNECTIONS] {threading,activeCount() - 1}")

	def handle_client(self, conn, addr):
		print(f"[NEW CONNECTION] {addr} connected.")
		route_num = conn.recv(HEADER).decode(FORMAT)
		rn = int(route_num[1:-1])
		bus = Bus(rn)
		#TODO: process the data for the routes
		#predictor = Predictor()
		connected = True
		print("[RECEIVING MESSAGES]")
		while connected:
			msg_length = conn.recv(HEADER).decode(FORMAT)
			if msg_length:
				msg_length = int(msg_length)
				msg = conn.recv(msg_length).decode(FORMAT)
				if msg  == DISCONNECT_MESSAGE:
					print("[DISCONNECT_MESSAGE RECEIVED] disconnecting")
					break
				data = json.loads(msg)
				#match data and predict
				bus.match(data)
				#predictor.driver(data)

		conn.close()

def route_factory(route_num):
	for route in ROUTES:
		route_num = int(route_num)
		route.route_num = int(route.route_num)
		if str(route_num) == str(route.route_num):
			return route
	print("ROUTE NOT FOUND")
	return 0

def load_routes():
	with open(ROUTES_FILE) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			ROUTES.append(Route(row[0], row[1], row[2:]))

def data_to_loops(template, datas):
	master = []
	for data in datas:
		print(f"\t[NEW FILE] from {data[0][0], data[0][1]}")
		data_index = 0
		template_index = 0
		time_hold = 0
		loop = Loop('0', 0)
		#for each point in data
		while data_index < len(data):
			#find data_index of point matching the next template
			data_index = match(template, template_index, data, data_index)

			if data_index >= len(data):
				break

			if (template_index == 0):
				loop = Loop(data[data_index][0], data[data_index][1])
				template_index += 1
				time_hold = data[data_index][1]
			elif template_index == len(template) - 1:
				loop.data.append(data[data_index][1] - time_hold)
				master.append(loop)
				template_index = 0
				print("\t\t[LOOP ADDED]")
			else: 
				loop.data.append(data[data_index][1] - time_hold)
				time_hold = data[data_index][1]
				template_index += 1
			data_index += 1
	return master

def single_avg(master, template_index):
	a = 0 
	for l in master:
		a += l.data[template_index]
	return (a / len(master))

def single_t_avg(master, time, template_index):
	count = 0
	a = 0 
	for l in master:
	#if time is in the range
		if l.start_time > time - (60*30) and l.start_time < time + (60 * 30):
			count += 1
			a += l.data[template_index]
		if a == 0:
			print("Error, no matching time data")
	return (a / count)

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
			#print("out of points")
			return data_index
		if distance(data[data_index][2], template[template_index][0], data[data_index][3], template[template_index][1]) < 28:
			return data_index
		data_index += 1
	#print("miss")
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
			if l.start_time > t - (60*30) and l.start_time < t + (60 * 30):
				count += 1
				a += l.data[p]
			if a == 0:
				print("Error, no matching time data")
		time_average.append(a)
	for i in range(len(time_average)):
		time_average[i] /= count
	return time_average

def cc(reg, df, actual):
	return reg.score(df, actual)

def stder(reg, df, actual):
	se = 0
	for i in range(len(df)):
		se += (reg.predict([df[i]]) - actual[i])**2
	se = se/(len(df)-2)
	se = sqrt(se)
	return se

def format(master):
	actual = master[-1].data
	time = master[-1].start_time
	master.pop()
	average = avg(master)
	most_recent = master[-1].data
	time_average = t_avg(master, time)

	#format
	df = []
	for i in range(len(actual)):
		df.append([average[i], most_recent[i], time_average[i]])
	return actual, df

def main():
	print("[STARTING] server is starting...")
	load_routes()
	# import pdb; pdb.set_trace()
	server = Server()
	server.start()

if __name__ == "__main__": 
	main()