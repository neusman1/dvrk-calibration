#created April 5th, 2016

import sys
import csv
from numpy import array
from cisstRobotPython import *
import math

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
    all_cartesian_positions_array = []
    cartesian_axis_total_groupings = [ [],[],[] ]
    all_distances_to_average = []

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
    
    #create list of only cartesian positions
    for arrayElement in all_forward_kinematics_array:
        xyz = []
        for axis in range(3):
            xyz.append(arrayElement[axis][3])
        all_cartesian_positions_array.append(xyz)

    #calculate averavge position
    for axis in range(3):
        for arrayElement in all_cartesian_positions_array:
            cartesian_axis_total_groupings[axis].append(arrayElement[axis])
    average_cartesian_position = [ (math.fsum(cartesian_axis_total_groupings[0])/len(cartesian_axis_total_groupings[0])), (math.fsum(cartesian_axis_total_groupings[1])/len(cartesian_axis_total_groupings[1])), (math.fsum(cartesian_axis_total_groupings[2])/len(cartesian_axis_total_groupings[2])) ]
    print average_cartesian_position

    #calculate average distace of each joint frame to average cartesian point
    for arrayElement in all_cartesian_positions_array:
        distance = math.sqrt( ((arrayElement[0] - average_cartesian_position[0])**2) + ((arrayElement[1] - average_cartesian_position[1])**2) + ((arrayElement[2] - average_cartesian_position[2])**2) )
        all_distances_to_average.append(distance)
    average_distance = math.fsum(all_distances_to_average)/len(all_distances_to_average)
        

    #for testing purposes only
    print average_distance
    #print cartesian_axis_total_groupings
    #print all_forward_kinematics_array
    #print all_forward_kinematics_array[0]
    #print all_cartesian_positions_array
    #print all_joint_data_array[0]
    #print type(all_joint_data_array[0][0])
    #print r.ForwardKinematics(array(all_joint_data_array[0]))




run('PSM2')
