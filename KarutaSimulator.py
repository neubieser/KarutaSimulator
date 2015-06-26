from __future__ import print_function
from Tkinter import Tk, W, E, BOTH
from ttk import Frame, Button, Label, Style
from ttk import Entry
from PIL import ImageTk, Image
import threading
import random
import time
from subprocess import call
from collections import deque

from KarutaClient import KarutaClient

#p1 is on top
#p2 is on bottom
#no comments
#Karuta.state can be 'taking', 'move-select-start', 'move-select-stop'

NUM_COLS = 16

scale = .14
#cards = [2,4,5,6,8,9,10,11,13,14,15,16,17,18,20,21,22,23,24,26,27,28,29,32,33,34,35,37,38,40,41,42,46,47,48\
#         ,49,50,51,54,55,57,59,61,62,63,65,66,67,68,70,71,73,74,75,76,77,81,83,85,87,89,90,91,92,93,94,96,97\
#         ,98,99,100,72,82,44,60,95,36,84,80,53,86]
cards = [i for i in range(1,101)]
order = [(NUM_COLS,1),(1,1),(NUM_COLS-1,1),(2,1),(NUM_COLS,2),(NUM_COLS-1,2),(NUM_COLS,3),(1,2),(NUM_COLS-2,1),(3,1),(2,2),(NUM_COLS-2,2),(1,3),(NUM_COLS-1,3),\
         (2,3),(NUM_COLS-2,3),(NUM_COLS-3,1),(3,2),(NUM_COLS-3,2),(3,3),(4,1),(NUM_COLS-4,1),(NUM_COLS-5,1),(4,2),(4,3)]
with open('Audio/Verse2/durations.txt','r') as f:
    durations = f.readlines()
    verse2Durations = [int(1000*float(i)) for i in durations]


def assignCards(cards,order):
    cpy = cards[:]
    ass1 = {}
    ass2 = {}
    p1 = cpy[:len(cpy)/2]
    p2 = cpy[len(cpy)/2:]
    p1 = p1[:25]
    p2 = p2[:25]
    for i in range(len(p1)):
        ass1[order[i]] = p1[i]
    for i in range(len(p2)):
        ass2[order[i]] = p2[i]
    return ass1,ass2

class Card:
    def __init__(self, number):
        self.number = number
        img = Image.open('Images/'+str(number)+'.png')
        img = img.resize((int(625*scale), int(873*scale)),Image.ANTIALIAS)
        self.width,self.height = img.size
        self.baseimg = img
        self.img = ImageTk.PhotoImage(img)
    def flip(self):
        self.baseimg = self.baseimg.rotate(180)
        self.img = ImageTk.PhotoImage(self.baseimg)


