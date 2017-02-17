#!/usr/bin/env python

#Created on February 13, 2017
#Author: Nick Eusman

#To Do:
# -allow for input from joint 1
# -figure out 3D plot as surface instead of wireframe


import numpy
import csv
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#from matplotlib import cm
import math

def run():

    files = [ [], [] ]
    effortThreshold = 0.1

    for document in os.listdir("ForceTestingDataJointSpace"):
        if document.startswith("force_joint_space_data_collection"):
            if 'joint_0' in document:
                files[0].append(document)
            if 'joint_1' in document:
                files[1].append(document)


    for documentType in range(len(files)):
        allSlopes = []
        allOffsets = []
        allDepths = []
        for document in range(len(files[documentType])):

            effortsOverThreshold = []
            dX = []
            jointDepths = []
            reader = list(csv.reader(open('ForceTestingDataJointSpace/' + files[documentType][document],"rb"), delimiter=','))

            for depth in range(14):
                effortsOverThreshold.append([])
                dX.append([])
                jointDepths.append([])

                #find range of values for given depth
                startIndex = -1
                endIndex = -1
                for row in range(1, len(reader)):
                    currentIndex = int(reader[row][0])
                    if currentIndex == depth and startIndex == -1:
                        startIndex = row
                    if currentIndex != depth and previousIndex == depth and endIndex == -1:
                        endIndex = row - 1
                    previousIndex = int(reader[row][0])

                if depth == 13:
                    endIndex = len(reader) -1

                #save all values which are above threshold effort
                thresholdPosition = float(reader[startIndex][2])
                allDepths.append(float(reader[startIndex][1]))
                for row in range(endIndex, startIndex -1, -1):
                    if abs(float(reader[row][3])) > effortThreshold:
                        effortsOverThreshold[depth].append(abs(float(reader[row][3])))
                        dX[depth].append( thresholdPosition - float(reader[row][2]) )
                        jointDepths[depth].append(float(reader[row][1]))

                    else:
                        break

                #reverse back to normal order
                effortsOverThreshold[depth][::-1]
                dX[depth][::-1]
                jointDepths[depth][::-1]

                #plotting of effort and displacement
                slope, offset = numpy.polyfit(effortsOverThreshold[depth], dX[depth], 1)
                allSlopes.append(slope)
                allOffsets.append(offset)
                plt.plot(effortsOverThreshold[depth], dX[depth], '-')
            plt.show()


            #plot slopes and depths
            plt.plot(allSlopes, allDepths, '.')
            plt.show()

            allDepths2 = list(numpy.power(allDepths, .25))
            plt.plot(allSlopes, allDepths2, '.')
            plt.show()


        #3D graphing

        totalEffort = []
        totalDX = []
        totalDepth = []

        for depth in range(len(effortsOverThreshold)):
            for value in range(len(effortsOverThreshold[depth])):
                totalEffort.append(effortsOverThreshold[depth][value])
                totalDX.append(dX[depth][value])
                totalDepth.append(jointDepths[depth][value])


        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        #totalEffort, totalDX = numpy.meshgrid(totalEffort, totalDX)
        #surf = ax.plot_surface(totalEffort, totalDX, totalDepth, cmap=cm.coolwarm, linewidth=0, antialiased=False)

        ax.plot_wireframe( totalEffort, totalDX, totalDepth)
        plt.show()


run()
