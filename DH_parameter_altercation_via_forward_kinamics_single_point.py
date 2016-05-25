#created April 5th, 2016
# To Do:
# -fix issue with non-zero returns after second itteration

import sys
import csv
from numpy import array
from cisstRobotPython import *
import math

def average_distance_computation(joint_increment_number_array, sample_range, offsets_list):
    #set up robot
    r = robManipulator()
    r.LoadRobot('/home/neusman1/catkin_ws/src/cisst-saw/sawIntuitiveResearchKit/share/dvpsm-copy-for-testing.rob')
    
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
    increment_of_change_array = [round(float(x) * (sample_range), 5) for x in joint_increment_number_array] 

    #modify offsets
    k2.SetPositionOffset( k2offset + increment_of_change_array[0] + offsets_list[0])
    k3.SetPositionOffset( k3offset + increment_of_change_array[1] + offsets_list[1])
    k4.SetPositionOffset( k4offset + increment_of_change_array[2] + offsets_list[2])
    k5.SetPositionOffset( k5offset + increment_of_change_array[3] + offsets_list[3])
    tooltip = array([[0.0, -1.0, 0.0, 0.0], [ 0.0,  0.0,  1.0,  0.0100 + increment_of_change_array[4] + offsets_list[4] ], [-1.0,  0.0,  0.0,  0.0], [ 0.0,  0.0,  0.0,  1.0]])

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
    
    #return distance and used offsets
    return_array = [average_distance, 
                    round(increment_of_change_array[0] + offsets_list[0], 5), 
                    round(increment_of_change_array[1] + offsets_list[1], 5), 
                    round(increment_of_change_array[2] + offsets_list[2], 5), 
                    round(increment_of_change_array[3] + offsets_list[3], 5), 
                    round(increment_of_change_array[4] + offsets_list[4], 5)]
    return return_array


def optimal_offsets(offsets_list, sample_range):
    offset_ideals = []
    ideal_error = 100000
    progress = 0.0
    
    
    #check 10 possible joint positions for each joint in given sample range
    for joint2 in range(-5,6):
        for joint3 in range(-5,6):
            sys.stdout.write('\rProgress %02.3f%%' %( progress / (11**5) *100))
            sys.stdout.flush()
            for joint4 in range(-5,6):
                for joint5 in range(-5,6):
                    for joint6 in range(-5,6):
                        progress = progress + 1
                        input_array = [joint2,joint3,joint4,joint5,joint6]
                        output = average_distance_computation(input_array, sample_range, offsets_list)

                        #check if gathered value is better then previous, if so set as new ideal
                        if output[0] < ideal_error:
                            ideal_error = output[0]
                            offset_ideals = [output[1],output[2],output[3],output[4],output[5]]

    sys.stdout.write('\rProgress %03.3f%%' %(100))

    return [offset_ideals, ideal_error]
    


    """
    for joint3 in range(-5,6):
        for joint4 in range(-5,6):
            sys.stdout.write('\rProgress %02.3f%%' %( progress / (11**2) *100))
            sys.stdout.flush()
            progress = progress + 1
            input_array = [0.0,joint3,joint4,0.0,0.0]
            #input_array = [joint2,joint3,0.0,0.0,0.0]
            #input_array = [0.0,0.0,0.0,joint5,joint6]
            output = average_distance_computation(input_array, sample_range, offsets_list)
            #write colected values to csv
            #writer.writerow( output )
            #check if gathered value is better then perivous, if so set as new ideal

            #print output
            if output[0] < ideal_error:
                ideal_error = output[0]
                offset_ideals = [output[1],output[2],output[3],output[4],output[5]]
                     
                
                if ideal_error < 0.00312023255857:
                    #print "\n \n \n \n \n New Ideal Acheived! \n"
                    print "offset ideals: ", offset_ideals
                    #print "ideal error: ", ideal_error
                
  
    return [offset_ideals, ideal_error]

    """

def run():

    #write values to csv
    csv_file_name = 'DH_testing_output.csv'
    print "Values will be saved in: ", csv_file_name
    f = open(csv_file_name, 'wb')
    writer = csv.writer(f)

    #begin testing (each itteration of loop is another degree of precision)
    optimal_offset_list = [0.0,0.0,0.0,0.0,0.0]
    for sample_range_size in range(4):
        sample_range = (1.0/10.0)**(sample_range_size +1)
        #print "\n sample range: ",sample_range
        #print "optimal offset list: ", optimal_offset_list
        offset_output = optimal_offsets(optimal_offset_list,sample_range)
        #print "offset output: ", offset_output
        optimal_offset_list = offset_output[0]
        ideal_error = offset_output[1]
        print " \n scale size ", (1.0/10.0)**(sample_range_size +1), "done testing"
    print "\n"
    print "ideal error: ", ideal_error
    print "optimal offsets: ", optimal_offset_list
                                
    #record results
    writer.writerow(["ideal error"])
    writer.writerow([ideal_error, " "])
    writer.writerow(["optimal offsets"])
    writer.writerow(optimal_offset_list)

run()
