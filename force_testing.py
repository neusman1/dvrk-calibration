#!/usr/bin/env python

#Created on July 27, 2016
#Author: Nick Eusman

#To Do:
# -logout so as to be in dialout group
# -work on collecting data (list in phone notes)
# -write simple code to get transformation


import sys
from dvrk.psm import *
import rospy
import csv
import math
import numpy
import PyKDL
import time
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import WrenchStamped
import pickle


def average_of_points(list_of_points):
    totals = [ [], [], [] ]
    average = [ ]
    for axis in range(len(list_of_points[0])):
        for nb in range(len(list_of_points)):
            totals[axis].append(list_of_points[nb][axis])
    for axis in range(len(list_of_points[0])):
        average.append(sum(totals[axis])/len(totals[axis]))
    return average

class force_testing:

    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._points = [0.0, 0.0, 0.0]
        self._force = [0.0, 0.0, 0.0]
        rospy.Subscriber('/atracsys/fiducials', PointCloud, self.points_callback)
        rospy.Subscriber('/optoforce/wrench', WrenchStamped, self.force_callback)

    def points_callback(self, data):
        self._points[:] = data.points
    
    def force_callback(self, data):
        self._force = data.wrench.force

    def run(self):
        self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
        self._robot.set_wrench_body_orientation_absolute(True)
        rotation = pickle.load(file('atracsys2dvrk_rotation'))
        translation = pickle.load(file('atracsys2dvrk_translation'))
        current_wrench_body = []
        current_atracsys_position = []
        current_joint_effort = []
        desired_joint_effort = []
        current_cartesian_position = []
        desired_cartesian_position = []
        optoforce_forces = []
        zPosition = -0.105 #Default is -0.105
        while not rospy.is_shutdown():
            atracsys_pos = numpy.array([ (self._points[0].x)/10**3, (self._points[0].y)/10**3, (self._points[0].z)/10**3 ])
            atracsys2dvrk = rotation.dot(atracsys_pos)+translation

            self._robot.move(PyKDL.Vector(0.0, 0.0, zPosition))
            time.sleep(.3)
            raw_input('when force sensor is under tooltip, hit [enter]')
            for position_nb in range(1,6):
                self._robot.move(PyKDL.Vector((0.001 * position_nb), 0.0, zPosition))
                for sample_nb in range(20):
                    current_wrench_body.append(self._robot.get_current_wrench_body()[:])
                    current_atracsys_position.append([atracsys2dvrk[0], atracsys2dvrk[1], atracsys2dvrk[2]])
                    current_joint_effort.append(self._robot.get_current_joint_effort()[:])
                    desired_joint_effort.append(self._robot.get_desired_joint_effort()[:])
                    current_cartesian_position.append([self._robot.get_current_position().p[0], self._robot.get_current_position().p[1], self._robot.get_current_position().p[2]])
                    desired_cartesian_position.append([self._robot.get_desired_position().p[0], self._robot.get_desired_position().p[1], self._robot.get_desired_position().p[2]])
                    optoforce_forces.append([self._force.x, self._force.y, self._force.z])
                print 'position recorded'
                time.sleep(.5)
            
            self._robot.move(PyKDL.Vector(0.0, 0.0, -0.105))
            #write values to csv file
            csv_file_name = 'force_testing_output_at_z-pos_of_' + str(zPosition) + '.csv'
            print "\n Values will be saved in: ", csv_file_name
            f = open(csv_file_name, 'wb')
            writer = csv.writer(f)
            writer.writerow(["current wrench body", "", "", "", "", "", "atracsys positions","","","current joint effort", "", "", "", "", "", "","desired joint effort", "", "", "", "", "", "", "current cartesian positions", "", "","desired cartesian positions", "", "", "optoforce forces", "", ""])
            for row in range(len(current_atracsys_position)):
                writer.writerow([current_wrench_body[row][0],
                                 current_wrench_body[row][1],
                                 current_wrench_body[row][2],
                                 current_wrench_body[row][3],
                                 current_wrench_body[row][4],
                                 current_wrench_body[row][5],
                                 current_atracsys_position[row][0],
                                 current_atracsys_position[row][1],
                                 current_atracsys_position[row][2],
                                 current_joint_effort[row][0],
                                 current_joint_effort[row][1],
                                 current_joint_effort[row][2],
                                 current_joint_effort[row][3],
                                 current_joint_effort[row][4],
                                 current_joint_effort[row][5],
                                 current_joint_effort[row][6],
                                 desired_joint_effort[row][0],
                                 desired_joint_effort[row][1],
                                 desired_joint_effort[row][2],
                                 desired_joint_effort[row][3],
                                 desired_joint_effort[row][4],
                                 desired_joint_effort[row][5],
                                 desired_joint_effort[row][6],
                                 current_cartesian_position[row][0],
                                 current_cartesian_position[row][1],
                                 current_cartesian_position[row][2],
                                 desired_cartesian_position[row][0],
                                 desired_cartesian_position[row][1],
                                 desired_cartesian_position[row][2],
                                 optoforce_forces[row][0],
                                 optoforce_forces[row][1],
                                 optoforce_forces[row][2] ])

            
            rospy.signal_shutdown('Finished Task')

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = force_testing(robotName)
    app.run()
