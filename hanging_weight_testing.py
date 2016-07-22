#!/usr/bin/env python

#Created on July 22, 2016
#Author: Nick Eusman

#To Do:
# -ideally, the system wouldn't have a "before" element, but rather use the desired position in the dvrk's case, and the same point translated to the atracsys' cartesian system in the case of the atracsys. (joint current before should be a baseline number anyhow) <---Implementation?


import sys
from dvrk.psm import *
import rospy
import csv
import math
import numpy
import time
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
        recorded_atracsys_position = [ [], [] ]
        recorded_current_joint_position = [ [], [] ]
        recorded_current_joint_effort = [ [], [] ]
        recorded_dvrk_position = [ [], [] ]
        #for totaling data:
        recorded_atracsys_position_totals = [ [ [], [], [] ], [ [], [], [] ] ]
        recorded_current_joint_position_totals = [ [], [] ]
        recorded_current_joint_effort_totals = [ [], [] ]
        recorded_dvrk_position_totals = [ [ [], [], [] ], [ [], [], [] ] ]
        #for averages
        recorded_atracsys_position_averages = [ [], [] ]
        recorded_current_joint_position_averages = [ [], [] ]
        recorded_current_joint_effort_averages = [ [], [] ]
        recorded_dvrk_position_averages = [ [], [] ]


        while not rospy.is_shutdown():
            self._robot.move_joint(numpy.array([0.0,0.0,0.235,0.0,0.0,0.0,-0.20]))

            #record unweighted data
            raw_input("Hit [enter] when robot is unweighted")
            for i in range(20):
                recorded_atracsys_position[0].append( [(self._points[0].x)/10**3, (self._points[0].y)/10**3, (self._points[0].z)/10**3 ]  )
                recorded_current_joint_effort[0].append(self._robot.get_current_joint_effort()[0])
                recorded_current_joint_position[0].append(self._robot.get_current_joint_position()[0])
                recorded_dvrk_position[0].append([self._robot.get_current_position().p[0], self._robot.get_current_position().p[1], self._robot.get_current_position().p[2]])
                time.sleep(.3)

            #recored weighted data
            raw_input("Hit [enter] when robot is weighted")
            for sample_nb in range(20):
                recorded_atracsys_position[1].append( [(self._points[0].x)/10**3, (self._points[0].y)/10**3, (self._points[0].z)/10**3 ]  )
                recorded_current_joint_effort[1].append(self._robot.get_current_joint_effort()[0])
                recorded_current_joint_position[1].append(self._robot.get_current_joint_position()[0])
                recorded_dvrk_position[1].append([self._robot.get_current_position().p[0], self._robot.get_current_position().p[1], self._robot.get_current_position().p[2]])
                time.sleep(.3)

            #average out data sets
            for before_after in range(2):
                for sample_nb in range(20):
                    for axis in range(3):
                        recorded_atracsys_position_totals[before_after][axis].append(recorded_atracsys_position[before_after][sample_nb][axis])
                        recorded_dvrk_position_totals[before_after][axis].append(recorded_dvrk_position[before_after][sample_nb][axis])
                    recorded_current_joint_position_totals[before_after].append(recorded_current_joint_position[before_after][sample_nb])
                    recorded_current_joint_effort_totals[before_after].append(recorded_current_joint_effort[before_after][sample_nb])

            for before_after in range(2):
                for axis in range(3):
                    recorded_atracsys_position_averages[before_after].append(sum(recorded_atracsys_position_totals[before_after][axis])/len(recorded_atracsys_position_totals[before_after][axis]))
                    recorded_dvrk_position_averages[before_after].append(sum(recorded_dvrk_position_totals[before_after][axis])/len(recorded_dvrk_position_totals[before_after][axis]))
                recorded_current_joint_position_averages[before_after].append(sum(recorded_current_joint_position_totals[before_after])/len(recorded_current_joint_position_totals[before_after]))
                recorded_current_joint_effort_averages[before_after].append(sum(recorded_current_joint_effort_totals[before_after])/len(recorded_current_joint_effort_totals[before_after]))

            print 'atracsys position averages: \n', recorded_atracsys_position_averages[0], "\n", recorded_atracsys_position_averages[1]
            print 'dvrk position averages: \n', recorded_dvrk_position_averages[0], "\n", recorded_dvrk_position_averages[1]
            print 'joint position averages: \n', recorded_current_joint_position_averages[0], "\n", recorded_current_joint_position_averages[1]
            print 'joint effort averages: \n', recorded_current_joint_effort_averages[0], "\n", recorded_current_joint_effort_averages[1]
            print "In the atracsys, a change downward is in Y+, in the dvrk at this position, a change downward is X+"
            print 'atracsys Y change: ', recorded_atracsys_position_averages[1][1] - recorded_atracsys_position_averages[0][1]
            print 'dvrk X change: ', recorded_dvrk_position_averages[1][0] - recorded_dvrk_position_averages[0][0]
            print 'difference in atracsys and dvrk change: ', (recorded_atracsys_position_averages[1][1] - recorded_atracsys_position_averages[0][1]) - (recorded_dvrk_position_averages[1][0] - recorded_dvrk_position_averages[0][0])

            rospy.signal_shutdown('Finished Task')

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()
