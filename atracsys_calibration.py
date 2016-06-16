#!/usr/bin/env python

#Created on July 15, 2016



import time
import rospy
import threading
import math
import sys
import csv
import datetime
import numpy
import PyKDL
from tf_conversions import posemath
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Joy, PointCloud
from std_msgs.msg import String, Bool
from sensor_msgs.msg import JointState
from cisstNumericalPython import *

class atracsys_calibration:

    def __init__(self, robot_name):
        self._robot_name = robot_name
        self._serial_number = ""
        self._data_received = False # use pots to make sure the ROS topics are OK
        self._last_potentiometers = []
        self._last_joints = []
        self._robot_state = 'uninitialized'
        self._robot_state_event = threading.Event()
        self._goal_reached = False
        self._goal_reached_event = threading.Event()
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

    def _position_cartesian_current_cb(self, data):
        self._position_cartesian_current = posemath.fromMsg(data.pose)



    """
    def dmove(self, delta_input, interpolate = True):
        return self.__dmove_translation(delta_input, interpolate)
       

    def __dmove_translation(self, delta_translation, interpolate = True):
        # convert into a Frame
        delta_rotation = PyKDL.Rotation.Identity()
        delta_frame = PyKDL.Frame(delta_rotation, delta_translation)
        return self.__dmove_frame(delta_frame, interpolate)


    def __dmove_frame(self, delta_frame, interpolate = True):
        # add the incremental move to the current position, to get the ending frame
        end_frame = delta_frame * self.__position_cartesian_desired
        return self.__move_frame(end_frame, interpolate)
    
    """




    def pot_callback(self, data):
        self._last_potentiometers[:] = data.position
        self._data_received = True

    def joints_callback(self, data):
        self._last_joints[:] = data.position

    def robot_state_callback(self, data):
        self._robot_state = data.data
        self._robot_state_event.set()

    def goal_reached_callback(self, data):
        self._goal_reached = data.data
        self._goal_reached_event.set()

    def set_position_goal_joint(self, goal):
        self._goal_reached_event.clear()
        self._goal_reached = False
        joint_state = JointState()
        joint_state.position[:] = goal
        self._set_position_goal_joint_publisher.publish(joint_state)
        self._goal_reached_event.wait(180) # 3 minutes at most
        if not self._goal_reached:
            rospy.signal_shutdown('failed to reach goal')
            sys.exit(-1)

    def set_state_block(self, state, timeout = 60):
        self._robot_state_event.clear()
        self.set_robot_state.publish(state)
        self._robot_state_event.wait(timeout)
        if (self._robot_state != state):
            rospy.logfatal(rospy.get_caller_id() + ' -> failed to reach state ' + state)
            rospy.signal_shutdown('failed to reach desired state')
            sys.exit(-1)

    def run(self):
        ros_namespace = '/dvrk/' + self._robot_name
        self.set_robot_state = rospy.Publisher(ros_namespace + '/set_robot_state',
                                               String, latch = True, queue_size = 1)
        self._set_position_goal_joint_publisher = rospy.Publisher(ros_namespace
                                                                  + '/set_position_goal_joint',
                                                                  JointState, latch = True, queue_size = 1)
        self._set_robot_state_publisher = rospy.Publisher(ros_namespace
                                                          + '/set_robot_state',
                                                          String, latch = True, queue_size = 1)
        rospy.Subscriber(ros_namespace + '/position_cartesian_current',
                         PoseStamped, self._position_cartesian_current_cb)
        rospy.Subscriber(ros_namespace + '/robot_state', String, self.robot_state_callback)
        rospy.Subscriber(ros_namespace + '/goal_reached', Bool, self.goal_reached_callback)
        rospy.Subscriber(ros_namespace +  '/io/analog_input_pos_si', JointState, self.pot_callback)
        rospy.Subscriber(ros_namespace +  '/io/joint_position', JointState, self.joints_callback)
        rospy.Subscriber('/spacenav/joy', Joy, self.joy_callback)
        rospy.Subscriber('/atracsys/fiducials', PointCloud, self.points_callback)

        # create node
        rospy.init_node('dvrk_calibrate_atracsys', anonymous = True)

        #vaibale setup
        fast_mode = False
        recorded_dvrk_positions = []
        recorded_atracsys_positions = []

        while not rospy.is_shutdown():
            #display mouse,atracsys, and dvrk positions
            print 'Mouse axes: '
            for i in range(len(self._last_axes)):
                print self._last_axes[i]
            print '\n'
            print 'Atracsys fiducials: '
            for i in range(len(self._points)):
                print self._points[i]
            print '\n'
            print 'dvrk tooltip position: '
            for i in range(3):
                print self._position_cartesian_current.p[i]
            print '\n'
            time.sleep(.1)
        
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
            self.dmove(PyKDL.Vector(y, -x, z), False)

            #record data
            if self.mouse_buttons()[0] == 1 and self.previous_mouse_buttons[0] == 0:
                time.sleep(.1)
                recorded_dvrk_positions.append( self._position_cartesian_current.p)
                recorded_atracsys_positions.append( self._points )
                
            
            #enable quicker speed if pressing 2nd mouse button
            if self.mouse_buttons()[1] == 1 and self.previous_mouse_buttons[1] == 0:
                fast_mode = not fast_mode
            """

            #record previous mouse button values
            self.previous_mouse_buttons[:] = self._last_buttons




if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print sys.argv[0] + ' requires one argument: name of dVRK arm'
    else:
        calibration = atracsys_calibration(sys.argv[1])
        calibration.run()

