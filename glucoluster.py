# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 09:42:31 2014

@author: estofado
"""

import csv
import decimal
import math
#from sklearn.cluster import spectral_clustering 
#from sklearn.cluster import DBSCAN
from scipy.cluster import hierarchy
import numpy as np
#import scipy
import mlpy
import matplotlib.pyplot as plt

def readMysugrCsv(path):
    '''CSV needs some manual preprocessing right now, like deleting days 
    without measurements, see example csv'''
    dat = []
    #read data
    with open(path,"rb") as source:
        rdr= csv.reader( source )
        i = 1
        date = ''
        for row in reversed(list(rdr)):
            i = i+1        
            #print i
            if row[0] != date: #für jeden Tag neuer subvector
                date = row[0]
                dat.append([date, []])
            if row[2] != "":                        # jeder subvector besteht aus
                                            #Datum und [[Zeit,Wert],[Zeit,Wert]]
                                            #Zeit als Anzahl Minuten des Tages
                #print row[1]            
                #print "___",float(row[2])
                hours = int(row[1].split(":")[0])
                minutes = int(row[1].split(":")[1])
                dat[-1][-1].append([hours*60+minutes, float(row[2])])
    return dat
    
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

def linearize(where, times, values):
    '''times und values sind zwei Vektoren [125,460] und [6.5,7.8], die dann
    an der Stelle where den linear interpolierten Wert zurückgeben'''
    slope = (values[1]-values[0])/float(times[1]-times[0])
    if where > times[1] or where < times[0]:
        raise ValueError('Interpolation is recommended between boundaries')
    interpolation =  values[0]+(where-times[0])*slope
    return int(interpolation * 100) / 100.0

def findpos(where, day):
    '''Hilft, welche Grenzwerte zur Interpolation herangezogen werden sollen
    ist day= ['11-04-1989',[[230,8.0],[430,9.1],[670,9.0],[1010,5.0]]]
    dann wird für where= 300 die 1 ausgegeben, was bedeuten soll, zum 
    Interpolieren bitte die Werte an den Stellen 230 und 430 zu nehmen'''
    if where >= 24*60:
        raise ValueError('Time value too large')    
    for i in range(len(day[1])):
        if day[1][-1][0] < where:
            pos = -1
            break
        if day[1][i][0] < where and day[1][i+1][0] > where:
            pos = i+1            
            break
        else:
            pos = 0
    return pos
    
def interpolate(data, resolution = 48):
    """Transformiert die eingelesenen Daten so, dass
    die Einträge für die Zeit (in Minuten seit 0 Uhr) und die Messwerte
    durch Interpolation in einen Vektor der Länge resolution
    überführt werden. resolution == 48 bedeutet also Interpolation auf 
    Halbstunden-Werte (24*60/resolution == 30)"""
#   pointsinspace = np.zeros(resolution)
#   pointsinspace =    pointsinspace.transpose()
    for day in data:
        #print "DAY:", day
        h48 = []
        for i in range(resolution):
            #print "i: ", i
            pos = findpos(i*(24*60/resolution), day)
            if pos > 0 and pos < len(day[1])-1:
                #print "if"
                #print "minutes",i*30
                #print "POS: ",pos
                                
                times = [day[1][pos-1][0], day[1][pos][0]]
                #print times
                values = [day[1][pos-1][1], day[1][pos][1]]
                #print values                
                h48.append(linearize(i*(24*60/resolution), times, values))
            else:
                #print "else"
                h48.append(day[1][pos][1])
            #print day[1][j][0]    
        day[1] = h48
        #print pointsinspace
        
        #line = np.array(h48)
        #line = line.transpose()
        #print line
        #pointsinspace = np.concatenate((pointsinspace, line), axis=0)
    #print pointsinspace
    return data

#def rotateseq(dayseq):
#    '''Verschiebt Messwertesequenz um eine Position, wird 
#    in euclidianrotationdistance verwendet
#    rotateseq([1,2,3]) gibt [2,3,1]'''
#    return dayseq[1:]+[dayseq[0]]
#
#def euclidiandistance(day1seq, day2seq):
#    '''Berechnet euklidischen Abstand zwischen zwei Blutzuckersequenzen
#    distance([1,2,3],[3,2,1]) gibt sqrt(2) = 1.41...'''    
#    summe = 0    
#    for i in range(len(day1seq)):
#        summe = summe + (day1seq[i]-day2seq[i])**2
#    return math.sqrt(summe)
#    
#def euclidianrotationdistance(day1seq, day2seq):
#    '''Tage sollen nicht unähnlich sein, nur weil man 3 Stunden später
#    aufgestanden ist. Deswegen wird einer der Tage mir rotateseq nach und nach
#    vollständig durchrotiert, jedes Mal die euklidische Distanz berechnet
#    und dann das Minimum dieser Werte genommen
#
#    euclidianrotationdistance([0,0,1,2,3,0,0,0], [0,0,0,0,0,1,2,3])
#    gibt [distance = 0.0, shift = 3] aus, weil mit drei Rotationen die Vektoren ineinander
#    überführt werden konnen.
#    '''
#    minimum = euclidiandistance(day1seq, day2seq)
#    shift = 0    
#    rotday2seq = day2seq
#    for i in range(len(day1seq) -1):
#        rotday2seq = rotateseq(rotday2seq)
#        reuc = euclidiandistance(day1seq, rotday2seq)
#        if reuc < minimum:
#            minimum = reuc
#            shift = i+1
#    return [minimum, shift]    


def distancematrix(data, metric = mlpy.dtw_std):
    '''Nimmt data mit interpolierten Blutzuckerwerten und erstellt eine 
    vollständige Distanzmatrix, die alle Entfernungen zwischen den Tagesverläufen
    entsprechend der in dieser Funktion benutzten Metrik berechnet.
    Standardmäßig wird die Dynamic Time Warp Distance benutzt aus dem Paket MLpy'''
    distmat = np.zeros((len(data), len(data)))
    for i in range(len(data)):
        for j in range(i, len(data)):
            distmat[i, j] = metric(data[i][1], data[j][1], dist_only=True)
            if j != i:            
                distmat[j, i] =distmat[i, j]
    #np.savetxt("DISTANCEmatrix.txt", distmat, delimiter=",")
    return distmat
    
def convertDistToSim(distmatrix):
    '''Manche Cluster-Algorithmen brauchen keine Distanz- sondern eine 
    Ähnlichkeitsmatrix, Umwandlung mal wieder ein bisschen willkürlich'''
    med = np.median(distmatrix)
    simmatrix = np.zeros((len(distmatrix), len(distmatrix)))
    for i in range(len(simmatrix)):
        for j in range(len(simmatrix)):
            simmatrix[i][j] = math.exp(-distmatrix[i][j]/(med))
    return simmatrix

def averageday(data, dayvector, labeldates):
    '''errechnet Durchschnitt und Standardabweichung einer Menge von Tagen, 
    die als Vektor von Indices in data übergeben werden. Bild wird geplottet'''
    means = []
    stdev = []
    plt.figure()
    for i in range(48):  
        measurements = []
        for index in dayvector:
            #print data[index][1][i]
            measurements.append(data[index][1][i])
            #plt.plot(np.linspace(0.0, 24.0, num=len(data[index][1])),data[index][1])

        means.append(np.median(measurements))
        stdev.append(np.std(measurements)/2)
    #print len(means), len(measurements)
    # make a figure and an axes object
    
    plt.axis([-1, 25, 20, max(measurements)+100])
    plt.errorbar(np.linspace(0.0, 24.0, num=len(means)),means, yerr=(stdev,stdev))
#    plt.errorbar(x, y, xerr=0.2, yerr=0.4)
    plt.xticks(np.arange(0, 25, 6))
    plt.xlabel("Tageszeit / h")
    plt.ylabel('Durchschnittswerte und Standardabweichungen zur Tageszeit')
    title = "Durchschnitt von " +str(len(dayvector)) + " Tagen inklusive " + labeldates[dayvector[0]]    
    plt.title(title)
    #days = ""
    #for index in dayvector:
     #   days = days + labeldates[index] + ", " 
    #plt.text(0, -13, days, fontsize=8)
    
def clusterAndPlotAverages(distmatrix,  labeldates, noOfClusters=0, cutoff=0, clustersize=0):
    '''runs hierarchical clustering on the given distance matrix using UPGMA 
    and plots the clusters average days, set either noOfClusters or cutoff as 
    keyword arguments and specify clustersize to plot only clusters with a 
    minimum size'''
    if cutoff == 0: #method="average" == UPGMA   
        clusters = hierarchy.fclusterdata(distmatrix, noOfClusters, criterion='maxclust', metric='euclidean', method='average')
    if noOfClusters == 0:
        clusters = hierarchy.fclusterdata(distmatrix, cutoff, criterion='distance', metric='euclidean', method='average')
    if noOfClusters == 0 and cutoff == 0:
        raise ValueError('Call clusterAndPlotAverages with specifying either cutoff or noOfClusters')
    #print clusters
    groupedDays = []
    for i in range(max(clusters)):
        groupedDays.append([])
    for i in range(len(clusters)):
        groupedDays[clusters[i]-1].append(i)
    for group in groupedDays:
        if len(group)> clustersize:
            averageday(data, group, labeldates)
 
###############################################################################

   
data = readMysugrCsv("/home/damian/Desktop/Diabetes-Data/DiabMeasurements.csv")
#Datensatz filtern: Nimm nur Tage mit mindestens ... Einträgen
filtered = filterDays(data, threshold = 11)
data = filtered[0]
labeldates = filtered[1]


decimal.getcontext().prec = 2

data = interpolate(data)

saveInterpolatedCsv("/home/damian/Desktop/Diabetes-Data/DiabInterpolMeasurements.csv",data)

#Distanzmatrix aus den interpolierten Tagesverläufen berechnen
# dazu in distancematrix die DYNAMIC TIME WARPING-Metrik benutzen
# try whatever metric you think is suitable! write your own!    
distmatrix = distancematrix(data, metric = mlpy.dtw_std)
simmatrix = convertDistToSim(distmatrix)


with open("DaysDIST.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(distmatrix)

with open("DaysSIM.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(simmatrix)

##DBSCAN
#db = DBSCAN().fit(simmatrix)
#core_samples = db.core_sample_indices_
#labels = db.labels_
#
#n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
#
#print('Estimated number of clusters: %d' % n_clusters_)
#
##SPECTRAL CLUSTERING
#labels = spectral_clustering(simmatrix, n_clusters=7, eigen_solver='arpack')
#plt.hist(labels)
##plt.show()

#DENDROGRAMM aus scikit-learn
#'average' macht ein UPGMA-Clustering
dendro = hierarchy.linkage(distmatrix, method='average')
hierarchy.dendrogram(dendro,labels=labeldates)

noOfClusters = 10

clusterAndPlotAverages(distmatrix, labeldates,noOfClusters = 3)

#averageday(data, [32,22,71,44,47,101])
#averageday(data, [32,22,71])
#averageday(data, [44,47,101])
