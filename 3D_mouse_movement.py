import sys
from dvrk_python.robot import * 
from sensor_msgs.msg import Joy
import rospy
import time

class calibration_testing:

    def __init__(self, robotName):
        self._robot_name = robotName
        self._robot = robot(self._robot_name)
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
        move_mode = True
        while move_mode == True:
            scale = 1.0 / 5000.0
            x = self._last_axes[0] * scale
            y = self._last_axes[1] * scale
            z = self._last_axes[2] * scale
            # print x,y,z
            self._robot.delta_move_cartesian_translation([y, -x, z], False)
            if self.mouse_buttons()[0] == 1:
                move_mode = not move_mode
        
            time.sleep(0.01) # 0.01 is 10 ms

            #print self.mouse_positions()
            #print self.mouse_buttons()

if (len(sys.argv) != 2):
    print sys.argv[0] + ' requires one argument, i.e. name of dVRK arm'
else:
    robotName = sys.argv[1]
    app = calibration_testing(robotName)
    app.run()

