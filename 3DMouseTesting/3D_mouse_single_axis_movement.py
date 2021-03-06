#created on March 2nd 2016

#to do:
#

import sys
from dvrk.arm import * 
from sensor_msgs.msg import Joy
import rospy
import time
import random
import csv
import math

class calibration_testing:

    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._last_axes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._last_buttons = [0, 0]
        self.previous_mouse_buttons = [0, 0]
        rospy.Subscriber('/spacenav/joy', Joy, self.joy_callback)
        

    def joy_callback(self, data):
        self._last_axes[:] = data.axes
        self._last_buttons[:] = data.buttons

    def mouse_positions(self):
        return self._last_axes
        
    def mouse_buttons(self):
        return self._last_buttons
    
    def run(self):
        d2r = math.pi / 180
        recorded_joint_positions = []
        recorded_cartesian_positions = []
        sample_nb = 0
        acceleration_counter = 1.0
        range_of_motion = [ [-60 * d2r, 60 * d2r], [-60 * d2r, 60 * d2r], [-60 * d2r, 60 * d2r]]
        density = 10
        joint_motions = [ 0, 0, 0]
        joint_indexs = [ 0, 0, 0]

        self._robot.move_joint_list([0.0,0.0,0.1,0.0,0.0,0.0,0.0],[0,1,2,3,4,5,6])
        time.sleep(1)
        axis_under_testing = raw_input("please type 's' for shaft, 'w' for wrist, or 'f' for finger \n")
        print "Please set a refence point"

        while sample_nb < (density + 1):
            if self._last_axes[0] != 0 or self._last_axes[1] != 0 or self._last_axes[2] != 0:
                acceleration_counter += 0.03
            else:
                acceleration_counter = 1.0
            scale = acceleration_counter / 5000.0
            x = self._last_axes[0] * scale
            y = self._last_axes[1] * scale
            z = self._last_axes[2] * scale
            #move psm based on mouse position
            self._robot.delta_move_cartesian_translation([y, -x, z], False)
            if self.mouse_buttons()[0] == 1 and self.previous_mouse_buttons[0] == 0:
                #record data
                recorded_cartesian_positions.append(list(self._robot.get_current_cartesian_position().p)[:])
                recorded_joint_positions.append(list(self._robot.get_current_joint_position())[:])
                print recorded_cartesian_positions[sample_nb]
                time.sleep(.2)
                if sample_nb < density:
                    #calculate next joint position
                    if axis_under_testing == "s":
                        joint_motions[0] = range_of_motion[0][0] + (sample_nb*((range_of_motion[0][1] - range_of_motion[0][0])/(density -1)))
                        #move to next joint position
                        self._robot.delta_move_cartesian_translation([0.0,0.0,0.05])
                        time.sleep(.2)
                        self._robot.move_joint_list([joint_motions[0], 0.0, 0.0, 0.0],[3,4,5,6])
                    time.sleep(.2)
                    #calculate next joint position
                    if axis_under_testing == "w":
                        joint_motions[1] = range_of_motion[1][0] + (sample_nb*((range_of_motion[1][1] - range_of_motion[1][0])/(density -1)))
                        #move to next joint position
                        self._robot.delta_move_cartesian_translation([0.0,0.0,0.05])
                        time.sleep(.2)
                        self._robot.move_joint_list([0.0, joint_motions[1], 0.0, 0.0],[3,4,5,6])
                    #calculate next joint position
                    if axis_under_testing == "f":
                        joint_motions[2] = range_of_motion[2][0] + (sample_nb*((range_of_motion[2][1] - range_of_motion[2][0])/(density -1)))
                        #move to next joint position
                        self._robot.delta_move_cartesian_translation([0.0,0.0,0.05])
                        time.sleep(.2)
                        self._robot.move_joint_list([0.0, 0.0, joint_motions[2], 0.0],[3,4,5,6])

                   
                    #move close to next cartesian position
                    cartesian_totals = []
                    average_cartesian_positions = []
                    for axis in range(3):
                        for cartesian_sample in range(len(recorded_cartesian_positions)):
                            cartesian_totals.append(recorded_cartesian_positions[cartesian_sample][axis])
                        average_cartesian_positions.append(sum(cartesian_totals)/len(cartesian_totals))
                        cartesian_totals = []
                    self._robot.move_cartesian_translation([average_cartesian_positions[0], average_cartesian_positions[1], average_cartesian_positions[2] + 0.0025])              
                    time.sleep(.2)
                sample_nb += 1
                if sample_nb < (density +1):
                    print "you are on sample: ", sample_nb, " / ", density
                elif sample_nb == (density +1):
                    print "finished"
                    self._robot.delta_move_cartesian_translation([0.0,0.0,0.05])

            self.previous_mouse_buttons[:] = self.mouse_buttons()
            time.sleep(0.03) # 0.03 is 30 ms, which is the spacenav's highest output frequency

        # write all values to csv file
        csv_file_name = 'single_axis_mouse_positions_' + str(axis_under_testing) + '.csv'
        print "Values will be saved in: ", csv_file_name
        f = open(csv_file_name, 'wb')
        writer = csv.writer(f)
        writer.writerow(["cartesian positions"," "," ","joint positions"])
        for i in range(density):
            writer.writerow(recorded_cartesian_positions[(i+1)] + recorded_joint_positions[(i+1)])


if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

