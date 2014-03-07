# -*- coding: utf-8 -*-

import mlpy
import numpy as np

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
