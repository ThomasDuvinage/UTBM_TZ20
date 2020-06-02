#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, json

url = "http://localhost/index.php?uid=" #change it to "https://extranet1.utbm.fr/gestprod/api/cms/carte/" to run on utbm internal server or to "http://[IP_ADDRESS]/API_UTBM/index?uid=" to run it locally
csvFile = "liste.07.01.19.csv"
outFile = "liste.07.01.19.out.csv"

#response = urllib.urlopen(url)
#data = json.loads(response.read())
#print data['porteur']['login']

def getInfoFromAPI(csvFile, outFile):
    with open(csvFile,'r') as f, open(outFile,'w') as g:
        header = next(f)
        g.write(header)
        nb = 0
        for i in f:
            print(i)
            i = i[:-1].split(',')
            try:
                response = urllib.urlopen(url+i[2])
                data = json.loads(response.read())
                nb += 1
                print(data)
                j = data[1][1]
                print(j)
            except:
                print("Erreur avec la carte : " + i[2])
                j = "erreur : " + i[1]
            g.write(i[0]+','+j+'\n')
    print(str(nb) + " carte(s) identifiee(s) correctement.")
        
getInfoFromAPI(csvFile,outFile)
