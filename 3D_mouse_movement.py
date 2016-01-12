import sys
from dvrk.arm import * 
from sensor_msgs.msg import Joy
import rospy
import time
import random


class calibration_testing:

    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = arm(self._robot_name)
        self._last_axes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._last_buttons = [0, 0]
        rospy.Subscriber('/spacenav/joy', Joy, self.joy_callback)
        

    def joy_callback(self, data):
        self._last_axes[:] = data.axes
        self._last_buttons[:] = data.buttons

    def mouse_positions(self):
        return self._last_axes
        
    def mouse_buttons(self):
        return self._last_buttons
    
    def run(self):
        self._robot.move_joint_list([0.0,0.0,0.1],[0,1,2])
        random.seed()
        joint_orientation1 = random.uniform(-4.53786, 4.53786)
        joint_orientation2 = random.uniform(-1.39626, 1.39626)
        joint_orientation3 = random.uniform(-1.39626, 1.39626)
        self._robot.move_joint_list([joint_orientation1,joint_orientation2,joint_orientation3,0.0],[3,4,5,6])

        move_mode = 0
        slow_speed = False
        while move_mode < 10:
            if slow_speed == False:  
                scale = 1.0 / 500.0
            elif slow_speed == True:
                scale = 1.0 / 5000.0
            x = self._last_axes[0] * scale
            y = self._last_axes[1] * scale
            z = self._last_axes[2] * scale
            # print x,y,z
            self._robot.delta_move_cartesian_translation([y, -x, z], False)
            if self.mouse_buttons()[0] == 1:
                joint_orientation1 = random.uniform(-4.53786, 4.53786)
                joint_orientation2 = random.uniform(-1.39626, 1.39626)
                joint_orientation3 = random.uniform(-1.39626, 1.39626)
                print joint_orientation1,joint_orientation2,joint_orientation3
                self._robot.delta_move_cartesian_translation([0.0,0.0,0.025])
                self._robot.move_joint_list([joint_orientation1,joint_orientation2,joint_orientation3],[3,4,5])
                move_mode += 1
                print self._robot.get_current_cartesian_position().p
            if self.mouse_buttons()[1] == 1:
                slow_speed = not slow_speed
                time.sleep(.2)
                print "Slow speed is", slow_speed
            time.sleep(0.01) # 0.01 is 10 ms
            
            

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

