#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, json

url = "http://localhost/API_UTBM/index?uid="
csvFile = "liste.07.01.19.csv"
outFile = "liste.07.01.19.out.csv"

#response = urllib.urlopen(url)
#data = json.loads(response.read())
#print data['porteur']['login']

def doIt(csvFile, outFile):
    with open(csvFile,'r') as f, open(outFile,'w') as g:
        header = next(f)
        g.write(header)
        nb = 0
        for i in f:
            print(i)
            i = i[:-1].split(',')
            try:
                response = urllib2.urlopen(url+i[1])
                data = json.loads(response.read())
                nb += 1
                print(data)
                j = str(data[1][1])
                print(j)
            except:
                print("Erreur avec la carte : " + i[1])
                j = "erreur : " + i[1]
            g.write(i[0]+','+j+'\n')
    print(str(nb) + " carte(s) identifiée(s) correctement.")
    
doIt(csvFile,outFile)