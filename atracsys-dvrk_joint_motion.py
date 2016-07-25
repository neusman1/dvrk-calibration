#!/usr/bin/env python

#Created on July 1, 2016
#Author: Nick Eusman

#To Do:
# -Possibly implement DH changing algorithm
# -See if Peter has other DH algorithm working, if so try to implement (possibly change csv format to fit)
# -Figure out why Atracsys sees 3 points at certain positions


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
            raw_input("The dvrk arm is about to make LARGE MOVEMENTS, please ensure there is ample space, then hit [enter]")
            print "The robot will now move to its joint maxima and minima to ensure the atracsys has full vision"
            time.sleep(2)
            
            for joint0 in range(3):
                for joint1 in range(3):
                    self._robot.move_joint(numpy.array([-70*d2r + (70*joint0)*d2r, -40*d2r + (40*joint1)*d2r, 0.235,0.0,0.0,0.0,-0.20]))
                    
                    if len(self._points) == 0:
                        print "The Atracsys cannot see this joint position, please adjust the dvrk arm"
                        rospy.signal_shutdown('Atracsys cannot see joint position')
                    time.sleep(1)
            
            
            print "Begining test of each joint position"
            global progress
            global points_skipped
            points_skipped = 0
            progress = 0.0
            
            time.sleep(1)
            #try density number of positions per joint in all possible configurations
            for axis0 in range(density):
                for axis1 in range(density):
                    for axis2 in range(density):
                        for axis3 in range(density):
                            sys.stdout.write('\rProgress %02.3f%%' %( progress / (3**6) *100))
                            sys.stdout.flush()
                            for axis4 in range(density):
                                for axis5 in range(density):
                                    joint_indexs = [axis0, axis1, axis2, axis3, axis4, axis5]
                                    progress = progress + 1
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
                                    if len(self._points) == 1:
                                        recorded_dvrk_joint_positions.append([self._robot.get_current_joint_position()[0],self._robot.get_current_joint_position()[1],self._robot.get_current_joint_position()[2], self._robot.get_current_joint_position()[3], self._robot.get_current_joint_position()[4], self._robot.get_current_joint_position()[5], self._robot.get_current_joint_position()[6]])
                                        recorded_dvrk_cartesian_positions.append([self._robot.get_current_position().p[0], self._robot.get_current_position().p[1], self._robot.get_current_position().p[2]])
                                        recorded_atracsys_positions.append( [(self._points[0].x)/10**3, (self._points[0].y)/10**3, (self._points[0].z)/10**3 ]  )
                                    elif len(self._points) >= 2:
                                        print "\n More then one fiducial point found"
                                        points_skipped = points_skipped +1
                                        print points_skipped, " points skipped"
                                    elif len(self._points) == 0:
                                        print "\n Atracsys fiducial not found"
                                        points_skipped = points_skipped +1
                                        print points_skipped, " points skipped"

            sys.stdout.write('\rProgress %02.3f%%' %(100))
            self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
            
            """
            #write values to csv file
            csv_file_name = 'Atracsys_joint_motion_output.csv'
            print "\n Values will be saved in: ", csv_file_name
            f = open(csv_file_name, 'wb')
            writer = csv.writer(f)
            writer.writerow(["atracsys positions","","","dvrk cartesian positions", "", "", "dvrk joint positions"])
            for row in range(len(recorded_atracsys_positions)):
                writer.writerow([recorded_atracsys_positions[row][0],recorded_atracsys_positions[row][1],recorded_atracsys_positions[row][2],recorded_dvrk_cartesian_positions[row][0],recorded_dvrk_cartesian_positions[row][1],recorded_dvrk_cartesian_positions[row][2],recorded_dvrk_joint_positions[row][0],recorded_dvrk_joint_positions[row][1],recorded_dvrk_joint_positions[row][2],recorded_dvrk_joint_positions[row][3],recorded_dvrk_joint_positions[row][4],recorded_dvrk_joint_positions[row][5],recorded_dvrk_joint_positions[row][6]])
            """

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
            print 'Transformation: \n', transformation
            print 'FRE: \n', FRE

            Transformation.Rotation().dump('atracsys2dvrk_rotation')
            Transformation.Translation().dump('atracsys2dvrk_translation')
                        

            rospy.signal_shutdown('Finished Task')

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

