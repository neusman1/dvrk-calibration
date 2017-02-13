#!/usr/bin/env python

#Created on February 13, 2017
#Author: Nick Eusman

#To Do:
# -modify code to be entierly in jointspace


import sys
from dvrk.psm import *
import rospy
import csv
import math
import numpy
import PyKDL
import time
import datetime


class force_testing:

    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._points = [0.0, 0.0, 0.0]
        self._force = [0.0, 0.0, 0.0]

    def run(self):
        avg_current_joint_positions = []
        avg_current_joint_effort = []
        avg_depth = []
        
        while not rospy.is_shutdown():
            jointUnderTesting = 0;
            self._robot.move(PyKDL.Vector(0.0, 0.0, -0.09))
            time.sleep(.3)
            raw_input('when surface is in place, hit [enter]')

            for depthIndex in range(14):
                depth = -0.09 - (float(depthIndex) * 0.01)
                print depth
                self._robot.move(PyKDL.Vector(0.0, 0.0, depth))
                time.sleep(1)
                position_nb = 0
                isEffortThreshold = False
                while not isEffortThreshold: #move to 20 positions
                    position_nb += 1

                    current_joint_positions = 0.0
                    current_joint_effort = 0.0
                    joint_depth = 0.0
                    for sample_nb in range(20): #take 20 samples at each position
                        
                        current_joint_effort += self._robot.get_current_joint_effort()[0]
                        current_joint_positions += self._robot.get_current_joint_position()[0]
                        joint_depth += self._robot.get_current_joint_position()[2]
                                                        
                        time.sleep(.02) #sleep after each sample
                    avg_current_joint_positions.append( current_joint_positions / 20.0 )
                    avg_current_joint_effort.append( current_joint_effort / 20.0 )
                    avg_depth.append( joint_depth / 20.0 )
                    print 'position recorded: ', position_nb
                    time.sleep(.5) 
                    if abs(avg_current_joint_effort[position_nb - 1]) > 1.2:
                        isEffortThreshold = True
                    else:
                        self._robot.move(PyKDL.Vector((-0.001 * position_nb), 0.0, depth))
                        print depth
                        time.sleep(1)
                    
            self._robot.move(PyKDL.Vector(0.0, 0.0, -0.09))

            #write values to csv file
            csv_file_name = 'ForceTestingDataJointSpace/force_joint_space_data_collection_output_at_joint_' + jointUnderTesting + '_' + ('-'.join(str(x) for x in list(tuple(datetime.datetime.now().timetuple())[:6]))) + '.csv'
            print "\n Values will be saved in: ", csv_file_name
            f = open(csv_file_name, 'wb')
            writer = csv.writer(f)
            writer.writerow(["current Joint positions", "current joint effort", "current depth"])
            for row in range(len(avg_current_joint_positions)):         #column number for data in csv file
                writer.writerow([avg_depth[row],
                                 avg_current_joint_positions[row],
                                 avg_current_joint_effort[row] ])
                                 

            rospy.signal_shutdown('Finished Task')

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = force_testing(robotName)
    app.run()
