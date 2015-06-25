#Karuta Memorizer Helper
import random
from Poem import Poem
from Poem import emptyCard
X_CHOICES = 4



class Tester:
    def __init__(self,poems):
        self.poems = poems
        self.correct = [0 for i in poems]
        self.tried = [0 for i in poems]
    def testFull(self,num = 1):
        numCorrect = 0
        for i in range(num):
            if self.testPoem(int(len(self.poems)*random.random())+1):
                numCorrect = numCorrect + 1
        print 'You got '+str(100*numCorrect/num)+'% correct.'
    def testPoem(self,poem):
        index = poem-1
        print self.poems[index].rverse1
        notIt = self.poems[:index]+self.poems[index+1:]
        random.shuffle(notIt)
        notIt = notIt[:(X_CHOICES - 1)]
        randomVerses = [self.poems[index].card()] + [i.card() for i in notIt]
        random.shuffle(randomVerses)
        for i in range(X_CHOICES):
            print (str(i+1)+':\n'+randomVerses[i])
        guess = input()-1
        if randomVerses[guess] == self.poems[index].card():
            print 'Correct!'
            return True
        else:
            print ('Wrong! The answer was:\n'+self.poems[index].card())
            raw_input()
            return False
##    def testPoems(self,poem):
##        index = poem-1
##        print self.poems[index].rverse1
##        notIt = self.poems[:index]+self.poems[index+1:]
##        random.shuffle(notIt)
##        notIt = notIt[:13]
##        cards = notIt + self.poems[index]
##        random.shuffle(cards)
##        emptyCard = emptyCard()
##        row1 = concat([cards[0],cards[12],emptyCard,emptyCard,emptyCard,cards[13],cards[1]])
##        row2 = concat([cards[2],cards[3],emptyCard,emptyCard,emptyCard,cards[4],cards[5]])
##        row3 = concat([cards[6],cards[7],cards[8],emptyCard,cards[9],cards[10],cards[11]])
##        print row1
##        print row2
##        print row3
    def testK(self):
        index = int(len(self.poems)*random.random())
        print self.poems[index].rverse1
        guess = input("What's the kimariji? -> ")
        if guess == self.poems[index].kimariji[:-1]:
            print 'Correct!'
        else:
            print 'Wrong! The answer was: '+self.poems[index].kimariji
        self.testPoem(index+1)
    def info(self,num):
        p = self.poems[num-1]
        print p.rverse1
        print p.rverse2
        print '\n'
        print p.jverse1.decode('utf-8')
        print p.jverse2.decode('utf-8')
        print '\n'
        print p.verse1
        print p.verse2
        print '\n'
        print p.author
    def search(self,unique):
        for i in self.poems:
            if i.kimariji[:-1] == unique:
                return i.number



allPoems = [Poem(i+1) for i in range(100)]
learned = [100,13,15,17,18,2,21,22,23,28,32,33,35,37,40,42,46,47,48,51,57,59,6,61,62,63,65,66,67,70,71,74,75,77,81,83,85,87,9,91,93,96,98,99]
lp = [allPoems[i-1] for i in learned]
t = Tester(allPoems)

                
        
