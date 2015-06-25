class Poem:
    def __init__(self,number):
        with open('poems/poem'+str(number)+'.kar', 'r') as f:
            c = f.readlines()
            self.author = c[0]
            self.verse1 = c[1]
            self.verse2 = c[2]
            self.rauthor = c[3]
            self.rverse1 = c[4]
            self.rverse2 = c[5]
            self.jauthor = c[6]
            self.jverse1 = c[7]
            self.jverse2 = c[11]
            self.kimariji = c[9]
            self.jkimariji = c[10]
            self.number = number
    def card(self):
        verse = self.jverse2.decode('utf-8')
        if len(verse) == 15:
            c = u'\u3000'
        else:
            c = verse[14]
        card = verse[10]+verse[5]+verse[0]+'\n'+ \
               verse[11]+verse[6]+verse[1]+'\n'+ \
               verse[12]+verse[7]+verse[2]+'\n'+ \
               verse[13]+verse[8]+verse[3]+'\n'+ \
               c        +verse[9]+verse[4]+'\n'
        return card
def emptyCard():
    c = u'\u3000'
    line = c+c+c+'\n'
    return line+line+line+line+line
            
        
