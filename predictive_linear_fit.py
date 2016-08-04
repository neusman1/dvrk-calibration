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

    dvrk_or_opto_wrench = raw_input('use forces form dvrk or optoforce sensor? type "dvrk" or "opto" then hit [enter] \n ')
    for filetype in range(len(list_of_position_files)):
        for filename in range(len(list_of_position_files[filetype])):
            reader = list(csv.reader(open('ForceTestingData/' +list_of_position_files[filetype][filename],"rb"), delimiter=','))
            if dvrk_or_opto_wrench == 'opto':
                coef = float(list(reader)[0][-1:][0])
            elif dvrk_or_opto_wrench == 'dvrk':
                xForce = []
                xCartesian = []
                xAtracsys = []
                tested_list = []
                for cord in range(2,len(reader)):
                    xForce.append(float(reader[cord][0]))
                    xCartesian.append(float(reader[cord][23]))
                    xAtracsys.append(float(reader[cord][6]))
                cartesian_v_atracsys_diff = [ a - b for a,b in zip( xCartesian,  xAtracsys) ]
                untested_list = zip(xForce, cartesian_v_atracsys_diff)
                for cord in untested_list:
                    if cord[0] > 0.08:
                        tested_list.append(cord)
                force_for_plotting, diff_for_plotting = zip(*tested_list)
                force_for_plotting = list(force_for_plotting)
                diff_for_plotting = list(diff_for_plotting)
                coef, intercept = numpy.polyfit( force_for_plotting, diff_for_plotting, 1)
            else:
                print 'incorrect answer format'
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
    """
    #predicted_slope at z pos of -0.1425
    predicted_slope = (slope * -0.1425) + offset
    reader = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1425_2016-8-4-15-45-31.csv' ,"rb"), delimiter=','))
    """
    #predicted_slope at z pos of -0.1925
    predicted_slope = (slope * -0.1925) + offset
    reader = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1925_2016-8-4-15-48-11.csv' ,"rb"), delimiter=','))
    
    gathered_slope = float(list(reader)[0][-1:][0])
    print 'gathered_slope: ', gathered_slope
    print 'predicted_slope: ', predicted_slope

    Force = [[],[],[]]
    Cartesian = [[],[],[]]
    Atracsys = [[],[],[]]
    calculated_absolute = [[],[0],[0]]
    error_values = [[],[],[]]
    error_without_correction = [[],[],[]]

    for row in range(2, len(reader)):
        for axis in range(3):
            if dvrk_or_opto_wrench == 'opto':
                Force[axis].append(float(reader[row][(29 + axis)]))
            elif dvrk_or_opto_wrench == 'dvrk':
                Force[axis].append(float(reader[row][(0 + axis)]))
            Cartesian[axis].append(float(reader[row][(23 + axis)]))
            Atracsys[axis].append(float(reader[row][(6 + axis)]))
    for coordinate in range(len(Force[0])):
            calculated_absolute[0].append( Cartesian[0][coordinate] - (Force[0][coordinate] * predicted_slope) )
            calculated_absolute[1].append( Cartesian[1][coordinate] ) #only modify axis under testing
            calculated_absolute[2].append( Cartesian[2][coordinate] )
    for axis in range(3):
        error_corrected = []
        error_uncorrected = []
        for coordinate in range(len(Cartesian[0])):
            error_corrected.append( calculated_absolute[axis][coordinate] - Atracsys[axis][coordinate] )
            error_uncorrected.append( Cartesian[axis][coordinate] - Atracsys[axis][coordinate] )
        error_values[axis] = ( math.fsum(error_corrected)/len(error_corrected) )
        error_without_correction[axis] = ( math.fsum(error_uncorrected)/len(error_uncorrected) )
    print error_values
    print error_without_correction
    
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
