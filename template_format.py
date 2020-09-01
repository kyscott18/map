import csv

def template_to(file):
	template = []
	with open(file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			template.append(row)
	return template