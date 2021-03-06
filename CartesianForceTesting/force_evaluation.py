#!/usr/bin/env python

#Created on August 3, 2016
#Author: Nick Eusman

#To Do:
# -change for new force_data_collection.py format (DONE)
# -no longer use optoforce data? (DONE)
# -save results in csv, and test different points in separate file? (DONE)
# -z position only needs one depth tested
# -modify minimum force for dvrk, not using old optofoce values
# -change evaluation to account for the fact that z axis will be uniform throughout ? (possibly dont need to change since it will be an average this way)

import numpy
import csv
import os
import matplotlib.pyplot as plt
import math
import datetime

def run():
    list_of_position_files = [ [ [], [], [] ], [ [], [], [] ], [ [], [], [] ], [ [], [], [] ], [ [], [], [] ] ] #list of all files sorted by their five test points and their three axis
    list_of_coefficients_with_depth = [ [], [], [] ]
    final_slopes = []
    final_offsets = []
    zforce = []
    xCartesian = []
    xAtracsys = []
    tested_list = []
    for file in os.listdir("ForceTestingDataAllAxis"): #sort files
        if file.startswith("force_data_collection_output"):
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

                print list_of_position_files[filetype][fileaxis][filename]
                print tested_list
                force_for_plotting, diff_for_plotting = zip(*tested_list)
                force_for_plotting = list(force_for_plotting)
                diff_for_plotting = list(diff_for_plotting)
                coef, intercept = numpy.polyfit( force_for_plotting, diff_for_plotting, 1) 

                list_of_coefficients_with_depth[fileaxis].append([ round((-0.105 -( 0.025 * filetype)), 5), coef])  # save force vs deflection graphs


    for axis in range(3):
        depths, coefficients = zip(*list_of_coefficients_with_depth[axis]) #save final depth vs coefficient (of force and deflection) graphs's slope and offset
        slope, offset = numpy.polyfit(depths, coefficients, 1)
        final_slopes.append(slope)
        final_offsets.append(offset)

    csv_file_name = 'ForceTestingDataAllAxis/force_testing_results_at_' + ('-'.join(str(x) for x in list(tuple(datetime.datetime.now().timetuple())[:6]))) + '.csv'
    print "\n Values will be saved in: ", csv_file_name
    f = open(csv_file_name, 'wb')
    writer = csv.writer(f)
    writer.writerow(["Axis","Slope","Offset"])
    print final_slopes
    print final_offsets
    for row in range(len(final_offsets)):
        if row == 0:
            writer.writerow(["X",str(final_slopes[row]),str(final_offsets[row])])
        elif row == 1:
            writer.writerow(["Y",str(final_slopes[row]),str(final_offsets[row])])
        elif row == 2:
            writer.writerow(["Z",str(final_slopes[row]),str(final_offsets[row])])
                
    

run()
