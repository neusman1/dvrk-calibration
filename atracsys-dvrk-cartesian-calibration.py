#!/usr/bin/env python

#Created on July 1, 2016
#Author: Nick Eusman

#To Do:
# -



import sys
from dvrk.psm import * 
import rospy
import time
import csv
import math
import numpy
from sensor_msgs.msg import PointCloud
from cisstRobotPython import *
from cisstNumericalPython import *

class calibration_testing:
    
    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._points = [0.0, 0.0, 0.0]
        rospy.Subscriber('/atracsys/fiducials', PointCloud, self.points_callback)
    
    def points_callback(self,data):
        self._points[:] = data.points

    def run(self):
        recorded_dvrk_cartesian_positions = []
        recorded_atracsys_positions = []
        while not rospy.is_shutdown():
            self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))

            for xCoorinate in range(3):
                for yCoordinate in range(3):
                    for zCoordinate in range(3):
                        #move the robot
                        self._robot.move(PyKDL.Vector((0.025 + (xCoorinate * -0.025)), (-0.025 + (yCoordinate * 0.025)), (-0.1 + (zCoordinate * -0.05))))
                        time.sleep(1)
                        #record positional data
                        if len(self._points) == 1:
                            recorded_dvrk_cartesian_positions.append([self._robot.get_current_position().p[0], self._robot.get_current_position().p[1], self._robot.get_current_position().p[2]])
                            recorded_atracsys_positions.append( [(self._points[0].x)/10**3, (self._points[0].y)/10**3, (self._points[0].z)/10**3 ]  )
                            print 'position recorded'
                        elif len(self._points) >= 2:
                            print "\n More then one fiducial point found"
                        elif len(self._points) == 0:
                            print "\n Atracsys fiducial not found"
        

            self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20])) 
            #dvrk points to numpy array
            number_of_points = len(recorded_atracsys_positions)
            dvrk_coordinates = numpy.zeros(shape=(number_of_points,3))
            for coordinate in range(len(recorded_dvrk_cartesian_positions)):
                dvrk_coordinates[coordinate] = [recorded_dvrk_cartesian_positions[coordinate][0], recorded_dvrk_cartesian_positions[coordinate][1], recorded_dvrk_cartesian_positions[coordinate][2]]
            dvrk_coordinates_for_testing = dvrk_coordinates.astype(float)
            #atracsys points to numpy array
            atracsys_coordinates = numpy.zeros(shape=(number_of_points,3))
            for coordinate in range(len(recorded_atracsys_positions)):
                atracsys_coordinates[coordinate] = [recorded_atracsys_positions[coordinate][0], recorded_atracsys_positions[coordinate][1], recorded_atracsys_positions[coordinate][2]]
            atracsys_coordinates_for_testing = atracsys_coordinates.astype(float)
            #calculate and display transformation and FRE 
            (transformation, FRE) = nmrRegistrationRigid(atracsys_coordinates_for_testing,dvrk_coordinates_for_testing)
            #print 'dvrk positions: \n', dvrk_coordinates_for_testing
            #print 'atracsys positions: \n', atracsys_coordinates_for_testing
            print '\n Transformation: \n', transformation
            print 'FRE: \n', FRE
            
            #save transformaton
            transformation.Rotation().dump('atracsys2dvrk_rotation')
            transformation.Translation().dump('atracsys2dvrk_translation')

            rospy.signal_shutdown('Finished Task')



if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

