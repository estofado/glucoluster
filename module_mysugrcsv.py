# -*- coding: utf-8 -*-
import csv
import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

def readMysugrCsvGCA(path):
    '''reads glucose, carbohydrate and insulin data from csv
    returns only days that have entries in all categories
    returns vector with
        0th entry being combined data [[date, [glucoentries], [carboentries], [insulinentries]], ...]
        1st entry being just [[date + glucoentries],...]
        2nd  "     "     " [[date + carboentries],...]
        3rd  "     "     " [[date + insulineentries],...]'''
    datgluc = []
    datcarb = []
    datinsu = []
    #read data
    with open(path,"rb") as source:
        rdr= csv.reader( source,delimiter=',' )
        i = 1
        gluc_day = ''
        carb_day = ''
        insu_day = ''
        days_carb = []
        days_insu = []
        
        for row in reversed(list(rdr)):
            print row
            #glucose
            if row[2] == '' or row[0] =='Datum' or row[0] =='Date':
                continue            
            else:
                i = i+1        
                #print row
                if row[0] != gluc_day: #für jeden Tag neuer subvector
                    gluc_day = row[0]
                    datgluc.append([gluc_day, []])
                if row[2] != "":                 # jeder subvector besteht aus
                                                #Datum und [[Zeit,Wert],[Zeit,Wert]]
                                                #Zeit als Anzahl Minuten des Tages
                    #print row[1]            
                    #print "___",float(row[2])
                    hours = int(row[1].split(":")[0])
                    minutes = int(row[1].split(":")[1])
                    datgluc[-1][-1].append([hours*60+minutes, float(row[2])])
            #food
            if row[4] == '' or row[0] =='Datum' or row[0] =='Date':
                continue            
            else:
                i = i+1        
                #print row
                
                if row[0] != carb_day: #für jeden Tag neuer subvector
                    carb_day = row[0]
                    datcarb.append([carb_day, []])
                    days_carb.append(carb_day)
                if row[4] != "":                 # jeder subvector besteht aus
                                                #Datum und [[Zeit,Wert],[Zeit,Wert]]
                                                #Zeit als Anzahl Minuten des Tages
                    #print row[1]            
                    #print "___",float(row[2])
                    hours = int(row[1].split(":")[0])
                    minutes = int(row[1].split(":")[1])
                    datcarb[-1][-1].append([hours*60+minutes, float(row[4])])
            #insulin
            if row[3] == '' or row[0] =='Datum' or row[0] =='Date':
                continue            
            else:
                i = i+1        
                #print row
                if row[0] != insu_day: #für jeden Tag neuer subvector
                    insu_day = row[0]
                    datinsu.append([insu_day, []])
                    days_insu.append(insu_day)
                if row[3] != "":                 # jeder subvector besteht aus
                                                #Datum und [[Zeit,Wert],[Zeit,Wert]]
                                                #Zeit als Anzahl Minuten des Tages
                    #print row[1]            
                    #print "___",float(row[2])
                    hours = int(row[1].split(":")[0])
                    minutes = int(row[1].split(":")[1])
                    datinsu[-1][-1].append([hours*60+minutes, float(row[3])])
    data = [] #combines all data in one structure
    glucodata = [] #only glucose-values for days with all fields present
    carbodata = []
    insudata = []
    for day in datgluc:
        datum = day[0]
        try:
            weekday = datetime.datetime.strptime(datum, '%d-%b-%y').strftime('%A')
        except:
            weekday = datetime.datetime.strptime(datum, '%d.%m.%Y').strftime('%A')
        try:
            carb_index = days_carb.index(datum)
        except Exception:
            carb_index = -1
            pass
        try:
        	   insu_index = days_insu.index(datum)
        except Exception: 
            insu_index = -1
            pass
        if carb_index != -1 and insu_index != -1:
            #print "append", datum
            glucodata.append(day)                                
            carbodata.append([datum,datcarb[carb_index][1]])
            insudata.append([datum,datinsu[insu_index][1]])
            
#            day.append(" ")
 #           day[-1] = day[-2]
  #          day[-2] = weekday               
   #         day.append(datcarb[carb_index][1])
    #        day.append(datinsu[insu_index][1])
            data.append([datum, weekday, day[1],datcarb[carb_index][1],datinsu[insu_index][1]]) 
    return [data, glucodata, carbodata, insudata]

def filterDays(data, threshold = 3):   
    ''' Remove days with less than 3 measurements from dataset and saves their 
    names in second output structure'''
    i = 0            
    while i < len(data):
        if len(data[i][1]) < threshold:
            data.pop(i)
            continue
        i = i+1
    #Distanzmatrix wird leider ohne Datum der Tage (= "Labeldates") gespeichert, deswegen hier
        #die Daten aus data extrahieren
    i = 0
    labeldates = []            
    while i < len(data):
        labeldates.append(data[i][0])
        i = i+1
    return [data, labeldates]

def saveInterpolatedCsv(path,data):
    '''Save interpoolated days to a csv-File for inspecting them with
    Weka Explorer/Knowledge Flow or try some Matlab stuff with it'''
    #Interpolierte Tageswerte in CSV zwischenspeichern z.B. für Analyse mit Weka 
        #Explorer
    with open(path,"wb") as result:
        wtr = csv.writer( result )
        heading = ["date"]
        for i in range(len(data[0][1])):
            heading.append("h"+str(i))
        wtr.writerow(heading)
        for day in data:
            listrow = [day[0]]
            for elem in day[1]:
                listrow.append(elem)
            wtr.writerow( listrow )
