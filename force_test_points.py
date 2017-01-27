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
    test_files = [ [ [], [], [] ], [ [], [], [] ] ]
    for file in os.listdir("ForceTestingDataAllAxis"): #sort files
        if file.startswith("force_data_collection_output"):
            if '-0.1425' in file:
                if 'x_axis' in file:
                    test_files[0][0].append(file)
                elif 'y_axis' in file:
                   test_files[0][1].append(file)
                elif 'z_axis' in file:
                    test_files[0][2].append(file)
            elif '-0.1925' in file:
                if 'x_axis' in file:
                    test_files[1][0].append(file)
                elif 'y_axis' in file:
                    test_files[1][1].append(file)
                elif 'z_axis' in file:
                    test_files[1][2].append(file)
    reader1 = list(csv.reader(open('ForceTestingDataAllAxis/force_testing_results_at_2017-1-25-20-51-36.csv' ,"rb"), delimiter=',')) #needs actual file
    for axis in range(3):
      slopes.append(float(reader1[axis + 1][1]))
      offsets.append(float(reader1[axis + 1][2]))


    for filedepth in range(len(test_files)):
        for fileaxis in range(len(test_files[filedepth])):
            predicted_slope = (slopes[fileaxis] * ( -0.1425 + ( -0.05 * filedepth ))) + offsets[fileaxis]
            reader = list(csv.reader(open('ForceTestingDataAllAxis/' + str(test_files[filedepth][fileaxis][0]),"rb"), delimiter=','))

            #calculate coefficient
            axisForce = []
            axisCartesian = []
            axisAtracsys = []
            tested_list = []
            for cord in range(1,len(reader)): #set atracsys, force (from dvrk), and cartesian based on axis which was tested
                if fileaxis == 0:
                    axisForce.append(float(reader[cord][0])) ##change if optoforce used
                    axisCartesian.append(float(reader[cord][23]))
                    axisAtracsys.append(float(reader[cord][6]))
                elif fileaxis == 1:
                    axisForce.append(float(reader[cord][1])) ##change if optoforce used
                    axisCartesian.append(float(reader[cord][24]))
                    axisAtracsys.append(float(reader[cord][7]))
                elif fileaxis == 2:
                    axisForce.append(float(reader[cord][2])) ##change if optoforce used
                    axisCartesian.append(float(reader[cord][25]))
                    axisAtracsys.append(float(reader[cord][8]))
                        
            cartesian_v_atracsys_diff = [ a - b for a,b in zip( axisCartesian,  axisAtracsys) ]
            untested_list = zip(axisForce, cartesian_v_atracsys_diff)
            for cord in untested_list: #test if point has more than minimal force, if does, add to tested list
                if fileaxis == 0:
                    if cord[0] > 1.3 or cord[0] < -1.3: ##change if optoforce used
                        tested_list.append(cord)
                elif fileaxis == 1:
                    if cord[0] > 1.8 or cord[0] < -1.8: ##change if optoforce used
                        tested_list.append(cord)
                elif fileaxis == 2:
                    if cord[0] > 0.4 or cord[0] < -.4: ##change if optoforce used
                        tested_list.append(cord)

            force_for_plotting, diff_for_plotting = zip(*tested_list)
            force_for_plotting = list(force_for_plotting)
            diff_for_plotting = list(diff_for_plotting)
            coef, intercept = numpy.polyfit( force_for_plotting, diff_for_plotting, 1)
            gathered_slope = coef
            
            print 'gathered_slope: ', gathered_slope
            print 'predicted_slope: ', predicted_slope

    
            Force = [[],[],[]]
            Cartesian = [[],[],[]]
            Atracsys = [[],[],[]]
            calculated_absolute = [[],[],[]]
            error_values = [[],[],[]]
            error_without_correction = [[],[],[]]
            for row in range(1, len(reader)):
                for axis in range(3):
                    Force[axis].append(float(reader[row][axis]))
                    Cartesian[axis].append(float(reader[row][(23 + axis)]))
                    Atracsys[axis].append(float(reader[row][(6 + axis)]))
            for coordinate in range(len(Force[0])):
                if fileaxis == 0:#only modify axis under testing
                    calculated_absolute[0].append( Cartesian[0][coordinate] - (Force[0][coordinate] * predicted_slope) )
                    calculated_absolute[1].append( Cartesian[1][coordinate] ) 
                    calculated_absolute[2].append( Cartesian[2][coordinate] )
                elif fileaxis == 1:
                    calculated_absolute[0].append( Cartesian[0][coordinate] )
                    calculated_absolute[1].append( Cartesian[1][coordinate] - (Force[1][coordinate] * predicted_slope)) 
                    calculated_absolute[2].append( Cartesian[2][coordinate] )
                elif fileaxis == 2:
                    calculated_absolute[0].append( Cartesian[0][coordinate] )
                    calculated_absolute[1].append( Cartesian[1][coordinate] ) 
                    calculated_absolute[2].append( Cartesian[2][coordinate] - (Force[2][coordinate] * predicted_slope) )
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
                print 'final point error  for ' + str( -0.1425 + ( -0.05 * filedepth )) + ' test point with dvrk forces with deflection correction'
                print error_values[0][19]
                print 'final point error  for ' + str( -0.1425 + ( -0.05 * filedepth )) + ' test point with dvrk forces without deflection correction'
                print error_without_correction[0][19]
    
    
    
    
    
    
    
run()
