#!/usr/bin/env python

#Created on August 3, 2016
#Author: Nick Eusman

#To Do:
# -finish code

import numpy
import csv
import os
import matplotlib.pyplot as plt
import math

def run():
    list_of_position_files = [ [],[],[],[],[] ]
    list_of_coefficients_with_z_position = []
    zforce = []
    xCartesian = []
    xAtracsys = []
    tested_list = []
    for file in os.listdir("ForceTestingData"):
        if file.startswith("force_testing_output"):
            if '-0.105' in file:
                list_of_position_files[0].append(file)
            elif '-0.13' in file:
                list_of_position_files[1].append(file)
            elif '-0.155' in file:
                list_of_position_files[2].append(file)
            elif '-0.18' in file:
                list_of_position_files[3].append(file)
            elif '-0.205' in file:
                list_of_position_files[4].append(file)


    for filetype in range(len(list_of_position_files)):
        for filename in range(len(list_of_position_files[filetype])):
            reader = list(csv.reader(open('ForceTestingData/' +list_of_position_files[filetype][filename],"rb"), delimiter=','))
            coef = float(list(reader)[0][-1:][0])
            list_of_coefficients_with_z_position.append([ round((-0.105 -( 0.025 * filetype)), 5), coef])

    #print list_of_coefficients_with_z_position

    zpositions, coefficients = zip(*list_of_coefficients_with_z_position)

    slope, offset = numpy.polyfit(zpositions, coefficients, 1)
    #print slope
    """
    plt.plot(zpositions, coefficients, '.')
    xaxis = numpy.arange(-0.21, 0, 0.025)
    plt.plot(xaxis, slope*xaxis + offset, '-')
    plt.axis([-0.21, -0.1 , 0.0005, 0.002])
    plt.show()
    """
    #predicted_slope at z pos of -0.1425
    predicted_slope = (slope * -0.1425) + offset
    reader = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1425_2016-8-4-13-35-29.csv' ,"rb"), delimiter=','))
    gathered_slope = float(list(reader)[0][-1:][0])
    print 'gathered_slope: ', gathered_slope
    print 'predicted_slope: ', predicted_slope

    Force = [[],[],[]]
    Cartesian = [[],[],[]]
    Atracsys = [[],[],[]]
    caluculated_absolute = [[],[],[]]
    error_values = [[],[],[]]
    
    for row in range(2, len(reader)):
        for axis in range(3):
            Force[axis].append(float(reader[row][(29 + axis)]))
            Cartesian[axis].append(float(reader[row][(23 + axis)]))
            Atracsys[axis].append(float(reader[row][(6 + axis)]))
    for coordinate in range(len(Force[0])):
        for axis in range(3):
            caluculated_absolute[axis].append( Cartesian[axis][coordinate] - (Force[axis][coordinate] * predicted_slope) )
    for axis in range(3):
        error = []
        for coordinate in range(len(Cartesian[0])):
            error.append( caluculated_absolute[axis][coordinate] - Atracsys[axis][coordinate] )
        error_values[axis] = ( math.fsum(error)/len(error) )
    print error_values
    
    """
    dvrk_wrench = []
    opto_wrench = []
    
    for row in range(2, len(reader)):
        opto_wrench.append(reader[row][31])
        dvrk_wrench.append(reader[row][0])

    plt.plot(opto_wrench, dvrk_wrench, '.')
    plt.show()
    """

run()
