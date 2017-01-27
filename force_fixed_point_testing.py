#!/usr/bin/env python

#Created on January 27, 2017
#Author: Nick Eusman

import sys
from dvrk.psm import *
import rospy
import csv
import math
import numpy
import PyKDL
import time
import datetime
from geometry_msgs.msg import WrenchStamped

current_wrench_body = []
current_joint_effort = []
desired_joint_effort = []
current_cartesian_position = []
desired_cartesian_position = []
current_joint_positions = []
desired_joint_positions = []


class force_testing:
    
    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._points = [0.0, 0.0, 0.0]
        self._force = [0.0, 0.0, 0.0]

    def run(self):
        #self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
        self._robot.set_wrench_body_orientation_absolute(True)
        
        while not rospy.is_shutdown():
            raw_input("Move the robot to the appropriate position (make sure it is clamped down) then hit [enter]")
            self._robot.home()
            self.collect_data()
            zero_position = PyKDL.Vector( self._robot.get_current_position().p[0], 
                                          self._robot.get_current_position().p[1], 
                                          self._robot.get_current_position().p[2])
            
            #linearly test x axis
            self._robot.dmove(PyKDL.Vector(-0.014, 0.0, 0.0))
            time.sleep(1)
            self.collect_data()
            for xaxis in range(4):
                self._robot.dmove(PyKDL.Vector(0.007, 0.0, 0.0))
                time.sleep(1)
                self.collect_data()
            self._robot.move(zero_position)
            print "finished linearly testing x axis"
            
            #linearly test y axis
            self._robot.dmove(PyKDL.Vector(0.0, -0.014, 0.0))
            time.sleep(1)
            self.collect_data()
            for yaxis in range(4):
                self._robot.dmove(PyKDL.Vector(0.0, 0.007, 0.0))
                time.sleep(1)
                self.collect_data()
            self._robot.move(zero_position)
            print "finished linearly testing y axis"
            
            #linearly test z axis
            self._robot.dmove(PyKDL.Vector(0.0, 0.0, -0.004,))
            time.sleep(1)
            self.collect_data()
            for zaxis in range(4):
                self._robot.dmove(PyKDL.Vector(0.0, 0.0, 0.002))
                time.sleep(1)
                self.collect_data()
            self._robot.move(zero_position)
            print "finished linearly testing z axis"
            
            
            #test 3 dimentional vectors in cube shape surrounding center point
            for xaxis in [-0.007, 0.007]:
                for yaxis in [-0.007, 0.007]:
                    for zaxis in [-0.002, 0.002]:
                        self._robot.dmove(PyKDL.Vector(xaxis, yaxis, zaxis))
                        time.sleep(1)
                        self.collect_data()
                        self._robot.move(zero_position)
                        time.sleep(.3)
            print "finished testing all axis"

            #finished testing, save values to csv
            csv_file_name = 'ForceTestingDataAllAxis/force_fixed_point_output_' + ('-'.join(str(x) for x in list(tuple(datetime.datetime.now().timetuple())[:6]))) + '.csv'
            print "\n Values will be saved in: ", csv_file_name
            f = open(csv_file_name, 'wb')
            writer = csv.writer(f)
            writer.writerow(["current wrench body", "", "", "", "", "", "current joint effort", "", "", "", "", "", "","desired joint effort", "", "", "", "", "", "", "current cartesian positions", "", "","desired cartesian positions", "", "", "current joint positions", "", "", "", "", "", "", "desired joint positions"])
            for row in range(len(current_wrench_body)):         #column number for data in csv file

                writer.writerow([current_wrench_body[row][0],         #1
                                 current_wrench_body[row][1],         #2
                                 current_wrench_body[row][2],         #3
                                 current_wrench_body[row][3],         #4
                                 current_wrench_body[row][4],         #5
                                 current_wrench_body[row][5],         #6
                                 
                                 current_joint_effort[row][0],        #7
                                 current_joint_effort[row][1],        #8
                                 current_joint_effort[row][2],        #9
                                 current_joint_effort[row][3],        #10
                                 current_joint_effort[row][4],        #11
                                 current_joint_effort[row][5],        #12
                                 current_joint_effort[row][6],        #13
                                 
                                 desired_joint_effort[row][0],        #14
                                 desired_joint_effort[row][1],        #15
                                 desired_joint_effort[row][2],        #16
                                 desired_joint_effort[row][3],        #17
                                 desired_joint_effort[row][4],        #18
                                 desired_joint_effort[row][5],        #19
                                 desired_joint_effort[row][6],        #20
                                 
                                 current_cartesian_position[row][0],  #21
                                 current_cartesian_position[row][1],  #22
                                 current_cartesian_position[row][2],  #23
                                 
                                 desired_cartesian_position[row][0],  #24
                                 desired_cartesian_position[row][1],  #25
                                 desired_cartesian_position[row][2],  #26
                                 
                                 current_joint_positions[row][0],     #27
                                 current_joint_positions[row][1],     #28
                                 current_joint_positions[row][2],     #29
                                 current_joint_positions[row][3],     #30
                                 current_joint_positions[row][4],     #31
                                 current_joint_positions[row][5],     #32
                                 current_joint_positions[row][6],     #33

                                 desired_joint_positions[row][0],     #34
                                 desired_joint_positions[row][1],     #35
                                 desired_joint_positions[row][2],     #36
                                 desired_joint_positions[row][3],     #37
                                 desired_joint_positions[row][4],     #38
                                 desired_joint_positions[row][5],     #39
                                 desired_joint_positions[row][6] ])   #40

            rospy.signal_shutdown('Finished Task')





    def collect_data(self):
        global current_wrench_body
        global current_joint_effort
        global desired_joint_effort
        global current_cartesian_position
        global desired_cartesian_position
        global current_joint_positions
        for sample_nb in range(20):
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
            desired_joint_positions.append([self._robot.get_desired_joint_position()[0], 
                                            self._robot.get_desired_joint_position()[1], 
                                            self._robot.get_desired_joint_position()[2], 
                                            self._robot.get_desired_joint_position()[3], 
                                            self._robot.get_desired_joint_position()[4], 
                                            self._robot.get_desired_joint_position()[5], 
                                            self._robot.get_desired_joint_position()[6] ])
            time.sleep(.02)
        print "position recorded"
    

            

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = force_testing(robotName)
    app.run()
