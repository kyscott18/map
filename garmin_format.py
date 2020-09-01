import csv

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

def garmin_to(files):
	#date, time, lat, lon
	datas = []
	for file in files:
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
		datas.append(data)
	return datas