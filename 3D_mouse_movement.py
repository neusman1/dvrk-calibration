#created on January 5th 2016

#to do:
# 27 positions
# 3 for shaft, 3 for wrist, 3 fingers
# after button pressed, move close to average cartesian position of previous trials

import sys
from dvrk.arm import * 
from sensor_msgs.msg import Joy
import rospy
import time
import random
import csv

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
        recorded_joint_positions = []
        recorded_cartesian_positions = []
        sample_nb = 0
        acceleration_counter = 1.0
        range_of_motion = [ [-4.53786, 4.53786], [-1.39626, 1.39626], [-1.39626, 1.39626]]
        density = 3
        joint_motions = [ 0, 0, 0]
        joint_indexs = [ 0, 0, 0]
        
        while sample_nb < (density ** 3):
            if self._last_axes[0] != 0 or self._last_axes[1] != 0 or self._last_axes[2] != 0:
                acceleration_counter += 0.03
            else:
                acceleration_counter = 1.0
            scale = acceleration_counter / 5000.0
            x = self._last_axes[0] * scale
            y = self._last_axes[1] * scale
            z = self._last_axes[2] * scale
            self._robot.delta_move_cartesian_translation([y, -x, z], False)
            if self.mouse_buttons()[0] == 1 and self.previous_mouse_buttons[0] == 0:
                #record data
                recorded_cartesian_positions.append([self._robot.get_current_cartesian_position().p[0],self._robot.get_current_cartesian_position().p[1],self._robot.get_current_cartesian_position().p[2]])
                recorded_joint_positions.append([self._robot.get_current_joint_position()[0],self._robot.get_current_joint_position()[1],self._robot.get_current_joint_position()[2],self._robot.get_current_joint_position()[3],self._robot.get_current_joint_position()[4],self._robot.get_current_joint_position()[5],self._robot.get_current_joint_position()[6]])
                print recorded_cartesian_positions[sample_nb]
                #calculate next joint position
                shaft_remainder = sample_nb % (density ** 2)
                shaft_index = (sample_nb - shaft_remainder) / (density ** 2)
                finger_index = shaft_remainder % density
                wrist_index = (shaft_remainder - finger_index) / density
                joint_indexs = [shaft_index, wrist_index, finger_index]
                for joint in range(3):
                    joint_motions[joint] = range_of_motion[joint][0] + (joint_indexs[joint]*((range_of_motion[joint][1] - range_of_motion[joint][0])/(density -1)))
                #move to next joint position
                self._robot.delta_move_cartesian_translation([0.0,0.0,0.05])
                self._robot.move_joint_list([joint_motions[0], joint_motions[1], joint_motions[2], 0.0],[3,4,5,6])
                #move close to next cartesian position
                cartesian_totals = []
                average_cartesian_positions = []
                for axis in range(3):
                    for cartesian_sample in range(len(recorded_cartesian_positions)):
                        cartesian_totals.append(recorded_cartesian_positions[cartesian_sample][axis])
                    average_cartesian_positions.append(sum(cartesian_totals)/len(cartesian_totals))
                    cartesian_totals = []
                self._robot.move_cartesian_translation([average_cartesian_positions[0], average_cartesian_positions[1], average_cartesian_positions[2]+ 0.02])
                sample_nb += 1
                print "you are on sample: ", sample_nb, " / ", density**3
            
            """
            if self.mouse_buttons()[1] == 1 and self.previous_mouse_buttons[1] == 0:
                self.open_jaw()
            if self.mouse_buttons()[1] == 0 and self.previous_mouse_buttons[1] == 1:
                self.close_jaw()
            """
            self.previous_mouse_buttons[:] = self.mouse_buttons()
            time.sleep(0.03) # 0.03 is 30 ms, which is the spacenav's highest output frequency

        # write all values to csv file
        csv_file_name = 'mouse_positions.csv'
        print "Values will be saved in: ", csv_file_name
        f = open(csv_file_name, 'wb')
        writer = csv.writer(f)
        writer.writerow(["cartesian positions"," "," ","joint positions"])
        for i in range(10):
            writer.writerow(cartesian_positions[i] + joint_positions[i])


            

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

