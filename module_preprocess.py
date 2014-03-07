# -*- coding: utf-8 -*-

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
