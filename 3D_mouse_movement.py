#created on January 5th 2016

#to do:
#
#

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
        joint_positions = []
        cartesian_positions = []
        sample_nb = 0
        acceleration_counter = 1.0

        self._robot.move_joint_list([0.0,0.0,0.1],[0,1,2])
        random.seed()
        joint_orientation1 = random.uniform(-4.53786, 4.53786)
        joint_orientation2 = random.uniform(-1.39626, 1.39626)
        joint_orientation3 = random.uniform(-1.39626, 1.39626)
        self._robot.move_joint_list([joint_orientation1,joint_orientation2,joint_orientation3,0.0],[3,4,5,6])

        """
        self._robot.move_joint_list([0.0,0.0,0.0,0.0],[3,4,5,6])
        range_of_motion = [ [-4.53786, 4.53786], [-1.39626, 1.39626], [-1.39626, 1.39626]]
        move_amounts = []
        joint_orientations = []
        for i in range(3):
            move_amounts.append(( range_of_motion[i][(1)] - range_of_motion[i][0] ) / sample_nb)
        for i in range(3):
            joint_orintations.append(range_of_motion[i][0] + ( move_amounts[i] * sample_nb )
        self._robot.move_joint_list([joint_orientations[0],joint_orientations[1],joint_orientation[2],0.0],[3,4,5,6])
        
        """

        while sample_nb < 10:
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
                joint_orientation1 = random.uniform(-4.53786, 4.53786)
                joint_orientation2 = random.uniform(-1.39626, 1.39626)
                joint_orientation3 = random.uniform(-1.39626, 1.39626)
                self._robot.delta_move_cartesian_translation([0.0,0.0,0.01])
                self._robot.move_joint_list([joint_orientation1,joint_orientation2,joint_orientation3],[3,4,5])
                cartesian_positions.append([self._robot.get_current_cartesian_position().p[0],self._robot.get_current_cartesian_position().p[1],self._robot.get_current_cartesian_position().p[2]])
                joint_positions.append([self._robot.get_current_joint_position()[0],self._robot.get_current_joint_position()[1],self._robot.get_current_joint_position()[2],self._robot.get_current_joint_position()[3],self._robot.get_current_joint_position()[4],self._robot.get_current_joint_position()[5],self._robot.get_current_joint_position()[6]])
                #print'C:  ', cartesian_positions
                #print'J:  ', joint_positions
                print cartesian_positions[sample_nb]
                sample_nb += 1
            
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

