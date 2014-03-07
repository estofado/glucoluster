# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 09:42:31 2014

@author: estofado
""" 
import csv
import module_mysugrcsv
import module_preprocess
import module_distance
import decimal
import math
#from sklearn.cluster import spectral_clustering 
#from sklearn.cluster import DBSCAN
from scipy.cluster import hierarchy
import numpy as np
#import scipy
import mlpy
import matplotlib.pyplot as plt

import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

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
    
    plt.axis([-1, 25, 0, max(measurements)+4])
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
    
def clusterAndPlotAverages(distmatrix,  labeldates, data, noOfClusters=0, cutoff=0, clustersize=0):
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

   
glucodata =  module_mysugrcsv.readMysugrCsvGCA('/home/damian/Desktop/Diabetes_modules/damian.csv')[1]
#Datensatz filtern: Nimm nur Tage mit mindestens ... Einträgen

filtered =  module_mysugrcsv.filterDays(glucodata, threshold = 2)
glucodata = filtered[0]
labeldates = filtered[1]


decimal.getcontext().prec = 2

glucodata = module_preprocess.interpolate(glucodata)

module_mysugrcsv.saveInterpolatedCsv("/home/damian/Desktop/Diabetes_modules/DiabInterpolMeasurements.csv",glucodata)

#Distanzmatrix aus den interpolierten Tagesverläufen berechnen
# dazu in distancematrix die DYNAMIC TIME WARPING-Metrik benutzen
# try whatever metric you think is suitable! write your own!    
distmatrix = module_distance.distancematrix(glucodata, metric = mlpy.dtw_std)
#simmatrix = module_distance.convertDistToSim(distmatrix)


#with open("DaysDIST.csv", "wb") as f:
 #   writer = csv.writer(f)
  #  writer.writerows(distmatrix)

#with open("DaysSIM.csv", "wb") as f:
 #   writer = csv.writer(f)
  #  writer.writerows(simmatrix)

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

clusterAndPlotAverages(distmatrix, labeldates, glucodata ,cutoff=200)#noOfClusters = 3)

#averageday(data, [32,22,71,44,47,101])
#averageday(data, [32,22,71])
#averageday(data, [44,47,101])

####################FORECAST

#container = module_mysugrcsv.readMysugrCsvGCA('/home/damian/Desktop/Diabetes-Forecast/Export.csv')
