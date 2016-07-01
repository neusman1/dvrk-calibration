#!/usr/bin/env python

#Created on July 1, 2016
#Author: Nick Eusman

#To Do:
# -csv file writing of values
# -start other code to do nmr registartion? (or maybe use same code?)
# -run all the way through to test up/down mechanic
# -check if getting atracsys values at all points

import sys
from dvrk.psm import * 
import rospy
import time
import csv
import math
import numpy
from sensor_msgs.msg import PointCloud

class calibration_testing:
    
    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._points = [0.0, 0.0, 0.0]
        rospy.Subscriber('/atracsys/fiducials', PointCloud, self.points_callback)
    
    def points_callback(self,data):
        self._points[:] = data.points

    def run(self):
        #set-up parameters
        d2r = math.pi / 180
        recorded_dvrk_joint_positions = []
        recorded_dvrk_cartesian_positions = []
        recorded_atracsys_positions = []
        range_of_motion = [ [-70 * d2r, 70 * d2r], [-40 * d2r, 40 * d2r], [0.055, 0.235], [-150 * d2r, 150 * d2r], [-60 * d2r, 60 * d2r], [-60 * d2r, 60 * d2r]]
        density = 3
        joint_motions = [0.0,0.0,0.0,0.0,0.0,0.0]
        up_or_down = [True, True, True, True, True, True]

        #stay running untill shutdown
        while not rospy.is_shutdown():
            self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
            time.sleep(1)
            #try density number of positions per joint in all possible configurations
            for axis0 in range(density):
                for axis1 in range(density):
                    for axis2 in range(density):
                        for axis3 in range(density):
                            for axis4 in range(density):
                                for axis5 in range(density):
                                    joint_indexs = [axis0, axis1, axis2, axis3, axis4, axis5]
                                    
                                    for joint in range(6):
                                        if up_or_down[joint] == True:
                                            joint_motions[joint] = range_of_motion[joint][0] + (joint_indexs[joint]*((range_of_motion[joint][1] - range_of_motion[joint][0])/(density -1)))
                                        elif up_or_down[joint] == False:
                                            joint_motions[joint] = range_of_motion[joint][1] - (joint_indexs[joint]*((range_of_motion[joint][1] - range_of_motion[joint][0])/(density -1)))
                                    self._robot.move_joint(numpy.array([joint_motions[0], joint_motions[1], joint_motions[2], joint_motions[3], joint_motions[4], joint_motions[5], -0.20]))


                                    for joint in range(6):
                                        if all(item == 2 for item in joint_indexs[(joint):]):
                                            up_or_down[(joint)] = not up_or_down[(joint)]

                                            
                                    time.sleep(1)
                                    recorded_dvrk_joint_positions.append(self._robot.get_current_joint_position())
                                    recorded_dvrk_cartesian_positions.append(self._robot.get_current_position().p)
                                    recorded_atracsys_positions.append( [(self._points[0].x)/10**3, (self._points[0].y)/10**3, (self._points[0].z)/10**3 ]  )
                                    print up_or_down




if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

