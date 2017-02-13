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
        current_wrench_body = []
        current_atracsys_position = []
        current_joint_effort = []
        desired_joint_effort = []
        current_cartesian_position = []
        desired_cartesian_position = []
        optoforce_forces = []
        current_joint_positions = []
        
        while not rospy.is_shutdown():

            axis_under_testing = raw_input("Please type the axis which is to be tested ('x', 'y', or 'z') then hit [enter]\n")
            if axis_under_testing == 'x' or axis_under_testing == 'y' or axis_under_testing == 'z': 
                zPositionInput = int(raw_input("Please type the depth\n"))
                if zPositionInput == 1:
                    zPosition = -0.105
                elif zPositionInput == 2:
                    zPosition = -0.130
                elif zPositionInput == 3:
                    zPosition = -0.155
                elif zPositionInput == 4:
                    zPosition = -0.180
                elif zPositionInput == 5:
                    zPosition = -0.205
                elif zPositionInput == 6:
                    zPosition = -0.1425
                elif zPositionInput == 7:
                    zPosition = -0.1925
                else:
                    print "incorrect input"
                    rospy.signal_shutdown('Incorrect z position input')
            else:
                print "incorrect input"
                rospy.signal_shutdown('Incorrect axis input')

            self._robot.move(PyKDL.Vector(0.0, 0.0, zPosition))
            time.sleep(.3)
            raw_input('when force sensor is under tooltip, hit [enter]')
            
            for position_nb in range(1,21): #move to 20 positions
                if axis_under_testing == 'x':
                    self._robot.move(PyKDL.Vector((-0.00025 * position_nb), 0.0, zPosition))
                elif axis_under_testing == 'y':
                    self._robot.move(PyKDL.Vector(0.0, (-0.00025 * position_nb), zPosition)) 
                elif axis_under_testing == 'z':
                    self._robot.move(PyKDL.Vector(0.0, 0.0, (-0.00025 * position_nb) + zPosition)) 


                for sample_nb in range(20): #take 20 samples at each position
                    current_wrench_body.append([self._robot.get_current_wrench_body()[0], 
                                                self._robot.get_current_wrench_body()[1], 
                                                self._robot.get_current_wrench_body()[2], 
                                                self._robot.get_current_wrench_body()[3], 
                                                self._robot.get_current_wrench_body()[4], 
                                                self._robot.get_current_wrench_body()[5] ])
                    current_joint_effort.append([self._robot.get_current_joint_effort()[0], 
                                                 self._robot.get_current_joint_effort()[1], 
                                                 self._robot.get_current_joint_effort()[2], 
                                                 self._robot.get_current_joint_effort()[3], 
                                                 self._robot.get_current_joint_effort()[4], 
                                                 self._robot.get_current_joint_effort()[5], 
                                                 self._robot.get_current_joint_effort()[6] ]) 
                    desired_joint_effort.append([self._robot.get_desired_joint_effort()[0], 
                                                 self._robot.get_desired_joint_effort()[1], 
                                                 self._robot.get_desired_joint_effort()[2], 
                                                 self._robot.get_desired_joint_effort()[3], 
                                                 self._robot.get_desired_joint_effort()[4], 
                                                 self._robot.get_desired_joint_effort()[5],
                                                 self._robot.get_desired_joint_effort()[6] ])
                    current_cartesian_position.append([self._robot.get_current_position().p[0], 
                                                       self._robot.get_current_position().p[1], 
                                                       self._robot.get_current_position().p[2]])
                    desired_cartesian_position.append([self._robot.get_desired_position().p[0], 
                                                       self._robot.get_desired_position().p[1], 
                                                       self._robot.get_desired_position().p[2]])
                    current_joint_positions.append([self._robot.get_current_joint_position()[0], 
                                                    self._robot.get_current_joint_position()[1], 
                                                    self._robot.get_current_joint_position()[2], 
                                                    self._robot.get_current_joint_position()[3], 
                                                    self._robot.get_current_joint_position()[4], 
                                                    self._robot.get_current_joint_position()[5], 
                                                    self._robot.get_current_joint_position()[6] ])
                    time.sleep(.02)
                print 'position recorded ', position_nb, '/20'
                time.sleep(.5)
            self._robot.move(PyKDL.Vector(0.0, 0.0, zPosition))
            self._robot.move(PyKDL.Vector(0.0, 0.0, -0.105))

            #write values to csv file
            csv_file_name = 'ForceTestingDataJointSpace/force_joint_space_data_collection_output_' + axis_under_testing +'_axis_at_z-pos_of_' + str(zPosition) + '_' + ('-'.join(str(x) for x in list(tuple(datetime.datetime.now().timetuple())[:6]))) + '.csv'
            print "\n Values will be saved in: ", csv_file_name
            f = open(csv_file_name, 'wb')
            writer = csv.writer(f)
            writer.writerow(["current wrench body", "", "", "", "", "", "current joint effort", "", "", "", "", "", "","desired joint effort", "", "", "", "", "", "", "current cartesian positions", "", "","desired cartesian positions", "", "", "current joint positions"])
            for row in range(len(current_atracsys_position)):         #column number for data in csv file
                writer.writerow([current_wrench_body[row][0],         #1
                                 current_wrench_body[row][1],         #2
                                 current_wrench_body[row][2],         #3
                                 current_wrench_body[row][3],         #4
                                 current_wrench_body[row][4],         #5
                                 current_wrench_body[row][5],         #6
                                 
                                 current_joint_effort[row][0],        #10
                                 current_joint_effort[row][1],        #11
                                 current_joint_effort[row][2],        #12
                                 current_joint_effort[row][3],        #13
                                 current_joint_effort[row][4],        #14
                                 current_joint_effort[row][5],        #15
                                 current_joint_effort[row][6],        #16
                                 desired_joint_effort[row][0],        #17
                                 desired_joint_effort[row][1],        #18
                                 desired_joint_effort[row][2],        #19
                                 desired_joint_effort[row][3],        #20
                                 desired_joint_effort[row][4],        #21
                                 desired_joint_effort[row][5],        #22
                                 desired_joint_effort[row][6],        #23
                                 current_cartesian_position[row][0],  #24
                                 current_cartesian_position[row][1],  #25
                                 current_cartesian_position[row][2],  #26
                                 desired_cartesian_position[row][0],  #27
                                 desired_cartesian_position[row][1],  #28
                                 desired_cartesian_position[row][2],  #29
                                 
                                 current_joint_positions[row][0],     #33
                                 current_joint_positions[row][1],     #34
                                 current_joint_positions[row][2],     #35
                                 current_joint_positions[row][3],     #36
                                 current_joint_positions[row][4],     #37
                                 current_joint_positions[row][5],     #38
                                 current_joint_positions[row][6] ])   #39

            rospy.signal_shutdown('Finished Task')

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = force_testing(robotName)
    app.run()
