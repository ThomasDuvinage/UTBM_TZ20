#!/usr/bin/env python3

#TODO: modifier l'addition de fichier
#TODO: voir pour l'extraction de dossier vers SD et umount
import os
from datetime import datetime, timedelta
import errno
import time
import USBKey


class Files():
    import sys
    import csv
    from datetime import datetime, date, time, timedelta
    import os
    from os import path
    import shutil
    #import urllib  # for python 3 : import urllib.request
    import urllib
    import USBKey
    import json
    import structureConfig as structConfig
    import re

    """
        Le constructeur permet d'initialiser cette classe
        IMPORTANT Si le fichier n'existe pas encore il sera cree. Cela signifie que nous creons un FICHIER DE STOCKAGE DES UIDs ET RIEN D'AUTRE

        A l'inverse pour faire de la comparaison de fichier il faut creer un object Files en passant en argument l'endroit ou se trouve le fichier dans votre structure

        Argument : path pour le fichier (la valeur par defaut est None)
    """

    def __init__(self, initialFilePath=None):

        self.presents = 0
        self.absents = 0
        self.wrong_presents = 0
        self.errorsRequestAPI = 0

        self.initFilePath = initialFilePath
        self.folderPathName = ""

        self.pathDSIFile = ""

        self.read = 'r'
        self.append = 'a'
        self.write = 'w'

    """
        Cette methode permet de faire l'ajout d'etudiant dans le fichier donne comme initialFilePath
    """

    def addStudentToFile(self, UID, DTnow):
        # Cette variable permet de savoir si l'uid est deja present dans le fichier

        if(self.exist(self.initFilePath)):
            # la lecture de fichier suivante permet de savoir si la carte scannee par l'utilisateur est deja presente dans le fichier
            with open(self.initFilePath, self.read) as UIDFile:
                UIDFilereader = self.csv.reader(UIDFile)
                for row in UIDFilereader:
                    if(row[2] == UID):
                        print("Carte deja scannee")
                        return False

            with open(self.initFilePath, self.append) as UIDFile:
                UIDFileWriter = self.csv.writer(
                    UIDFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                UIDFileWriter.writerow(
                    [DTnow.strftime("%d-%m-%Y"), DTnow.strftime("%H-%M-%S"), UID])
                return True
        else:
            with open(self.initFilePath, self.write) as UIDFile:
                UIDFileWriter = self.csv.writer(
                    UIDFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                UIDFileWriter.writerow(
                    [DTnow.strftime("%d-%m-%Y"), DTnow.strftime("%H-%M-%S"), UID])
            return True

    """
        Cette methode permet de connnaitre le fichier qui possede la meme date a un interval donne dans le constructeur de la classe
        Dans notre cas cette methode est utilisee pour rechercher dans cle usb un le dossier  etant dans l'interval

        Output : nom du fichier dans l'intervalle sinon None
    """

    def foundSameEventFile(self, pathUSB, DTMain, interval):
        '''
            Pour cette fonction il faut encore ajouter des conditions d'autant plus que cette fonction permet de savoir si il y a des fichiers de la meme date sur celle-ci. Il faut donc ajouter cela
        '''
        folderList = listDirectory(
            pathUSB + "/Fichiers_SCAN", True, False, False)
        print("DIR LIST : ", folderList)

        for folderName in folderList:
            try:
                folderDT = self.datetime.strptime(
                    folderName, "%d-%m-%Y-%H-%M-%S")
                Delta = abs(DTMain - folderDT)
                if(Delta <= interval):
                    InnerFiles = listDirectory(
                        pathUSB+"/Fichiers_SCAN/"+folderName, False, True, True)
                    StandardFiles = ["report", "total"]
                    isExtractionComplete = True
                    for stfile in StandardFiles:
                        if not stfile+".csv" in InnerFiles:
                            isExtractionComplete = False
                    if isExtractionComplete:
                        print("Complete extraction found on USB key: ", folderName)
                        return folderName
                    else:
                        print("Uncomplete extraction found on USB key: ", folderName)
            except ValueError:
                print("Warning : Fichiers_SCAN folder contains undesired folders")
        return None

    """
        Cette methode permet de faire l'extration du dossier final genere par la methode: compareDsiFilesToFileCreation()

        Il est donc important de faire appel a cette methode avant de faire l'extraction vers la cle usb car sinon la valeur de la variable self.folderPathName
        ne correspondera pas a l'endroit ou se trouve les fichiers sur la cle usb
    """

    def exportFileToUSB(self, USB_Key, DSIPath):
        if(USB_Key):
            # this condition checks if the extraction have been done
            if(self.folderPathName + '/' != ""):
                if(self.exist(USB_Key + '/' + "Fichiers_SCAN")):
                    USB_Key += '/' + "Fichiers_SCAN" + '/' + \
                        self.initFilePath.rsplit(
                            '/')[-1].replace(".csv", "") + '/'

                    self.copyFilesFromDirectoryToDirectory(
                        self.folderPathName + '/', USB_Key)

                    if(self.exist(USB_Key)):
                        return True
                    else:
                        return False

                else:
                    self.os.mkdir(USB_Key + '/' + "Fichiers_SCAN")
                    USB_Key += '/' + "Fichiers_SCAN" + '/' + \
                        self.initFilePath.rsplit(
                            '/')[-1].replace(".csv", "") + '/'
                    self.copyFilesFromDirectoryToDirectory(
                        self.folderPathName + '/', USB_Key)

                    if(self.exist(USB_Key)):
                        return True
                    else:
                        return False

            # This condition permits to check if the final files extactions has been done and if the uid file is not empty
            # if so it extracts final files and
            elif(self.folderPathName == "" and not self.isEmpty(self.initFilePath)):
                self.compareDsiFilesToFileCreation(
                    DSIPath, self.initFilePath.rsplit('/')[-1].replace(".csv", ""))
                self.exportFileToUSB(USB_Key, DSIPath)
        else:
            print("ERROR : usb key missing or final files not in the folder")
            return False

    """
        Cette methode permet de relier des fichiers de la cle usb aux fichier presents dans le dosssier final_extractions.

        Pour cela les fichiers du dossier final_extractions sont ajoutes au fichier sur la cle usb
    """

    def addToUSBKEY(self, pathToUSB, DTnow, interval): #to call in case of multiple extraction

        if(pathToUSB):
            if(self.folderPathName != ""):#permet de verifier que l'extraction a ete faite 
                if(self.exist(pathToUSB + '/' + "Fichiers_SCAN/")):

                    directoryName = self.foundSameEventFile(
                        pathToUSB, DTnow, interval)

                    if directoryName:
                        pathToUSB += '/Fichiers_SCAN/' + directoryName

                        if(self.exist(self.folderPathName + '/presents.csv')):
                            with open(self.folderPathName + '/presents.csv', self.read) as presentFile:
                                presentFileReader = self.csv.reader(
                                    presentFile)

                                if(self.exist(pathToUSB + '/presents.csv')):
                                    next(presentFileReader)
                                    with open(pathToUSB + '/presents.csv', self.append) as presentFileUSBKey:
                                        fileUSBwriter = self.csv.writer(
                                            presentFileUSBKey)
                                        
                                        #Cette lecture du fichier permet de verifier si la personne n'est pas deja presente dans le fichier sur la cle
                                        #dans cette situation cela signifierait que la personne est rentree dans part deux entree en scannant les deux fois
                                        with open(pathToUSB + '/presents.csv', self.read) as presentFileUSBReader:
                                            checkerUSBPresent = self.csv.reader(presentFileUSBReader)

                                            for student in presentFileReader:
                                                presentFileUSBReader.seek(0)
                                                next(checkerUSBPresent)
                                                
                                                indicePresent = False
                                                for scannedPresent in checkerUSBPresent:
                                                    if(student[5] == scannedPresent[5]):
                                                        indicePresent = True
                                                
                                                if not indicePresent:
                                                    fileUSBwriter.writerow(
                                                        student[:])

                                    self.presents = self.__row_count(pathToUSB + '/presents.csv') - 1

                                else:
                                    with open(pathToUSB + '/presents.csv', self.write) as presentFileUSBKey:
                                        fileUSBwriter = self.csv.writer(
                                            presentFileUSBKey)

                                        for student in presentFileReader:
                                            fileUSBwriter.writerow(
                                                student[:])

                                print("Adding present content to USB done")

                        if(self.exist(self.folderPathName + '/absents.csv')):
                            with open(self.folderPathName + '/absents.csv', self.read) as absentFile:
                                absentFileReader = self.csv.reader(absentFile)

                                if(self.exist(pathToUSB + '/absents.csv') and self.exist(pathToUSB + '/presents.csv')):
                                    self.absents = 0
                                    #Supression du fichier absent sur la cle usb afin de regener les absents en fonction du fichier des presents 
                                    self.deleteFile(pathToUSB + '/absents.csv')
                                    #Cela permet par la suite de recreer un fichier absent sur la cle usb en lisant le fichier des presents qui est sur la cle
                                    with open(pathToUSB + '/presents.csv', self.read) as Present_File, open(self.pathDSIFile+".csv", self.read) as DSIfile:
                                        Present_FileReader = self.csv.reader(Present_File)                                       
                                        DSI_FileReader = self.csv.reader(DSIfile)

                                        # Ces deux lignes permettent de skiper les headers dans les fichiers
                                        next(DSI_FileReader)

                                        for DSI_Row in DSI_FileReader:
                                            indice_present = False
                                            Present_File.seek(0)
                                            next(Present_FileReader)
                                            for Present_Row in Present_FileReader:
                                                if(DSI_Row[3] == Present_Row[5]):
                                                    indice_present = True
                                                    break

                                            if not indice_present:
                                                if(self.exist(pathToUSB + '/absents.csv')):
                                                    with open(pathToUSB + '/absents.csv', self.append) as absentsFile:
                                                        absentFileWriter = self.csv.writer(
                                                            absentsFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                                                        absentFileWriter.writerow(DSI_Row[:])

                                                else:
                                                    with open(pathToUSB + '/absents.csv', self.write) as absentsFile:
                                                        absentFileWriter = self.csv.writer(
                                                            absentsFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                                                        absentFileWriter.writerow(
                                                            ['NOM', 'PRENOM', 'ETUD_NUMERO', 'NO_INDIVIDU', 'MAIL','LOGIN', 'FORMATION', 'NIVEAU'])
                                                        absentFileWriter.writerow(DSI_Row[:])

                                                self.absents += 1
                                            

                                elif(self.exist(pathToUSB + '/absents.csv')):#Si il n'y pas de fichier de present sur la cle mais qu'il y a un fichier d'absent alors nous ajoutons les absent que nous vons genere dans ce fichier
                                    with open(pathToUSB + '/absents.csv', self.append) as absentFileUSBKey:
                                        fileUSBwriter = self.csv.writer(
                                            absentFileUSBKey)
                                        next(absentFileReader)

                                        for student in absentFileReader:
                                            fileUSBwriter.writerow(
                                                student[:])

                                    self.absents = self.__row_count(pathToUSB + '/absents.csv') - 1

                                elif not self.exist(pathToUSB + '/absents.csv'):#Si il n'y a aucun fichier d'absent sur la cle alors on copie celui que nous avons genere
                                    with open(pathToUSB + '/absents.csv', self.write) as absentFileUSBKey:
                                        fileUSBwriter = self.csv.writer(
                                            absentFileUSBKey)

                                        for student in absentFileReader:
                                            fileUSBwriter.writerow(
                                                student[:])

                                print("Adding absents content to USB done")

                        #Comme les faux presents sont des personnes qui sont la par erreur nous pouvons les ajouter directement a la suite du fichier ou d'en creer un si il n'exite pas 
                        if(self.exist(self.folderPathName + '/faux-presents.csv')):
                            with open(self.folderPathName + '/faux-presents.csv', self.read) as wrong_present_File:
                                wPresentFileReader = self.csv.reader(
                                    wrong_present_File)

                                if(self.exist(pathToUSB + '/faux-presents.csv')):
                                    next(wPresentFileReader)
                                    with open(pathToUSB + '/faux-presents.csv', self.append) as wPresentFileUSBKey:
                                        fileUSBwriter = self.csv.writer(
                                            wPresentFileUSBKey)

                                        for student in wPresentFileReader:
                                            fileUSBwriter.writerow(
                                                student[:])
                                else:
                                    with open(pathToUSB + '/faux-presents.csv', self.write) as wPresentFileUSBKey:
                                        fileUSBwriter = self.csv.writer(
                                            wPresentFileUSBKey)

                                        for student in wPresentFileReader:
                                            fileUSBwriter.writerow(
                                                student[:])
                                
                            self.wrong_presents = self.__row_count(pathToUSB + '/faux-presents.csv') - 1
                            print("Adding faux-present content to USB done")

                        with open(pathToUSB + '/total.csv', self.write) as totalFileUSBKey:
                            totalFileWriter = self.csv.writer(totalFileUSBKey, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                            totalFileWriter.writerow(['DATE', 'HEURE', 'NOM', 'PRENOM','PRESENCE', 'ETUD_NUMERO', 'NO_INDIVIDU', 'MAIL', 'FORMATION', 'NIVEAU'])

                            if(self.exist(pathToUSB + '/presents.csv')):
                                with open(pathToUSB + '/presents.csv', self.read) as presentFile:
                                    presentFileReader = self.csv.reader(presentFile)
                                    next(presentFileReader)

                                    for present in presentFileReader:
                                        totalFileWriter.writerow(list(present[0:4])+["OUI"]+list(present[4:10]))

                            if(self.exist(pathToUSB + '/absents.csv')):
                                with open(pathToUSB + '/absents.csv', self.read) as absentsFile:
                                    absentFileReader = self.csv.reader(absentsFile)
                                    next(absentFileReader)

                                    for absent in absentFileReader:
                                        totalFileWriter.writerow(
                                            ["/", "/"]+list(absent[0:2])+["NON"]+list(absent[2:8]))

                            if(self.exist(pathToUSB + '/faux-presents.csv')):
                                with open(pathToUSB + '/faux-presents.csv', self.read) as fauxPresentFile:
                                    fauxPresentFileReader = self.csv.reader(fauxPresentFile)
                                    next(fauxPresentFileReader)

                                    for faux_present in fauxPresentFileReader:
                                        totalFileWriter.writerow(
                                            list(faux_present[0:2])+ ["/", "/", "OUI MAIS INATTENDUE", "/", "/", "/"]+[faux_present[2]]+["/","/"])

                            print("Adding total content to USB done")

                        if(self.exist(self.folderPathName + '/report.csv')):
                            linesReportUSB = []
                            with open(self.folderPathName + '/report.csv', self.read) as reportFile:
                                reportFileReader = self.csv.reader(reportFile)

                                if(self.exist(pathToUSB + '/report.csv') and self.__checkReportCorrectness(pathToUSB + '/report.csv')):
                                    next(reportFileReader)

                                    with open(pathToUSB + '/report.csv', self.read) as reportFileUSB:
                                        reportFileReaderUSB = self.csv.reader(
                                            reportFileUSB)
                                        headerReport = next(
                                            reportFileReaderUSB)

                                        linesReportUSB = next(reportFileReaderUSB)    

                                        numScan = self.__row_count(self.initFilePath) + int(linesReportUSB[0])

                                        numSupposedToAttend = self.__row_count(self.pathDSIFile+".csv")-1

                                        percentAbsents = (float(self.absents) / numSupposedToAttend) * 100
                                        percentPresents = (float(self.presents) / numSupposedToAttend) * 100
                                        percentWrongPresent = (float(self.wrong_presents) / numScan) * 100

                                        dateFirstScan, dateLastScan = 0, 0

                                        with open(self.structConfig.structure['UID_inputs'] + DTnow.strftime("%d-%m-%Y-%H-%M-%S") + ".csv", self.read) as inputFile:
                                            inputFileReader = self.csv.reader(
                                                inputFile)

                                            fileLines = list(inputFileReader)

                                            dateFirstScan = self.datetime.strptime(
                                                fileLines[0][1], "%H-%M-%S")
                                            dateLastScan = self.datetime.strptime(
                                                fileLines[-1][1], "%H-%M-%S")

                                        scanningTime = dateLastScan - dateFirstScan

                                        scanningTime += self.datetime.strptime(
                                            linesReportUSB[5], "%H:%M:%S")

                                    with open(pathToUSB + "/report.csv", self.write) as reportFile:
                                        reportWriter = self.csv.writer(
                                            reportFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)

                                        reportWriter.writerow(["Nombre scans","Nombre etudiants attendus","Nombre absents (%Attendus) ", "Nombre presents (%Attendus)",
                                                            "Nombre faux-presents (%Scans)", "DUREE SCAN", "Nombre erreur de requetes API"])
                                        reportWriter.writerow([str(numScan),str(numSupposedToAttend),str(self.absents) + ' (' + '%.2f'%percentAbsents + '%)', str(
                                            self.presents) + ' (' + '%.2f'%percentPresents + '%)', str(self.wrong_presents) + ' (' + '%.2f'%percentWrongPresent + '%)', scanningTime.strftime("%H:%M:%S"), self.errorsRequestAPI])
                                    
                                elif not self.__checkReportCorrectness(pathToUSB + '/report.csv'):
                                    print("There are problems in the file report.csv at ", pathToUSB + '/report.csv')
                                    return False

                            print("Adding report content to USB done")
                        return True
                    else:
                        print("No files found in the time interval")
                        return False
                else:
                    print("The folder to contain all files on USB doesn't exit")
                    self.os.mkdir(pathToUSB + '/' + "Fichiers_SCAN/")
                    if(self.addToUSBKEY(pathToUSB, DTnow, interval)):
                        return True

                    return False
            else:
                print("Please do the comparaison with the DSI file before trying to export files")
                return False
        else:
            print("No usb Key connected")
            return False

    """
    Cette methode permet de faire la comparaison de deux fichier.
    Elle compare le fichier qui contient les numeros de cartes avec le fichier fournit par la DSI

    argument : string pathToFile -> correspond a l'emplacement du fichier a comparer avec celui donne initialement
    sortie :

    Pour faire la comparaison il faut que le fichier de la DSI ait le format suivant :
        NOM, PRENOM, ETUD_NUMERO, NO_INDIVIDU, EMAIL, LOGIN, FORMATION, NIVEAU
    """
    
    def compareDsiFilesToFileCreation(self, pathToDsiFile, DTnow):
        self.pathDSIFile = pathToDsiFile
        pathToDsiFile+=".csv"
        self.folderPathName = self.structConfig.structure["final_extractions"] + \
            self.initFilePath.split('/')[-1].replace(".csv", "")
        try:  # here we try to create a Directory to store files
            self.os.mkdir(self.folderPathName)
        except OSError as e:
            if(e.errno != os.errno.EEXIST):
              print("Creation of the directory %s failed" % self.folderPathName)
              print(e)
              return

        # Cette ligne permet d'envoyer les requetes vers l'API afin de connaitre les logins
        self.__getUserInfoViaAPI(DTnow)

        api_output_path = self.structConfig.structure["API_OUTPUTS"] + \
            DTnow.strftime("%d-%m-%Y-%H-%M-%S") + ".csv"

        with open(api_output_path, self.read) as API_File, open(pathToDsiFile, self.read) as DSIfile:
            API_FileReader = self.csv.reader(API_File)
            DSI_FileReader = self.csv.reader(DSIfile,delimiter=',') # to specify delimiter : self.csv.reader(DSIfile,delimiter=";")

            next(DSI_FileReader) # Cette ligne permet de ne pas compter le header

            for API_Row in API_FileReader:
                print("Student found in API_output : ",API_Row[1])
                indice_present = 0
                for DSI_Row in DSI_FileReader:
                    #print(DSI_Row[5])
                    if(API_Row[1] == DSI_Row[5]):
                        print('Present recognized')
                        rowUidFile = self.__getRowByKey(
                            API_Row[0], self.initFilePath, 2)

                        if(self.exist(self.folderPathName + '/presents.csv')):
                            with open(self.folderPathName + '/presents.csv', self.append) as presentFile:
                                presentFileWriter = self.csv.writer(
                                    presentFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                                presentFileWriter.writerow(
                                    [rowUidFile[0], rowUidFile[1], DSI_Row[0], DSI_Row[1], DSI_Row[2], DSI_Row[3], DSI_Row[4], DSI_Row[5],DSI_Row[6], DSI_Row[7]])

                        else: #we first write the header in top of file
                            with open(self.folderPathName + '/presents.csv', self.write) as presentFile:
                                presentFileWriter = self.csv.writer(
                                    presentFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                                # ecrire le titre des colonnes du tableau
                                presentFileWriter.writerow(
                                    ['DATE', 'HEURE', 'NOM', 'PRENOM', 'ETUD_NUMERO', 'NO_INDIVIDU', 'MAIL', 'LOGIN','FORMATION', 'NIVEAU'])
                                presentFileWriter.writerow(
                                    [rowUidFile[0], rowUidFile[1], DSI_Row[0], DSI_Row[1], DSI_Row[2], DSI_Row[3], DSI_Row[4], DSI_Row[5], DSI_Row[6], DSI_Row[7]])

                        self.presents += 1
                        indice_present = 1
                        break
                DSIfile.seek(0)
                next(DSI_FileReader)
                if not indice_present and API_Row[1]!="Erreur_API":
                    rowUidFile = self.__getRowByKey(
                        API_Row[0], self.initFilePath, 2)

                    if(self.exist(self.folderPathName + '/faux-presents.csv')):
                        with open(self.folderPathName + '/faux-presents.csv', self.append) as fauxPresentFile:
                            fauxPresentFileWriter = self.csv.writer(
                                fauxPresentFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                            fauxPresentFileWriter.writerow(
                                [rowUidFile[0], rowUidFile[1], API_Row[1]])

                    else:
                        with open(self.folderPathName + '/faux-presents.csv', self.write) as fauxPresentFile:
                            fauxPresentFileWriter = self.csv.writer(
                                fauxPresentFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                            fauxPresentFileWriter.writerow(
                                ['DATE', 'HEURE', 'LOGIN'])
                            fauxPresentFileWriter.writerow(
                                [rowUidFile[0], rowUidFile[1], API_Row[1]])

                    self.wrong_presents += 1

        if(self.exist(self.folderPathName + '/presents.csv')):
            with open(self.folderPathName + '/presents.csv', self.read) as Present_File, open(pathToDsiFile, self.read) as DSIfile:
                DSIfile.seek(0)
                Present_FileReader = self.csv.reader(Present_File)
                DSI_FileReader = self.csv.reader(DSIfile)
                # Ces deux lignes permettent d'ignorer les headers dans les fichiers
                next(Present_FileReader)
                next(DSI_FileReader)

                for DSI_Row in DSI_FileReader:
                    indice_present = 0
                    Present_File.seek(0)
                    next(Present_FileReader)
                    for Present_Row in Present_FileReader:
                        if(DSI_Row[3] == Present_Row[5]):
                            indice_present = 1
                            print("Present found : ",Present_Row[2])
                            break

                    if not indice_present:
                        if(self.exist(self.folderPathName + '/absents.csv')):
                            with open(self.folderPathName + '/absents.csv', self.append) as absentsFile:
                                absentFileWriter = self.csv.writer(
                                    absentsFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                                absentFileWriter.writerow(
                                    DSI_Row[:])

                        else:
                            with open(self.folderPathName + '/absents.csv', self.write) as absentsFile:
                                absentFileWriter = self.csv.writer(
                                    absentsFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
                                # ecrire le titre des colonnes du tableau
                                absentFileWriter.writerow(
                                    ['NOM', 'PRENOM', 'ETUD_NUMERO', 'NO_INDIVIDU', 'MAIL', 'LOGIN', 'FORMATION', 'NIVEAU'])
                                absentFileWriter.writerow(
                                    DSI_Row[:])

                        self.absents += 1

        else:
            print("PATH DSI FILE : ",self.pathDSIFile)
            self.os.system("cp "+self.pathDSIFile + " " +
                           self.folderPathName + '/absents.csv')
            self.absents = 0 if not self.exist(self.folderPathName + '/absents.csv') else self.__row_count(self.folderPathName+'/absents.csv')

        with open(self.folderPathName + '/total.csv', self.append) as total_File:
            totalFileWriter = self.csv.writer(
                total_File, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)

            totalFileWriter.writerow(
                ['DATE', 'HEURE', 'NOM', 'PRENOM', 'PRESENCE','ETUD_NUMERO', 'NO_INDIVIDU','MAIL','LOGIN', 'FORMATION', 'NIVEAU'])

            if(self.exist(self.folderPathName + '/presents.csv')):
                with open(self.folderPathName + '/presents.csv', self.read) as presentFile:
                    presentFileReader = self.csv.reader(presentFile)
                    next(presentFileReader)

                    for present in presentFileReader:
                        totalFileWriter.writerow(list(present[0:4])+["OUI"]+list(present[4:10]))

            if(self.exist(self.folderPathName + '/absents.csv')):
                with open(self.folderPathName + '/absents.csv', self.read) as absentsFile:
                    absentFileReader = self.csv.reader(absentsFile)
                    next(absentFileReader)

                    for absent in absentFileReader:
                        totalFileWriter.writerow(
                            ["/", "/"]+list(absent[0:2])+["NON"]+list(absent[2:8]))

            if(self.exist(self.folderPathName + '/faux-presents.csv')):
                with open(self.folderPathName + '/faux-presents.csv', self.read) as fauxPresentFile:
                    fauxPresentFileReader = self.csv.reader(fauxPresentFile)
                    next(fauxPresentFileReader)

                    for faux_present in fauxPresentFileReader:
                        totalFileWriter.writerow(
                            list(faux_present[0:2])+ ["/", "/", "OUI MAIS INATTENDUE", "/", "/", "/"]+[faux_present[2]]+["/","/"])

        self.__generateReport(self.folderPathName, DTnow)

    """
        Cette methode permet verifier si un fichier existe deja dans la pathToFile specifie en argument

        Ouput : boolean
    """

    def exist(self, pathToFile=None):
        if pathToFile==None:
            if(self.path.exists(self.initFilePath)):
                return True
            else:
                return False
        else:
            if(self.path.exists(pathToFile)):
                return True
            else:
                return False

    """
        Cette methode permet de savoir si un fichier csv possede un commentaire
    """

    def isEmpty(self, pathToFile):
        if self.exist(pathToFile):
            if(self.__row_count(pathToFile) > 1):
                return True
            else:
                return False
        else:
            return False

    """
        Cette methode permet de supprimer un fichier a un certain endroit
    """

    def deleteFile(self, pathToFile):
        try:
            self.os.system("rm -rf "+pathToFile)
            print("deleted file ", pathToFile)
            return True
        except OSError:
            print("cant delete file ", pathToFile)
            return False

    """
        Cette methode permet de copier un repertoire vers un autre
    """

    def copyFilesFromDirectoryToDirectory(self, pathSrc, pathDest):
        try:
            self.os.system("cp -r " + pathSrc + ' ' + pathDest)
            print("File copy to :", pathDest)
            return True
        except OSError:
            print("ERROR : cant copy file to dest")
            return False

    """
        Cette methode permet de connaitre l'adresse du fichier
    """

    def getPath(self):
        return self.initFilePath

    """
        Cette methode privee permet d'envoyer les requetes vers l'API de l'UTBM
    """

    """
        Cette methode permet de connaitre l'index auquel se trouve un utilisateur dans le fichier qui se trouve a path et a la colonne precisee
    """

    def __getRowByKey(self, searchKey, path, columnToSearchIn):
        with open(path, self.read) as File:
            FileReader = self.csv.reader(File)

            for row in FileReader:
                if(row[columnToSearchIn] == searchKey):
                    return row

        return None

    """
        Cette methode permet de connaitre l'ensemble des logins en fonction de l'UID de chaque carte.

        Lecture du fichier des UID_inputs puis de generation du fichier API_OUTPUT. Si il y a une erreur dans la requete alors l'UID de la carte est ajoute au fichier
        API_OUTPUT mais avec le login -> Erreur

        Ainsi comme personne ne possede le login Erreur l'utilisateur sera mis dans le fichier de faux-presents.csv
    """

    def __getUserInfoViaAPI(self, DTnow):
        print("Getting students logins")
        url = self.structConfig.structure["API_url"]

        outFile = self.structConfig.structure["API_OUTPUTS"] + \
            DTnow.strftime("%d-%m-%Y-%H-%M-%S") + ".csv"

        with open(self.initFilePath, self.read) as f, open(outFile, self.write) as g:
            # outFileWriter = self.csv.writer(g, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)
            outFileWriter = self.csv.writer(g, delimiter=',',quotechar='|',escapechar='-',quoting=self.csv.QUOTE_NONE)
            for i in f:
                i = i[:-1].split(',')
                try:
                    print("Sending Request to API")
                    print("URL SENT TO API : ",url + str(i[2]))
                    response = self.urllib.urlopen(
                        url + str(i[2])).read().decode('utf-8')

                    data = self.json.loads(str(response))
                    j = data[1][1]

                    outFileWriter.writerow([i[2][:-1], j])

                    print("API request success")

                except:
                    self.errorsRequestAPI += 1
                    print("Error with UID : " + i[2])
                    outFileWriter.writerow([i[2][:-1], "Erreur_API"])

    """
        Cette methode permet de faire le fichier de report qui permet de faire un rapport sur l'evenement
    """

    def __generateReport(self, pathToFinalExtraction, DTnow):
        # on enleve 1 car cela correspond au header
        numScan = self.__row_count(self.initFilePath)
        numSupposedToAttend = self.__row_count(self.pathDSIFile+".csv")-1

        percentAbsents = (float(self.absents) / numSupposedToAttend) * 100
        percentPresents = (float(self.presents) / numSupposedToAttend) * 100
        percentWrongPresent = (float(self.wrong_presents) / numScan) * 100

        dateFirstScan, dateLastScan = 0, 0

        with open(self.structConfig.structure['UID_inputs'] + DTnow.strftime("%d-%m-%Y-%H-%M-%S") + ".csv", self.read) as inputFile:
            inputFileReader = self.csv.reader(inputFile)

            fileLines = list(inputFileReader)

            dateFirstScan = self.datetime.strptime(
                fileLines[0][1], "%H-%M-%S")
            dateLastScan = self.datetime.strptime(
                fileLines[-1][1], "%H-%M-%S")

        scanningTime = dateLastScan - dateFirstScan

        with open(pathToFinalExtraction + "/report.csv", self.write) as reportFile:
            reportWriter = self.csv.writer(
                reportFile, delimiter=',', quotechar='|', quoting=self.csv.QUOTE_MINIMAL)

            reportWriter.writerow(["Nombre scans","Nombre etudiants attendus","Nombre absents (%Attendus) ", "Nombre presents (%Attendus)",
                                   "Nombre faux-presents (%Scans)", "DUREE SCAN", "Nombre erreur de requetes API"])
            reportWriter.writerow([str(numScan),str(numSupposedToAttend),str(self.absents) + ' (' + '%.2f'%percentAbsents + '%)', str(
                self.presents) + ' (' + '%.2f'%percentPresents + '%)', str(self.wrong_presents) + ' (' + '%.2f'%percentWrongPresent + '%)', str(scanningTime), self.errorsRequestAPI])
        
    """
        Cette methode permet de verifir la validite d'un fichier report 

    """
    def __checkReportCorrectness(self,pathToReport):
        with open(pathToReport, self.read) as reportFile:
            reportReader = self.csv.reader(reportFile)

            header = next(reportReader)

            if(len(header) != 7):#Car le fichier report contient 7 elements si on commence a compter a partir de 1
                return False
            else:
                return True
        
        return False


    """
        Cette methode permet de compter le nombre de lines dans le fichier csv

        arguement : chemin vers le fichier dont on souhaite connaitre le nombre de lignes
    """

    def __row_count(self, path):
        file = open(path)
        reader = self.csv.reader(file)
        lines = len(list(reader))

        return lines

    """
        Cette methode permet de faire log des erreurs dans un fichier afin de faire du debug plus facilement
    """

    def create_DSI_errlog(self, errors_list, initial_path):
        Logfilename = '/'.join(initial_path.split('/')[:-1])+"/ERREURS_"+initial_path.split(
            '/')[-1].replace('.csv', '').replace(' ', '_')+".log"
        try:
            with open(Logfilename, 'w') as logfile:
                for error in errors_list:
                    logfile.write("--> "+error+"\n")
                logfile.close()
                return True
        except IOError:
            print("Can't write log file on USB Key (no write permission)")
            return False

    """
        Cette methode permet de verifier que le fichier de la DSI fournit par l'admin respecte la structure precisee dans le files/readme.md

        NOM,PRENOM,ETUD_NUMERO,NO_INDIVIDU,EMAIL,LOGIN,FORMATION,NIVEAU
    """

    def checkDSIFileStructure(self):
        with open(self.initFilePath, self.read) as DSI_File:
            DSI_Reader = self.csv.reader(DSI_File)
            errors = []
            try:
                header = next(DSI_Reader)
                num_col = len(header)
            except StopIteration:
                print("File is empty")
                errors.append("Le fichier est vide")
                self.create_DSI_errlog(errors, self.initFilePath)
                return False

            StandardHeader = ["NOM", "PRENOM", "ETUD_NUMERO",
                              "NO_INDIVIDU", "EMAIL", "LOGIN", "FORMATION", "NIVEAU"]

            # Check header
            if(num_col != 8):
                print("Error in header length")
                errors.append(
                    "Le nombre de colonnes de l'entete (actuellement de "+str(num_col)+") doit etre egal a 8")
            else:
                for i in range(8):
                    if header[i] != StandardHeader[i]:
                        errors.append("La cellule de l'entete en place "+str(
                            i+1)+" devrait etre nommee "+StandardHeader[i]+" et non "+str(header[i]))
                        print("Error in header titles")

            line_index = 1
            total_logins = []  # used to check login uniqueness in file
            # Check first line
            try:
                line = next(DSI_Reader)
                line_index += 1
            except StopIteration:
                print("Header is there, but nothing after")
                errors.append("Aucune ligne apres l'entete")
                self.create_DSI_errlog(errors, self.initFilePath)
                return False

            # Check other lines
            while True:
                num_col = len(line)
                err_prefix = "Ligne "+str(line_index)+" : "
                if(num_col == 8):
                    for i in [0, 1]:
                        if type(line[i]) != str or len(line[i]) == 0:
                            print(err_prefix + "cell "+str(i) +
                                  " is not string or is empty")
                            errors.append(
                                err_prefix+"La cellule "+StandardHeader[i]+" doit etre une chaine de caracteres non vide")
                    if type(line[5]) != str or len(line[5]) == 0:
                        print(err_prefix + "cell "+str(5) +
                              " is not string or is empty")
                        errors.append(
                            err_prefix+"La cellule "+StandardHeader[5]+" doit etre une chaine de caracteres non vide")
                    else:
                        if line[5] in total_logins:
                            print(err_prefix + "login duplicate")
                            errors.append(
                                err_prefix+"Duplication du login "+line[5])
                        total_logins.append(line[5])

                    for i in [2, 3]:
                        if not line[i].isdigit():
                            print(err_prefix + "cell " +
                                  StandardHeader[i]+" is not a number")
                            errors.append(
                                err_prefix+"La cellule "+StandardHeader[i]+" doit etre un nombre entier")
                    if not self.re.match("^[a-z-]+\.[a-z-]+[0-9-]*@utbm\.fr$", line[4]):
                        print(err_prefix +
                              "E-mail doesnt match utbm mail address regex")
                        errors.append(
                            err_prefix+"L'adresse e-mail ne correspond pas au format des adresses UTBM")

                else:
                    print(err_prefix + "number of columns (" +
                          str(num_col)+") is different from 8")
                    errors.append(
                        err_prefix+"Le nombre de cellules (actuellement de "+str(num_col)+") doit etre egal a 8")

                try:
                    line = next(DSI_Reader)
                    line_index += 1
                except StopIteration:  # End Of File
                    # TODO: check logins are unique
                    if errors:
                        self.create_DSI_errlog(errors, self.initFilePath)
                        return False
                    return True

    def ImportDSIFile(self, formattedDatetime):
        source = self.initFilePath
        destination = self.structConfig.structure["DSI_lists"] + \
            formattedDatetime+".csv"
        try:
            self.shutil.copyfile(source, destination)
        except:
            print("Error happened during importation of DSI file")
            return False
        return True
        
    def ParseReport(self): #return the following array : 
        with open(self.initFilePath,self.read) as Report_File:
            Report_Reader = self.csv.reader(Report_File)
            next(Report_Reader)
            try:
                res = []
                for item in Report_Reader:
                    res.append(item)
                return res
            except Exception as e:
                print("Error while reading report.csv : ")
                print(e)
                return False


# prefer absolute path over relative ones for parentDir
def listDirectory(parentDir, list_folders, list_files, only_csv):
    if only_csv and not list_files:
        print("Incoherent parameters")
        return
    res = []
    for r, d, f in os.walk(parentDir):
        if list_folders:
            for directory in d:
                res.append(directory)
        if list_files:
            for file in f:
                if not only_csv or file.endswith(".csv"):
                    res.append(file)
        break  # prevents from deeper search (we stop at level 1)
    return res



if __name__ == '__main__':
    try:
        pass
    except Exception as e:
        print(e)
