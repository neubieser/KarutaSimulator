from __future__ import print_function
from Tkinter import Tk, W, E, BOTH
from ttk import Frame, Button, Label, Style
from ttk import Entry
from PIL import ImageTk, Image
import threading
import random
import time
from subprocess import call

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

def randomAssignCards(cards,order):
    cpy = cards[:]
    random.shuffle(cpy)
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
        response = self.client.sendMessage('get,'+self.client.next)
        if not response == '':
            self.client.next = self.client.next + 1
            self.process(response)
        self.parent.after(200,self.pollForUpdates)
  
    def __init__(self, parent,multiplayer=False):



        self.fgrid = [[None for col in range(NUM_COLS)] for row in range(6)]
        self.model = [[None for col in range(NUM_COLS)] for row in range(6)]
        self.state = 'waiting' 
        self.faultCount = 0
        Frame.__init__(self, parent)   
        self.activeCard = 0
        self.parent = parent
        self.cardsLeft = [i for i in range(1,101)]
        random.shuffle(self.cardsLeft)
        self.initUI()
        if multiplayer:
            self.client = KarutaClient("localhost", 9999)
            self.client.next = 0
            self.pollForUpdates()
        

    def playNextAudio(self):
        if self.state == 'ready':
            self.state = 'taking'
            self.faultCount = 0
            self.cheated = False
            self.infoLabel.config(text='Now Playing')
            self.startTime = time.time()
            if self.cardsLeft:
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
                def doInBackground():
                    call(['afplay','Audio/Audio'+str(randomCard)+'.m4a'])
                t= threading.Thread(target=doInBackground, args=())
                t.start()
        elif self.state == 'taking':
            randomCard = self.activeCard
            def doInBackground():
                call(['afplay','Audio/Audio'+str(randomCard)+'.m4a'])
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

    def rerack(self):
        if self.state == 'waiting':
            moved = True
            while moved:
                moved = False
                for row in range(6):
                    for col in reversed(range(NUM_COLS/2)):
                        if self.model[row][col].isNone and not self.model[row][col+1].isNone:
                            self.swapCards((row,col),(row,col+1))
                            moved = True
                            # self.model[row][col+1].isNone = True
                            # self.model[row][col+1].pack_forget()
                            # self.model[row][col].isNone = False
                            # self.model[row][col].image = self.model[row][col+1].image
                            # self.model[row][col].config(image=self.model[row][col].image)
                            # self.model[row][col].pack(fill=BOTH)
                    for col in reversed([NUM_COLS-i-1 for i in range(NUM_COLS/2)]):
                        if self.model[row][col].isNone and not self.model[row][col-1].isNone:
                            self.swapCards((row,col),(row,col-1))
                            moved = True
                            # self.model[row][col-1].isNone = True
                            # self.model[row][col-1].pack_forget()
                            # self.model[row][col].isNone = False
                            # self.model[row][col].image = self.model[row][col-1].image
                            # self.model[row][col].config(image=self.model[row][col].image)
                            # self.model[row][col].pack(fill=BOTH)
                self.update()



            
        
    def initUI(self):
      
        self.parent.title("Karuta")
        
        Style().configure("TButton")
        
        p1,p2 = randomAssignCards(cards,order)
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
            if self.state == 'move-select-start':
                self.state = 'null'
                self.moveButton.config(text='Move')
                self.infoLabel.config(text='Move cancelled')
            elif self.state == 'waiting':
                self.state = 'move-select-start'
                self.infoLabel.config(text='Select card to move')
                self.moveButton.config(text='Cancel')
            self.update()
        b = Button(self,text='Move',command=move)
        b.grid(row=0,column=8)
        self.moveButton = b


        def playNextAudio():
            self.playNextAudio()
        b = Button(self,text='Play',command=playNextAudio)
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
            if self.state == 'taking' and not self.activeCardRow == -1:
                self.infoLabel.config(text="Card has not been found yet.")
                self.update()
            else:
                self.infoLabel.config(text="Ready.")
                self.state = 'ready'
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
        if row == 2:
            f.config(height = card.height+20)
        if col == 5:
            f.config(width = card.width)
        f.grid(row=row+1, column=col)
        f.pack_propagate(0)
        self.fgrid[row][col] = f
        
        pic = Label(f)
        if row <= 2:
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
                    if not self.cheated:
                        delta = round(endTime-self.startTime,2)
                        print(delta)
                        self.infoLabel.config(text="Got in "+str(delta))
                        self.state = 'waiting'
                    else:
                        self.infoLabel.config(text=str(self.faultCount)+" faults made")
                    pic.pack_forget()
                    ins.model[pic.row][pic.col].isNone = True
                elif self.activeCardRow == -1 or not (pic.row <= 2) == (self.activeCardRow <= 2):
                    self.cheated = True
                    self.faultCount = 1
                    self.infoLabel.config(text=str(self.faultCount)+" faults made")
            elif ins.state == 'move-select-start':
                ins.state = 'move-select-stop'
                ins.movingPic = (pic.row, pic.col)
                print('moving card:')
                print(ins.movingPic)
                ins.infoLabel.config(text="Card chosen. Select Destination")
            elif ins.state == 'move-select-stop':
                print('to:')
                print((pic.row, pic.col))
                ins.swapCards(self.movingPic,(pic.row, pic.col))
                ins.state = 'move-select-start'
                ins.moveButton.config(text="Cancel")
                ins.infoLabel.config(text="Move completed. Select next card.")




        
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



                
                


def main():
  
    root = Tk()
    app = Karuta(root,multiplayer=True)
    root.mainloop()

main()
