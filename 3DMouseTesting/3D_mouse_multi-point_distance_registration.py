#created on May 17th 2016

#to do:
# fix csv format (double quotes around lines when printing)

import sys
from dvrk.psm import * 
from sensor_msgs.msg import Joy
import rospy
import time
import random
import csv
import math
import numpy
import PyKDL

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
        sample_nb = 0
        acceleration_counter = 1.0
        fast_mode = False
        self._robot.move_joint(numpy.array([0.0,0.0,0.1,0.0,0.0,0.0,-0.20]))
        time.sleep(1)

        print "please move to position (0,0)"
        while sample_nb < 20:
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
            
            if self.mouse_buttons()[1] == 1 and self.previous_mouse_buttons[1] == 0:
                fast_mode = not fast_mode

            if self.mouse_buttons()[0] == 1 and self.previous_mouse_buttons[0] == 0:
                #record data
                recorded_joint_positions.append(list(self._robot.get_current_joint_position())[:])
                time.sleep(.2)
                sample_nb = sample_nb + 1
                print "Current sample number: ", sample_nb, " / 20"
                print "please move to position (", (sample_nb %5)*50,  ",", (math.floor(sample_nb/5))*50,")"
                if sample_nb % 5 != 0:
                    self._robot.dmove(PyKDL.Vector(0.0,0.0,0.005))
                    self._robot.dmove(PyKDL.Vector(0.05,0.0,0.0))
                if sample_nb %5 == 0 and sample_nb != 20:
                    self._robot.dmove(PyKDL.Vector(0.0,0.0,0.008))
                    self._robot.dmove(PyKDL.Vector(0.0,0.05,0.0))
                    self._robot.dmove(PyKDL.Vector(-0.05,0.0,0.0))
                    self._robot.dmove(PyKDL.Vector(-0.05,0.0,0.0))
                    self._robot.dmove(PyKDL.Vector(-0.05,0.0,0.0))
                    self._robot.dmove(PyKDL.Vector(-0.05,0.0,0.0))

            self.previous_mouse_buttons[:] = self.mouse_buttons()
            time.sleep(0.03) # 0.03 is 30 ms, which is the spacenav's highest output frequency
        
        # write all values to csv file
        csv_file_name = 'distance_registration_mouse_positions.csv'
        print "Values will be saved in: ", csv_file_name
        f = open(csv_file_name, 'wb')
        writer = csv.writer(f)
        #writer.writerow(["#Collected joint positions",""])
        for coordinates in range(len(recorded_joint_positions)):
            writer.writerow(recorded_joint_positions[coordinates])
            #writer.writerow(["Corrdinate(" + str((coordinates %5)*50)  + " " + str(int(math.floor(coordinates/5))*50) + ")", + str(recorded_cartesian_positions[coordinates][0]) , str(recorded_cartesian_positions[coordinates][1]) , str(recorded_cartesian_positions[coordinates][2])])
        

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run() 

