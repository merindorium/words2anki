# -*- coding: utf-8 -*-
import sys
import urllib2
from BeautifulSoup import BeautifulSoup
import csv

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if len(sys.argv) <= 1:
    print "Please write wordlist path"
    exit()
word_list_name = sys.argv[1]
word_list = file(word_list_name)
words = word_list.readlines()

def get_from_mult(word):
    url = 'http://www.multitran.ru/c/m.exe?l1=1&l2=2&s='+word.replace('\n', '').replace(' ', '%20')
    con2 = urllib2.urlopen(url)
    data = con2.read()
    soup = BeautifulSoup(data)
    trans_table = soup.find('form', {"id":"translation"})
    if trans_table.parent.findNext('a').text == '':
        try:
            suj = trans_table.parent.findNext('td', {'width':'90%'}).text
        except:
            suj = 'ANOTHER'
        seq = bcolors.FAIL+'[ERROR]'+ bcolors.ENDC
        sys.stdout.write(seq)
        sys.stdout.write(word.replace('\n','')+bcolors.FAIL+" - No such word"+ bcolors.ENDC)
        sys.stdout.write(' - try '+bcolors.OKBLUE+suj+ bcolors.ENDC+' \n')
        return

    trans_table = trans_table.parent.findNext('table',{'border':'0', 'style':None})

    for img in trans_table.findAll('img'):
        img['src'] = 'http://www.multitran.ru'+img['src']
        img['style'] = 'background-color:white;'

    for td in trans_table.findAll('td'):
        del td['bgcolor']

    for td in trans_table.findAll('td', {'width':'700'}):
        td.name = 'th'
        for span in td.findAll('span'):
            span.extract()

    for a in trans_table.findAll('a'):
        if a.get('title') != None:
            a.name = 'text'
            a.find('i').replaceWithChildren()
        else:
            a.replaceWith(a.text)
        del a['href']

    with open('to_anki.csv', 'a+') as csvfile:
        csvreader = csv.writer(csvfile)
        csvreader.writerow([word.replace('\n',''), trans_table])
        csvfile.flush()
    seq = bcolors.OKGREEN+'[OK]'+ bcolors.ENDC
    sys.stdout.write(seq)
    sys.stdout.write(word)



for i,word in enumerate(words):
    exist = False
    with open('to_anki.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[0] == word.replace('\n',''):
                exist = True
    if word != '' and not exist:
        try:
            get_from_mult(word)
        except:
            seq = bcolors.FAIL+'[ERROR]'+ bcolors.ENDC + word.replace('\n','')+' - Connection Error\n'
            sys.stdout.write(seq)