class Karuta(Frame):

    def pollForUpdates(self):
        response = self.client.sendMessage('get,'+str(self.client.next))
        responseMove = self.client.sendMessage('getmove,'+str(self.client.nextMove))
        if not response == '':
            self.client.next = self.client.next + 1
            self.queue.append(response)
        if not responseMove == '':
            self.client.nextMove = self.client.nextMove + 1
            self.queue.append(responseMove)
        self.parent.after(200,self.pollForUpdates)

    def processUpdates(self):
        if not len(self.queue) == 0:
            item = self.queue[0]
            success = self.process(item)
            if success:
                self.queue.popleft()
        self.parent.after(200,self.processUpdates)

    def process(self,message):
        info = message.split(',')
        print(message)
        if info[1] == 'took' and not info[0] == self.client.player:
            timeTaken = float(info[2])
            numFaults = info[3]
            if timeTaken < time.time() - self.startTime and timeTaken < self.delta:
                self.changeState('waiting')
                text = "Opponent won the card. Faults: you="+str(self.faultCount)+", opp="+numFaults
                self.client.sendMessage('took,'+str(self.delta)+','+str(self.faultCount))
                self.infoLabel.config(text=text)
                pic = self.model[self.activeCardRow][self.activeCardCol]
                pic.pack_forget()
                pic.isNone = True
                return True
            elif timeTaken > self.delta:
                text = "You won the card. Faults: you="+str(self.faultCount)+", opp="+numFaults
                self.infoLabel.config(text=text)
                self.changeState('waiting')
                return True
            else:
                return False
        elif info[1] == 'ready' and not info[0] == self.client.player:
            self.opponentReady = True
            if self.state == 'ready':
                self.infoLabel.config(text="Both players are ready.")
                self.update()
            return True
        elif info[1] == 'ready' and info[0] == self.client.player:
            self.changeState('ready')
            if self.opponentReady:
                self.infoLabel.config(text="Both players are ready.")
            else:
                self.infoLabel.config(text="Waiting for opponent.")
            self.update()
            return True
        elif info[0] == 'swap':
            arr = [int(k) for k in info[1:]]
            self.doSwap((arr[0],arr[1]),(arr[2],arr[3]))
            return True
        elif info[0] == 'rerack':
            self.performRerack(info[1])
            return True
        elif info[1] == 'play':
            if self.state == 'ready' and self.opponentReady:
                self.playNextAudio()
            return True
        elif info[1] == 'ghost' and not info[0] == self.client.player:
            numFaults = info[2]
            self.changeState('waiting')
            text = "Karufuda. Faults: you="+str(self.faultCount)+", opp="+numFaults
            self.infoLabel.config(text=text)
            return True
        elif info[0] == self.client.player:
            return True
        else:
            print(message)
            return True


  
    def __init__(self, parent,multiplayer=False):
        self.activeCard = 0
        self.startTime = -1
        self.client = KarutaClient("99.66.147.56", 3478)
        cards = self.client.cards
        self.queue = deque([])
        self.opponentReady = False
        self.fgrid = [[None for col in range(NUM_COLS)] for row in range(6)]
        self.model = [[None for col in range(NUM_COLS)] for row in range(6)]
        self.faultCount = 0
        Frame.__init__(self, parent)   
        self.activeCard = 0
        self.parent = parent
        self.cardsLeft = self.client.order
        self.initUI(cards)
        self.changeState('waiting') 

        if multiplayer:
            self.client.next = 0
            self.client.nextMove = 0
            self.pollForUpdates()
            self.processUpdates()
        

    def playNextAudio(self):
        if self.state == 'ready' and self.opponentReady:
            self.delta = 100000
            self.opponentReady = False
            self.faultCount = 0
            self.cheated = False
            self.infoLabel.config(text='Now Playing')
            self.startTime = time.time()
            if self.cardsLeft:
                previousCard = self.activeCard
                randomCard = self.cardsLeft.pop()
                self.activeCard = randomCard
                self.activeCardRow = -1
                for row in range(6):
                    for col in range(NUM_COLS):
                        if self.model[row][col].card.number == self.activeCard and not self.model[row][col].isNone:
                            self.activeCardRow = row
                            self.activeCardCol = col
                            break
                print(randomCard)
                def playCurrentVerse2():
                    call(['afplay','Audio/Verse2/Audio'+str(previousCard)+'.mp3'])

                t= threading.Thread(target=playCurrentVerse2, args=())
                t.start()
                self.parent.after(verse2Durations[previousCard],self.playNextVerse1)

                if self.activeCardRow == -1:
                    self.parent.after(10000+verse2Durations[previousCard],self.sendFouls)

        elif self.state == 'taking':
            randomCard = self.activeCard
            def doInBackground():
                call(['afplay','Audio/Verse1/Audio'+str(randomCard)+'.m4a'])
            t= threading.Thread(target=doInBackground, args=())
            t.start()
        else:
            self.infoLabel.config(text='Not everyone is ready yet')

    def reveal(self):
        self.cheated = True
        if self.activeCardRow == -1:
            self.infoLabel.config(text='karafuda')
        else:
            self.infoLabel.config(text='Row,Col = ('+str(self.activeCardRow)+','+str(self.activeCardCol)+')')
        self.update()
    def sendFouls(self):
        self.client.sendMessage('ghost,'+str(self.faultCount))
    def playNextVerse1(self):
        self.changeState('taking')
        def doPlay():

            call(['afplay','Audio/Verse1/Audio'+str(self.activeCard)+'.m4a'])
        t = threading.Thread(target=doPlay, args=())
        t.start()

    def rerack(self):
        if self.state == 'waiting' or self.state == 'move-select-start' or self.state == 'move-select-stop':
            self.client.sendMessage('rerack,'+self.client.player)
    def performRerack(self,player):
        self.opponentReady = False
        self.changeState('waiting')
        print('reracking')
        if player == 'p1':
            rows = [3,4,5]
        else:
            rows = [0,1,2]
        moved = True
        while moved:
            moved = False
            for row in rows:
                for col in reversed(range(NUM_COLS/2)):
                    if self.model[row][col].isNone and not self.model[row][col+1].isNone:
                        self.doSwap((row,col),(row,col+1))
                        moved = True
                        # self.model[row][col+1].isNone = True
                        # self.model[row][col+1].pack_forget()
                        # self.model[row][col].isNone = False
                        # self.model[row][col].image = self.model[row][col+1].image
                        # self.model[row][col].config(image=self.model[row][col].image)
                        # self.model[row][col].pack(fill=BOTH)
                for col in reversed([NUM_COLS-i-1 for i in range(NUM_COLS/2)]):
                    if self.model[row][col].isNone and not self.model[row][col-1].isNone:
                        self.doSwap((row,col),(row,col-1))
                        moved = True
                        # self.model[row][col-1].isNone = True
                        # self.model[row][col-1].pack_forget()
                        # self.model[row][col].isNone = False
                        # self.model[row][col].image = self.model[row][col-1].image
                        # self.model[row][col].config(image=self.model[row][col].image)
                        # self.model[row][col].pack(fill=BOTH)
            self.update()



            
        
    def initUI(self,cards):
      
        self.parent.title("Karuta")
        
        Style().configure("TButton")
        
        p1,p2 = assignCards(cards,order)
        for row in range(6):
            for col in range(NUM_COLS):
                if (NUM_COLS-col,row+1) in p1:
                    self.setCard(p1[(NUM_COLS-col,row+1)],row,col)
                elif (col+1,6-row) in p2:
                    self.setCard(p2[(col+1,6-row)],row,col)
                else:
                    self.setCard(-1,row,col)
        self.p1 = [i for i in p1.values()]
        self.p2 = [i for i in p2.values()]

        def move():
            if self.state == 'move-select-start' or self.state == 'move-select-stop':
                self.changeState('waiting')
                self.moveButton.config(text='Move')
                self.infoLabel.config(text='Move cancelled')
            elif self.state == 'waiting':
                self.changeState('move-select-start')
                self.infoLabel.config(text='Select card to move')
                self.moveButton.config(text='Cancel')
            self.update()
        b = Button(self,text='Move',command=move)
        b.grid(row=0,column=8)
        self.moveButton = b


        def playNextAudio():
            if self.state == 'taking':
                self.playNextAudio()
            else:
                self.client.sendMessage('play')
        b = Button(self,text='Play',command=playNextAudio)
        self.playButton = b
        b.grid(row=0, column=9)

        def reveal():
            self.reveal()

        b = Button(self,text='Reveal',command=reveal)
        b.grid(row=0, column=10)

        def rerack():
            self.rerack()

        b = Button(self,text='Rerack',command=rerack)
        b.grid(row=0, column=11)

        def ready():
            if self.startTime < time.time() - 11:
                if self.state == 'taking' and not self.activeCardRow == -1:
                    self.infoLabel.config(text="Card has not been found yet.")
                    self.update()
                else:
                    self.moveButton.config(text="Move")
                    self.client.sendMessage('ready')
                    self.update()

        b = Button(self,text='Ready',command=ready)
        b.grid(row=0, column=12)

        l = Label(self,text='')
        l.grid(row=0, column=0, columnspan=5)
        self.infoLabel = l
        self.pack()

                
      
    def setCard(self,cardnum,row,col):
        dodel = False
        if cardnum == -1:
            dodel = True
            cardnum = 1
        card = Card(cardnum)
        f = Frame(self, height = card.height, width = card.width)
        if (row == 2 and self.client.player == 'p1') or (row == 3 and self.client.player == 'p2'):
            f.config(height = card.height+20)
        if self.client.player == 'p1':
            f.grid(row=row+1, column=col)
        else:
            f.grid(row=6-row, column=NUM_COLS-col)
        f.pack_propagate(0)

        self.fgrid[row][col] = f
        
        pic = Label(f)
        if row <= 2:
            card.flip()
        if self.client.player == 'p2':
            card.flip()
        pic.config(image=card.img)
        pic.image = card.img
        pic.row = row
        pic.col = col
        pic.card = card
        
        def clicked(pic,ins,card):
            if ins.state == 'taking' and not pic.isNone:
                if card.number == ins.activeCard:
                    endTime = time.time()
                    self.delta = round(endTime-self.startTime,2)
                    print(self.delta)
                    print("Got in "+str(self.delta))
                    self.client.sendMessage('took,'+str(self.delta)+','+str(self.faultCount))

                    self.changeState('waiting')

                    pic.pack_forget()
                    ins.model[pic.row][pic.col].isNone = True
                elif self.activeCardRow == -1 or not (pic.row <= 2) == (self.activeCardRow <= 2):
                    self.faultCount = 1
            elif ins.state == 'move-select-start':
                ins.movingPic = (pic.row, pic.col)
                print('moving card:')
                print(ins.movingPic)
                if ((self.client.player == 'p1' and pic.row > 2) or (self.client.player == 'p2' and pic.row <= 2))\
                    and not pic.isNone:
                    ins.infoLabel.config(text="Card chosen. Select destination.")
                    ins.state = 'move-select-stop'

                else:
                    ins.infoLabel.config(text="Can't move that. Select a different card to move.")
                ins.moveButton.config(text="Cancel")

            elif ins.state == 'move-select-stop':
                print('to:')
                print((pic.row, pic.col))
                if ((self.client.player == 'p1' and pic.row <= 2) or (self.client.player == 'p2' and pic.row > 2))\
                    and not pic.isNone:
                    ins.infoLabel.config(text="Illegal move. Select a different card to move.")
                else:
                    ins.swapCards(self.movingPic,(pic.row, pic.col))
                    ins.infoLabel.config(text="Move completed. Select next card.")

                ins.state = 'move-select-start'




        
        f.bind("<Button-1>",lambda e,pic=pic,self=self,card=card:clicked(pic,self,card))
        pic.bind("<Button-1>",lambda e,pic=pic,self=self,card=card:clicked(pic,self,card))
        pic.pack(fill=BOTH)
        self.model[row][col] = pic

        if dodel:
            pic.pack_forget()
            self.model[row][col].isNone = True

        else:
            self.model[row][col].isNone = False

    def swapCards(self,pos1, pos2):
        row1,col1 = pos1
        row2,col2 = pos2
        if (self.client.player == 'p2' and row1 <=2 and row2 <=2) or\
            (self.client.player == 'p1' and row1 > 2 and row2 > 2):

            self.client.sendMessage('swap,'+str(row1)+','+str(col1)+','+str(row2)+','+str(col2))
        elif (self.client.player == 'p2' and row1 <= 2 and row2 > 2 \
            and not self.model[row1][col1].isNone and self.model[row2][col2].isNone) or \
            (self.client.player == 'p1' and row1 > 2 and row2 <= 2 \
            and not self.model[row1][col1].isNone and self.model[row2][col2].isNone):
            self.client.sendMessage('swap,'+str(row1)+','+str(col1)+','+str(row2)+','+str(col2))

    def doSwap(self,pos1, pos2):
        self.opponentReady = False
        if self.state == 'ready':
            self.changeState('waiting')
            self.infoLabel.config(text="Reconfirm when ready.")
        row1,col1 = pos1
        row2,col2 = pos2
        pic1 = self.model[row1][col1]
        pic2 = self.model[row2][col2]
        card1 , card2 = pic1.card , pic2.card
        if not (row1 <= 2) == (row2 <= 2):
            card1.flip()
            card2.flip()
        pic1.card , pic2.card = pic2.card , pic1.card
        pic1.image , pic2.image = pic1.card.img , pic2.card.img
        pic1.isNone , pic2.isNone = pic2.isNone , pic1.isNone
        if not pic1.isNone:
            pic1.config(image=pic1.image)
            pic1.pack(fill=BOTH)
        else:
            pic1.pack_forget()
        if not pic2.isNone:
            pic2.config(image=pic2.image)
            pic2.pack(fill=BOTH)
        else:
            pic2.pack_forget()
        self.update()
    def changeState(self,state):
        self.state = state
        if state == 'waiting':
            self.playButton.config(state=DISABLED)
            self.moveButton.config(state=NORMAL,text="Move")
        elif state == 'ready':
            self.playButton.config(state=NORMAL)
            self.moveButton.config(state=DISABLED,text="Move")
        elif state == 'move-select-start' or state == 'move-select-stop':
            self.playButton.config(state=DISABLED)
            self.moveButton.config(state=ACTIVE)
        elif state == 'taking':
            self.moveButton.config(state=DISABLED,text="Move")
            self.playButton.config(state=NORMAL)



                
                


def main():
  
    root = Tk()
    app = Karuta(root,multiplayer=True)
    root.mainloop()

main()
