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
        reference_position = []
        #self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
        self._robot.set_wrench_body_orientation_absolute(True)
        
        while not rospy.is_shutdown():
            raw_input("Move the robot to the appropriate position (make sure it is clamped down) then hit [enter]")
            self._robot.home()
            self.collect_data()
            
            for joint in range(3):
                jRef = 0.0
                for sample in range(len(current_joint_positions)):
                    jRef += current_joint_positions[sample][joint]
                jRef = jRef / len(current_joint_positions)
                reference_position.append(jRef)
            
            zero_position = PyKDL.Vector( self._robot.get_current_position().p[0], 
                                          self._robot.get_current_position().p[1], 
                                          self._robot.get_current_position().p[2])
            
            #linearly test x axis
            self._robot.dmove(PyKDL.Vector(-0.014, 0.0, 0.0))
            time.sleep(1)
            self.collect_data()
            for xaxis in range(3):
                self._robot.dmove(PyKDL.Vector(0.007, 0.0, 0.0))
                if(xaxis == 1):
                    self._robot.dmove(PyKDL.Vector(0.007, 0.0, 0.0))
                time.sleep(1)
                self.collect_data()
            self._robot.move(zero_position)
            print "finished linearly testing x axis"
            
            #linearly test y axis
            self._robot.dmove(PyKDL.Vector(0.0, -0.014, 0.0))
            time.sleep(1)
            self.collect_data()
            for yaxis in range(3):
                self._robot.dmove(PyKDL.Vector(0.0, 0.007, 0.0))
                if(yaxis == 1):
                    self._robot.dmove(PyKDL.Vector(0.0, 0.007, 0.0))
                time.sleep(1)
                self.collect_data()
            self._robot.move(zero_position)
            print "finished linearly testing y axis"
            
            #linearly test z axis
            self._robot.dmove(PyKDL.Vector(0.0, 0.0, -0.004,))
            time.sleep(1)
            self.collect_data()
            for zaxis in range(3):
                self._robot.dmove(PyKDL.Vector(0.0, 0.0, 0.002))
                if(zaxis == 1):
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
            writer.writerow(["reference joint positions","","",
                             "current joint positions", "", "", "", "", "", "",
                             "current joint effort", "", "", "", "", "", "",
                             "current wrench body", "", "", "", "", "",
                             "desired joint effort", "", "", "", "", "", "",
                             "current cartesian positions", "", "",
                             "desired cartesian positions", "", "",
                             "desired joint positions"])
            for row in range(len(current_wrench_body)):               #column number for data in csv file

                writer.writerow([reference_position[0],               #0
                                 reference_position[1],               #1
                                 reference_position[2],               #2
                                 
                                 current_joint_positions[row][0],     #3
                                 current_joint_positions[row][1],     #4
                                 current_joint_positions[row][2],     #5
                                 current_joint_positions[row][3],     #6
                                 current_joint_positions[row][4],     #7
                                 current_joint_positions[row][5],     #8
                                 current_joint_positions[row][6],     #9

                                 current_joint_effort[row][0],        #10
                                 current_joint_effort[row][1],        #11
                                 current_joint_effort[row][2],        #12
                                 current_joint_effort[row][3],        #13
                                 current_joint_effort[row][4],        #14
                                 current_joint_effort[row][5],        #15
                                 current_joint_effort[row][6],        #16
                                 
                                 current_wrench_body[row][0],         #17
                                 current_wrench_body[row][1],         #18
                                 current_wrench_body[row][2],         #19
                                 current_wrench_body[row][3],         #20
                                 current_wrench_body[row][4],         #21
                                 current_wrench_body[row][5],         #22
                                 
                                 desired_joint_effort[row][0],        #23
                                 desired_joint_effort[row][1],        #24
                                 desired_joint_effort[row][2],        #25
                                 desired_joint_effort[row][3],        #26
                                 desired_joint_effort[row][4],        #27
                                 desired_joint_effort[row][5],        #28
                                 desired_joint_effort[row][6],        #29
                                 
                                 current_cartesian_position[row][0],  #30
                                 current_cartesian_position[row][1],  #31
                                 current_cartesian_position[row][2],  #32
                                 
                                 desired_cartesian_position[row][0],  #33
                                 desired_cartesian_position[row][1],  #34
                                 desired_cartesian_position[row][2],  #35
                                 
                                 desired_joint_positions[row][0],     #36
                                 desired_joint_positions[row][1],     #37
                                 desired_joint_positions[row][2],     #38
                                 desired_joint_positions[row][3],     #39
                                 desired_joint_positions[row][4],     #40
                                 desired_joint_positions[row][5],     #41
                                 desired_joint_positions[row][6] ])   #42

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
