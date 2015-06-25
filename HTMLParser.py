#Parse HTML -> Poem format
import re

ls = []
lsr = []
lsjd = []
with open('/Users/neub/Karuta/poems/English.txt', 'r') as f:
    ls = f.readlines()
with open('/Users/neub/Karuta/poems/Romaji.txt', 'r') as f:
    lsr = f.readlines()
with open('/Users/neub/Karuta/poems/Japanese.UTF8', 'rb"utf-8"') as f:
    lsjd = f.readlines()
lsj = []
for i in range(len(lsjd)):
    if not lsjd[i] == '\n' and not lsjd[i] == ' \n':
        lsj.append(lsjd[i])
    



def parse(ls):
    poems = []
    pnum = 1
    for i in range(len(ls)):
        if '/images/onna'+str(pnum)+'.jpg' in ls[i]:
            author = re.search('<center>(.+?)</center>', ls[i+1]).group(1) + '\n'
            verse1 = re.search('<br>(.+?)\n',ls[i+2]).group(1) + '|' + \
                     re.search('<br>(.+?)\n',ls[i+3]).group(1) + '|' + \
                     re.search('<br>(.+?)\n',ls[i+4]).group(1) + '\n'
            verse2 = re.search('<br>(.+?)\n',ls[i+6]).group(1) + '|' + \
                     re.search('<br>(.+?)\n',ls[i+7]).group(1) + '\n'
            
            poems.append([author,verse1,verse2])
            pnum = pnum + 1
    return poems

poems = [[],[],[]]
poems[0] = parse(ls)
poems[1] = parse(lsr)
poems[2] = parse(lsj)

for poem in range(100):
    with open('/Users/neub/Karuta/poems/poem'+str(poem+1)+'.kar', 'w+') as f:
        f.write(poems[0][poem][0])
        f.write(poems[0][poem][1])
        f.write(poems[0][poem][2])
        f.write(poems[1][poem][0])
        f.write(poems[1][poem][1])
        f.write(poems[1][poem][2])
        f.write(poems[2][poem][0])
        f.write(poems[2][poem][1])
        f.write(poems[2][poem][2])
u = []
with open('/Users/neub/Karuta/unique.txt','r') as f:
    u = f.readlines()
lines = []
un = []
v = []
with open('/Users/neub/Karuta/poems/2ndVerse.UTF8','rb"utf-8"') as f:
    lines = f.readlines()
for i in lines:
    if len(i) < 20:
        un.append(i)
    else:
        v.append(i)
for i in range(1,101):
        with open('/Users/neub/Karuta/poems/poem'+str(i)+'.kar','a') as g:
            g.write(u[i-1])
            le = len(u[i-1].split())
            g.write((poems[2][i-1][1].decode('utf-8').replace('|','')[:le]+'\n').encode('utf-8'))
            g.write(v[un.index(u[i-1])])
            




