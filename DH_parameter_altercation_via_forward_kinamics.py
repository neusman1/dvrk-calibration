#created April 5th, 2016

import sys
import csv
from numpy import array
from cisstRobotPython import *

def run(self):
    #set up robot
    r = robManipulator()
    r.LoadRobot('/home/neusman1/catkin_ws/src/cisst-saw/sawIntuitiveResearchKit/share/dvpsm.rob')
    #set up tooltip offset
    tt = robManipulator()
    tooltip = array([[0.0, -1.0, 0.0, 0.0], [ 0.0,  0.0,  1.0,  0.0116], [-1.0,  0.0,  0.0,  0.0], [ 0.0,  0.0,  0.0,  1.0]])
    tt.Rtw0 = tooltip
    r.Attach(tt)
    
    all_joint_data_array = []
    all_forward_kinematics_array = []

    #import data
    with open('MouseData/joint_positions_for_testing.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            all_joint_data_array.append(row)
    
    #change data from str to float
    for arrayElement in all_joint_data_array:
        for jointElement in range(len(arrayElement)):
            arrayElement[jointElement] = float(arrayElement[jointElement])
    
    #calculate forward kinematics for each joint set
    for arrayElement in all_joint_data_array:
        FK = r.ForwardKinematics(array(arrayElement))
        all_forward_kinematics_array.append(FK)
    
    print all_forward_kinematics_array
    

    #for testing purposes only
    #print all_joint_data_array[0]
    #print type(all_joint_data_array[0][0])
    #print r.ForwardKinematics(array(all_joint_data_array[0]))




run('PSM2')
