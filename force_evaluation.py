#!/usr/bin/env python

#Created on August 3, 2016
#Author: Nick Eusman

#To Do:
# -change for new force_testing.py format
# -no longer use optoforce data?
# -save results in csv, and test different points in separate file?

import numpy
import csv
import os
import matplotlib.pyplot as plt
import math
import datetime

def run():
    list_of_position_files = [ [ [], [], [] ], [ [], [], [] ], [ [], [], [] ], [ [], [], [] ], [ [], [], [] ] ] #list of all files sorted by their five test points and their three axis
    list_of_coefficients_with_depth = [ [], [], [] ]
    final_slopes = [ [], [], [] ]
    final_offsets = [ [], [], [] ]
    zforce = []
    xCartesian = []
    xAtracsys = []
    tested_list = []
    for file in os.listdir("ForceTestingDataAllAxis"): #sort files
        if file.startswith("force_testing_output"):
            if '-0.105' in file:
                if 'x_axis' in file:
                    list_of_position_files[0][0].append(file)
                elif 'y_axis' in file:
                    list_of_position_files[0][1].append(file)
                elif 'z_axis' in file:
                    list_of_position_files[0][2].append(file)
            elif '-0.13' in file:
                if 'x_axis' in file:
                    list_of_position_files[1][0].append(file)
                elif 'y_axis' in file:
                    list_of_position_files[1][1].append(file)
                elif 'z_axis' in file:
                    list_of_position_files[1][2].append(file)
            elif '-0.155' in file:
                if 'x_axis' in file:
                    list_of_position_files[2][0].append(file)
                elif 'y_axis' in file:
                    list_of_position_files[2][1].append(file)
                elif 'z_axis' in file:
                    list_of_position_files[2][2].append(file)
            elif '-0.18' in file:
                if 'x_axis' in file:
                    list_of_position_files[3][0].append(file)
                elif 'y_axis' in file:
                    list_of_position_files[3][1].append(file)
                elif 'z_axis' in file:
                    list_of_position_files[3][2].append(file)
            elif '-0.205' in file:
                if 'x_axis' in file:
                    list_of_position_files[4][0].append(file)
                elif 'y_axis' in file:
                    list_of_position_files[4][1].append(file)
                elif 'z_axis' in file:
                    list_of_position_files[4][2].append(file)


    print list_of_position_files

    #calculate coeffiecint of slope between force and deflection for each file using dVRK forces
    for filetype in range(len(list_of_position_files)):
        for fileaxis in range(len(list_of_position_files[filetype])):
            for filename in range(len(list_of_position_files[filetype][fileaxis])):
                reader = list(csv.reader(open('ForceTestingDataAllAxis/' +list_of_position_files[filetype][fileaxis][filename],"rb"), delimiter=',')) #open each file

                #calculate coefficient
                axisForce = []
                axisCartesian = []
                axisAtracsys = []
                tested_list = []
                for cord in range(1,len(reader)): #set atracsys, force (from dvrk), and cartesian based on axis which was tested
                    if fileaxis == 0:
                        axisForce.append(float(reader[cord][0]))
                        axisCartesian.append(float(reader[cord][23]))
                        axisAtracsys.append(float(reader[cord][6]))
                    elif fileaxis == 1:
                        axisForce.append(float(reader[cord][1]))
                        axisCartesian.append(float(reader[cord][24]))
                        axisAtracsys.append(float(reader[cord][7]))
                    elif fileaxis == 2:
                        axisForce.append(float(reader[cord][2]))
                        axisCartesian.append(float(reader[cord][25]))
                        axisAtracsys.append(float(reader[cord][8]))
                        
                cartesian_v_atracsys_diff = [ a - b for a,b in zip( axisCartesian,  axisAtracsys) ]
                untested_list = zip(axisForce, cartesian_v_atracsys_diff)
                for cord in untested_list: #test if point has more than minimal force, if does, add to new list
                    if cord[0] > 0.08:
                        tested_list.append(cord)
                force_for_plotting, diff_for_plotting = zip(*tested_list)
                force_for_plotting = list(force_for_plotting)
                diff_for_plotting = list(diff_for_plotting)
                coef, intercept = numpy.polyfit( force_for_plotting, diff_for_plotting, 1) # save force vs deflection graphs

                list_of_coefficients_with_depth[fileaxis].append([ round((-0.105 -( 0.025 * filetype)), 5), coef])  


    for axis in range(3):
        depths, coefficients = zip(*list_of_coefficients_with_depth[axis]) #save final depth vs coefficient (of force and deflection) graphs's slope and offset
        slope, offset = numpy.polyfit(depths, coefficients, 1)
        final_slopes[axis].append(slope)
        final_offsets[axis].append(offset)

    csv_file_name = 'ForceTestingDataAllAxis/force_testing_results_at_' + ('-'.join(str(x) for x in list(tuple(datetime.datetime.now().timetuple())[:6]))) + '.csv'
    print "\n Values will be saved in: ", csv_file_name
    f = open(csv_file_name, 'wb')
    writer = csv.writer(f)
    writer.writerow(["Axis","Slope","Offset"])
    for row in range(len(current_atracsys_position)):
        if row == 0:
            writer.writerow(["X",str(final_offsets[row][0]),str(final_offsets[row][1])])
        elif row == 1:
            writer.writerow(["Y",str(final_offsets[row][0]),str(final_offsets[row][1])])
        elif row == 2:
            writer.writerow(["Z",str(final_offsets[row][0]),str(final_offsets[row][1])])
                
    
####FARTHEST POINT WHICH HAS BEEN UPDATED (untested)

    """
    test_point_145or195 = raw_input('Choose between the 145 or 195 test point. type either "145" or "195" then hit [enter] \n ')

    if test_point_145or195 == '145':
        #predicted_slope at z pos of -0.1425
        predicted_slope = (slope * -0.1425) + offset
        reader = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1425_2016-8-4-15-45-31.csv' ,"rb"), delimiter=','))  ####Will need to update later
    elif test_point_145or195 == '195':
        #predicted_slope at z pos of -0.1925
        predicted_slope = (slope * -0.1925) + offset
        reader = list(csv.reader(open('ForceTestingData/force_testing_output_at_z-pos_of_-0.1925_2016-8-4-15-48-11.csv' ,"rb"), delimiter=','))  ####Will need to update later
    
    gathered_slope = float(list(reader)[0][-1:][0]) #will no longer work
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
        for sample in range(20): #FINISH
            error_values[axis].append(  math.fsum(error_corrected[0 + (20 * sample):20 + (20 * sample)])/ 20  ) 
            error_without_correction[axis].append(  math.fsum(error_uncorrected[0 + (20 * sample):20 + (20 * sample)])/ 20  ) 
    #print error_values
    #print error_without_correction
    print 'final point error  for ' + test_point_145or195 + ' test point with ' + dvrk_or_opto_wrench + ' forces with deflection correction'
    print error_values[0][19]
    print 'final point error  for ' + test_point_145or195 + ' test point with ' + dvrk_or_opto_wrench + ' forces without deflection correction'
    print error_without_correction[0][19]

    """

run()
