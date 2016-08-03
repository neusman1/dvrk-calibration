#!/usr/bin/env python

#Created on August 3, 2016
#Author: Nick Eusman

#To Do:
# -finish code

import numpy
import csv
import os
import matplotlib.pyplot as plt

def run():
    list_of_position_files = [ [],[],[],[],[] ]
    list_of_ln_coefficients_with_z_position = []
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
            reader = csv.reader(open('ForceTestingData/' +list_of_position_files[filetype][filename],"rb"), delimiter=',')
            ln_coef = float(list(reader)[0][-1:][0])
            list_of_ln_coefficients_with_z_position.append([ round((-0.105 -( 0.025 * filetype)), 5), ln_coef])
            
    print list_of_ln_coefficients_with_z_position

    zpositions, lncoefficients = zip(*list_of_ln_coefficients_with_z_position)

    plt.plot(zpositions, lncoefficients, 'ro')
    plt.axis([-0.21, -0.1 , 0.0005, 0.002])
    plt.show()

    B, A = numpy.polyfit(zpositions, lncoefficients, 1)
    print B, A

    prediction = (A *float(raw_input('enter a z position'))) + B
    print 'the predicted ln coefficient is: ', prediction
run()
