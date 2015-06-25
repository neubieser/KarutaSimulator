from __future__ import print_function
from Tkinter import Tk, W, E, BOTH
from ttk import Frame, Button, Label, Style
from ttk import Entry
from PIL import ImageTk, Image
import threading
import random
import time
from subprocess import call

#p1 is on top
#p2 is on bottom
#no comments
#I only have audio for 80/100

scale = .14
#cards = [2,4,5,6,8,9,10,11,13,14,15,16,17,18,20,21,22,23,24,26,27,28,29,32,33,34,35,37,38,40,41,42,46,47,48\
#         ,49,50,51,54,55,57,59,61,62,63,65,66,67,68,70,71,73,74,75,76,77,81,83,85,87,89,90,91,92,93,94,96,97\
#         ,98,99,100,72,82,44,60,95,36,84,80,53,86]
cards = [i for i in range(1,101)]
order = [(12,1),(1,1),(11,1),(2,1),(12,2),(11,2),(12,3),(1,2),(10,1),(3,1),(2,2),(10,2),(1,3),(11,3),\
         (2,3),(10,3),(9,1),(3,2),(9,2),(3,3),(4,1),(8,1),(7,1),(4,2),(4,3)]

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
        flipped = self.baseimg.rotate(180)
        self.img = ImageTk.PhotoImage(flipped)


class Karuta(Frame):
  
    def __init__(self, parent):
        self.fgrid = [[None for col in range(12)] for row in range(6)]
        self.model = [[None for col in range(12)] for row in range(6)]
        Frame.__init__(self, parent)   
        self.activeCard = 0
        self.parent = parent
        self.cardsLeft = [i for i in range(1,101)]
        random.shuffle(self.cardsLeft)
        self.initUI()
        

    def playNextAudio(self):
        self.faultCount = 0
        self.cheated = False
        self.infoLabel.config(text='Now Playing')
        self.startTime = time.time()
        if self.cardsLeft:
            randomCard = self.cardsLeft.pop()
            self.activeCard = randomCard
            print(randomCard)
            def doInBackground():
                call(['afplay','Audio/Audio'+str(randomCard)+'.m4a'])
            t= threading.Thread(target=doInBackground, args=())
            t.start()
    def reveal(self):
        self.cheated = True
        if self.activeCard in self.p1:
            self.infoLabel.config(text='p1 has it')
            print('p1 has it')
        elif self.activeCard in self.p2:
            print('p2 has it')
            self.infoLabel.config(text='p2 has it')
        else:
            print('was karafuda')
            self.infoLabel.config(text='karafuda')
        self.update()

    def rerack(self):
        for row in range(6):
            for col in range(5):
                if self.model[row][col].isNone and not self.model[row][col+1].isNone:
                    self.model[row][col+1].isNone = True
                    self.model[row][col+1].pack_forget()
                    self.model[row][col].isNone = False
                    self.model[row][col].image = self.model[row][col+1].image
                    self.model[row][col].config(image=self.model[row][col].image)
                    self.model[row][col].pack(fill=BOTH)
            for col in [11,10,9,8,7]:
                if self.model[row][col].isNone and not self.model[row][col-1].isNone:
                    self.model[row][col-1].isNone = True
                    self.model[row][col-1].pack_forget()
                    self.model[row][col].isNone = False
                    self.model[row][col].image = self.model[row][col-1].image
                    self.model[row][col].config(image=self.model[row][col].image)
                    self.model[row][col].pack(fill=BOTH)
        self.update()



            
        
    def initUI(self):
      
        self.parent.title("Karuta")
        
        Style().configure("TButton")
        
        p1,p2 = randomAssignCards(cards,order)
        for row in range(6):
            for col in range(12):
                if (12-col,row+1) in p1:
                    self.setCard(p1[(12-col,row+1)],row,col)
                elif (col+1,6-row) in p2:
                    self.setCard(p2[(col+1,6-row)],row,col)
                else:
                    self.setCard(-1,row,col)
        self.p1 = [i for i in p1.values()]
        self.p2 = [i for i in p2.values()]
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
            f.config(width = card.width+250)
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
        
        def dostuff(pls,ins,card):
            if card.number == ins.activeCard:
                endTime = time.time()
                if not self.cheated:
                    delta = round(endTime-self.startTime,2)
                    print(delta)
                    self.infoLabel.config(text="Got in "+str(delta))
                else:
                    self.infoLabel.config(text=str(self.faultCount)+" faults made")
                pic.pack_forget()
                ins.model[pic.row][pic.col].isNone = True
            elif (card.number in ins.p1 and ins.activeCard in ins.p1) or \
                 (card.number in ins.p2 and ins.activeCard in ins.p2):
                pass
            else:
                self.cheated = True
                self.faultCount = self.faultCount + 1
                self.infoLabel.config(text=str(self.faultCount)+" faults made")



        
        pic.bind("<Button-1>",lambda e,pic=pic,self=self,card=card:dostuff(pic,self,card))
        pic.pack(fill=BOTH)
        self.model[row][col] = pic

        if dodel:
            pic.pack_forget()
            self.model[row][col].isNone = True

        else:
            self.model[row][col].isNone = False
                
                


def main():
  
    root = Tk()
    app = Karuta(root)
    root.mainloop()

main()
