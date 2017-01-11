#!/usr/bin/env python

#Created on January 11, 2017
#Author: Nick Eusman

#To Do:
# -change existing code to fit new format

import numpy
import csv
import os
import matplotlib.pyplot as plt
import math
import datetime

def run():
  
    slopes = []
    offsets = []
    reader1 = list(csv.reader(open('force_testing_results_at_ ... .csv' ,"rb"), delimiter=','))#needs acual files
    for axis in range(3):
      slopes.append(float(reader1[axis + 1][1]))
      offsets.append(float(reader1[axis + 1][2]))

####needs changes beyond htis point to account for different axis

    test_point_axis = raw_input('What axis was under testing?')
    test_point_145or195 = raw_input('Choose between the 145 or 195 test point. type either "145" or "195" then hit [enter] \n ')
    if test_point_145or195 == '145':
        #predicted_slope at z pos of -0.1425
        predicted_slope = (slope * -0.1425) + offset
        reader2 = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1425_2016-8-4-15-45-31.csv' ,"rb"), delimiter=','))  ####Will need to update later
    elif test_point_145or195 == '195':
        #predicted_slope at z pos of -0.1925
        predicted_slope = (slope * -0.1925) + offset
        reader2 = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1925_2016-8-4-15-48-11.csv' ,"rb"), delimiter=','))  ####Will need to update later
    
    gathered_slope = float(list(reader2)[0][-1:][0]) #will no longer work
    print 'gathered_slope: ', gathered_slope
    print 'predicted_slope: ', predicted_slope
    Force = [[],[],[]]
    Cartesian = [[],[],[]]
    Atracsys = [[],[],[]]
    calculated_absolute = [[],[0],[0]]
    error_values = [[],[],[]]
    error_without_correction = [[],[],[]]
    for row in range(2, len(reader2)):
        for axis in range(3):
            if dvrk_or_opto_wrench == 'opto':
                Force[axis].append(float(reader2[row][(29 + axis)]))
            elif dvrk_or_opto_wrench == 'dvrk':
                Force[axis].append(float(reader2[row][(0 + axis)]))
            Cartesian[axis].append(float(reader2[row][(23 + axis)]))
            Atracsys[axis].append(float(reader2[row][(6 + axis)]))
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
        for sample in range(20): #FINISH
            error_values[axis].append(  math.fsum(error_corrected[0 + (20 * sample):20 + (20 * sample)])/ 20  ) 
            error_without_correction[axis].append(  math.fsum(error_uncorrected[0 + (20 * sample):20 + (20 * sample)])/ 20  ) 
    #print error_values
    #print error_without_correction
    print 'final point error  for ' + test_point_145or195 + ' test point with ' + dvrk_or_opto_wrench + ' forces with deflection correction'
    print error_values[0][19]
    print 'final point error  for ' + test_point_145or195 + ' test point with ' + dvrk_or_opto_wrench + ' forces without deflection correction'
    print error_without_correction[0][19]
    
    
    
    
    
    
    
 run()
