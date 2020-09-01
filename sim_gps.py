import socket
import json
import csv
import garmin_format as gf

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(message)
	#recieve confirmation 
while(True):
	data = gf.garmin_to(['route1_4.csv'])
	print("Enter the route number:")
	x = input()
	#TODO: receive confirmation that the route number is valid
	rn = json.dumps(x)
	client.send(rn.encode(FORMAT))
	for point in data[0]:
		send(json.dumps(point))
	send(DISCONNECT_MESSAGE)
	break
