class KarutaSingleClient:
	def __init__(self):
		self.state = []
		self.player = 'p1'

	def sendMessage(self,message):
		messageInfo = message.split(',')
                if messageInfo[0] == 'getmove':
                        stateIndex = int(messageInfo[1])
                        if stateIndex < len(self.state):
                                return self.state[stateIndex]
                        else:
                                return ''
                elif messageInfo[0] == 'swap':
                        self.state.append(message)
                elif messageInfo[0] == 'rerack':
                        self.state.append(message)
                else:
                        self.state.append('p1'+','+message)
        def oppSendMessage(self,message):
                self.state.append(message)
