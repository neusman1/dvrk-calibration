#!/usr/bin/env python

#Created on Feburary 3, 2017
#Author: Nick Eusman

import sys
import csv
import os
import time
import datetime


def run():

    ##compute k0,k1,k2 for each point
    ##output raw into one file and avg in console
    k_sums = [0.0, 0.0, 0.0]
    counter = 0
    files_for_evaluation = []
    threshold = [0.2, 0.3, 0.3]
    skips = [0,0,0]
    for file in os.listdir("ForceTestingDataAllAxis"): #sort files
        if file.startswith("force_fixed_point_output"):
            files_for_evaluation.append(file)
    
    csv_file_name = 'ForceTestingDataAllAxis/force_fixed_point_k_values' + ('-'.join(str(x) for x in list(tuple(datetime.datetime.now().timetuple())[:6]))) + '.csv'
    print "\n Values will be saved in: ", csv_file_name
    f = open(csv_file_name, 'wb')
    writer = csv.writer(f)

    for filenumber in range(len(files_for_evaluation)):
        reader = list(csv.reader(open('ForceTestingDataAllAxis/' +files_for_evaluation[filenumber],"rb"), delimiter=','))
        print 'loading: ', files_for_evaluation[filenumber]
        for row in range(21,len(reader)):
            k_values = [0.0,0.0,0.0]
            for joint in range(3):
                if not((float(reader[row][joint + 10]) < threshold[joint]) and (float(reader[row][joint + 10]) > -threshold[joint])):
                    k = 0
                    if joint == 0 or joint == 1:
                        k =(( float(reader[row][joint]) - float(reader[row][joint + 3]) ) / ( float(reader[row][5]) * float(reader[row][joint + 10])))
                    elif joint == 2:
                        k =(( float(reader[row][joint]) - float(reader[row][joint + 3]) ) / ( float(reader[row][joint + 10])))
                    k_values[joint] = k
                    k_sums[joint] += k
                else:
                    skips[joint] += 1    
                writer.writerow([float(reader[row][5]), k_values[0], k_values[1],k_values[2] ])
            counter += 1
    print 'k values: ', (k_sums[0] / (counter - skips[0])), (k_sums[1] / (counter - skips[1])), (k_sums[2] / (counter - skips[2])) 


    
run()
