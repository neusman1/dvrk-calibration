#!/usr/bin/env python

#Created on July 15, 2016



import time
import rospy
import math
import sys
import csv
import numpy
import PyKDL
from dvrk.psm import * 
from geometry_msgs.msg import Point32
from sensor_msgs.msg import Joy, PointCloud
from cisstNumericalPython import *

class atracsys_calibration:

    def __init__(self, robot_name):
        self._robot_name = robot_name
        self._robot = arm(self._robot_name)
        self._last_axes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._last_buttons = [0, 0]
        self.previous_mouse_buttons = [0, 0]
        self._points = [0.0, 0.0, 0.0]
        self._position_cartesian_current = PyKDL.Frame()

    def points_callback(self,data):
        self._points[:] = data.points

    def joy_callback(self, data):
        self._last_axes[:] = data.axes
        self._last_buttons[:] = data.buttons
        
    def run(self):
        rospy.Subscriber('/spacenav/joy', Joy, self.joy_callback)
        rospy.Subscriber('/atracsys/fiducials', PointCloud, self.points_callback)

        #setup
        fast_mode = False
        recorded_dvrk_positions = []
        recorded_atracsys_positions = []
        self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
        number_of_points = 7
        #atracsys_position = [self._points[0].x, self._points[0].y, self._points[0].z ]
        while not rospy.is_shutdown():
            #display mouse,atracsys, and dvrk positions
            
            print 'Mouse axes: '
            for axis in range(len(self._last_axes)):
                print self._last_axes[axis]
            print '\n'
            print 'Atracsys fiducials: '


            for axis in range(len(self._points)):
                print self._points[axis]
                #print type(self._points[axis])
                #print self._points[axis].x
            

            #print type(self._points[0])
                
            print '\n'
            print 'dvrk tooltip position: '
            for axis in range(3):
                print self._robot.get_current_position().p[axis]
            print '\n'
            
            time.sleep(.03)
            """
            sys.stdout.write('Mouse axes: ')
            for i in range(len(self._last_axes)):
                sys.stdout.write(self._last_axes[i])
            sys.stdout.write( '\n')
            sys.stdout.write( 'Atracsys fiducials: ')
            for i in range(len(self._points)):
                sys.stdout.write( self._points[i])
                #sys.stdout.write( type(self._points[i]))
                #sys.stdout.write( self._points[i].x)
            #sys.stdout.write( type(self._points[0])
            sys.stdout.write( '\n')
            sys.stdout.write( 'dvrk tooltip position: ')
            for i in range(3):
                sys.stdout.write( self._robot.get_current_joint_position()[i])
            sys.stdout.write( '\n')
            
            sys.stdout.flush()
            """





            #mouse movement
            if self._last_axes[0] != 0 or self._last_axes[1] != 0 or self._last_axes[2] != 0:
                acceleration_counter += 0.03
            else:
                acceleration_counter = 1.0
            if fast_mode == True:
                scale = acceleration_counter / 1000.0
            elif fast_mode == False:
                scale = acceleration_counter / 5000.0
            x = self._last_axes[0] * scale
            y = self._last_axes[1] * scale
            z = self._last_axes[2] * scale
            #move based on mouse position
            self._robot.dmove(PyKDL.Vector(y, -x, z), False)

            #record data when pressing 1st mouse button
            if self._last_buttons[0] == 1 and self.previous_mouse_buttons[0] == 0 and not self._last_buttons[1] == 1 and self.previous_mouse_buttons[1] == 0:
                time.sleep(.3)
                recorded_dvrk_positions.append( [self._robot.get_current_position().p[0],self._robot.get_current_position().p[1],self._robot.get_current_position().p[2]] )
                recorded_atracsys_positions.append( [self._points[0].x, self._points[0].y, self._points[0].z ]  )
                print "position recorded"                
                time.sleep(.3)

            #enable quicker speed if pressing 2nd mouse button
            if self._last_buttons[1] == 1 and self.previous_mouse_buttons[1] == 0 and not self._last_buttons[0] == 1 and self.previous_mouse_buttons[0] == 0:
                fast_mode = not fast_mode
            
            #print recorded data when pressing both mouse buttons
            if self._last_buttons[1] == 1 and self.previous_mouse_buttons[1] == 0 and self._last_buttons[0] == 1 and self.previous_mouse_buttons[0] == 0:
                print recorded_atracsys_positions, recorded_dvrk_positions

            #record previous mouse button values
            self.previous_mouse_buttons[:] = self._last_buttons

            #calculate ridgid registation
            if len(recorded_dvrk_positions) == len(recorded_atracsys_positions) and len(recorded_dvrk_positions) == number_of_points:
                #dvrk points to numpy array
                dvrk_coordinates = numpy.zeros(shape=(number_of_points,3))
                for coordinate in range(len(recorded_dvrk_positions)):
                    dvrk_coordinates[coordinate] = [recorded_dvrk_positions[coordinate][0], recorded_dvrk_positions[coordinate][1], recorded_dvrk_positions[coordinate][2]]
                dvrk_coordinates_for_testing = dvrk_coordinates.astype(float)
                #atracsys points to numpy array
                atracsys_coordinates = numpy.zeros(shape=(number_of_points,3))
                for coordinate in range(len(recorded_atracsys_positions)):
                    atracsys_coordinates[coordinate] = [recorded_atracsys_positions[coordinate][0], recorded_atracsys_positions[coordinate][1], recorded_atracsys_positions[coordinate][2]]
                atracsys_coordinates_for_testing = atracsys_coordinates.astype(float)

                (transformation, FRE) = nmrRegistrationRigid(dvrk_coordinates_for_testing,atracsys_coordinates_for_testing)
                print 'dvrk positions: \n', dvrk_coordinates_for_testing
                print 'atracsys positions: \n', atracsys_coordinates_for_testing
                print 'Transformation: \n', transformation
                print 'FRE: \n', FRE
                rospy.signal_shutdown('Finished Task')

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print sys.argv[0] + ' requires one argument: name of dVRK arm'
    else:
        calibration = atracsys_calibration(sys.argv[1])
        calibration.run()

