#created April 5th, 2016
#To Do:
# -save average distances with the values used
# -

import sys
import csv
from numpy import array
from cisstRobotPython import *
import math

def average_distance_computation(joint_increment_number_array):
    #set up robot
    r = robManipulator()
    r.LoadRobot('/home/neusman1/catkin_ws/src/cisst-saw/sawIntuitiveResearchKit/share/dvpsm.rob')
    
    #set up kinematic offset vairables
    l2 = r.links[2]
    k2 = l2.GetKinematics()
    k2offset = k2.PositionOffset()
    l3 = r.links[3]
    k3 = l3.GetKinematics()
    k3offset = k3.PositionOffset()
    l4 = r.links[4]
    k4 = l4.GetKinematics()
    k4offset = k4.PositionOffset()
    l5 = r.links[5]
    k5 = l5.GetKinematics()
    k5offset = k5.PositionOffset()
    
    #convert increment
    increment_of_change_array = [float(x) * (0.0001) for x in joint_increment_number_array] 

    #modify offsets
    k2.SetPositionOffset( k2offset + increment_of_change_array[0])
    k3.SetPositionOffset( k3offset + increment_of_change_array[1])
    k4.SetPositionOffset( k4offset + increment_of_change_array[2])
    k5.SetPositionOffset( k5offset + increment_of_change_array[3])
    tooltip = array([[0.0, -1.0, 0.0, 0.0], [ 0.0,  0.0,  1.0,  0.0116 + increment_of_change_array[4]], [-1.0,  0.0,  0.0,  0.0], [ 0.0,  0.0,  0.0,  1.0]])

    #set up tooltip offset
    tt = robManipulator()
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

    #calculate average distace of each joint frame to average cartesian point
    for arrayElement in all_cartesian_positions_array:
        distance = math.sqrt( ((arrayElement[0] - average_cartesian_position[0])**2) + ((arrayElement[1] - average_cartesian_position[1])**2) + ((arrayElement[2] - average_cartesian_position[2])**2) )
        all_distances_to_average.append(distance)
    average_distance = math.fsum(all_distances_to_average)/len(all_distances_to_average)
    
    #print 'dist:           ', average_distance
    #print 'default offset: ', k2offset
    #print 'input array:    ', joint_increment_number_array
    #print 'change:         ', increment_of_change_array
    #print 'new offset:     ', k2offset + increment_of_change_array[0]
    print average_distance

    return_array = [average_distance, increment_of_change_array[0], increment_of_change_array[1], increment_of_change_array[2], increment_of_change_array[3], increment_of_change_array[4]]
    return return_array


def run():
    offset_ideals = []
    ideal_error = 100000
    for joint2 in range(-1000,1000):
        for joint3 in range(-1000,1000):
            for joint4 in range(-1000,1000):
                for joint5 in range(-1000,1000):
                    for joint6 in range(-1000,1000):
                        input_array = [joint2,joint3,joint4,joint5,joint6]
                        output = average_distance_computation(input_array)
                        if output[0] < ideal_error:
                            ideal_error = output[0]
                            offset_ideals = [output[1],output[2],output[3],output[4],output[5]]
                            if ideal_error < 0.00312023255857:
                                print "\n New Ideal Acheived! \n"
                                

                        
run()
