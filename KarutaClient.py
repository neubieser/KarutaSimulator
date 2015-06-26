import socket
import sys
import time



class KarutaClient:
	def __init__(self, HOST, PORT):
		self.player = ''
		self.HOST = HOST
		self.PORT = PORT
		received = self.sendMessage('join')
		

		if received == 'p1':
			self.player = 'p1'
			print 'connected as p1'
		elif received == 'p2':
			self.player = 'p2'
			print 'connected as p2'
		else:
			print 'could not connect'
	def sendMessage(self,message):
		if message == 'join' or not self.player == '':
			message = self.player+message
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			try:
			    # Connect to server and send data
			    sock.connect((self.HOST, self.PORT))
			    sock.sendall(message)

			    # Receive data from the server and shut down
			    received = sock.recv(1024)
			finally:
				sock.close()
			return received
		else:
			return ''

'''
HOST, PORT = "localhost", 9999
cl = KarutaClient()

cl.sendMessage('hello')
cl.sendMessage('wassup')
response = True
count = 0
while not response == '':
	response = cl.sendMessage('get,'+str(count))
	print response
	count = count + 1
'''