import SocketServer
import socket
import random

class KarutaServerState():
	def __init__(self):
		self.state = {}
		self.state['p1'] = []
		self.state['p2'] = []
		self.state['moves'] = []
		cards = [i for i in range(1,101)]
		random.shuffle(cards)
		mystr = ''
		for i in cards:
			mystr = mystr + str(i)+','
		random.shuffle(cards)
		readingOrder = ''
		for i in cards:
			readingOrder = readingOrder + str(i)+','
		readingOrder = readingOrder[:-1]
		self.cards = mystr + readingOrder
		self.p1 = None
		self.p2 = None
		

ks = KarutaServerState()

class MyTCPHandler(SocketServer.BaseRequestHandler):



    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
    	self.data = self.request.recv(1024).strip()
    	if self.data == 'join':
	    	if ks.p1 is None:
	    		ks.p1 = self
	    	elif ks.p2 is None:
	    		ks.p2 = self
	    	if ks.p1 is self:
	    		print 'p1 connected'
        		self.request.sendall('p1,'+ks.cards)
        	elif ks.p2 is self:
        		print 'p2 connected'
        		self.request.sendall('p2,'+ks.cards)
        else:
        	player = self.data[:2]
        	message = self.data[2:]
        	self.respond(player,message)
    def respond(self,player, message):
    	messageInfo = message.split(',')
    	if messageInfo[0] == 'get':
    		stateIndex = int(messageInfo[1])
    		state = ks.state[player]
    		if stateIndex < len(state):
    			self.request.sendall(state[stateIndex])
    		else:
    			self.request.sendall('')
    	elif messageInfo[0] == 'getmove':
    		stateIndex = int(messageInfo[1])
    		state = ks.state['moves']
    		if stateIndex < len(state):
    			self.request.sendall(state[stateIndex])
    	elif messageInfo[0] == 'swap':
    		ks.state['moves'].append(message)
    		print ks.state['moves']
    	elif messageInfo[0] == 'rerack':
    		ks.state['moves'].append(message)
    		print ks.state['moves']

    	else:
    		print player + ' sent '+message
    		if player == 'p1':
    			ks.state['moves'].append(player+','+message)
    		elif player == 'p2':
    			ks.state['moves'].append(player+','+message)
    		self.request.sendall('success')


class MyTCPServer(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


if __name__ == "__main__":
    with open('server.config','r') as f:
	data = f.readlines()
	HOST = data[0][:-1]
	PORT = int(data[1])
    print 'Running server on '+HOST+':'+str(PORT)
    #HOST, PORT = "192.168.1.88", 3478

    # Create the server, binding to localhost on port 9999
    server = MyTCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
