#created July 19th, 2016
# To Do:
# -

import sys
import csv
from numpy import array
from cisstRobotPython import *
import math
from cisstNumericalPython import *
import numpy


dvpsm_file_location = '/home/neusman1/catkin_ws/src/cisst-saw/sawIntuitiveResearchKit/share/dvpsm-copy-for-testing.rob'
def average_distance_computation(joint_increment_number_array, sample_range, offsets_list):
    #set up robot
    r = robManipulator()
    r.LoadRobot(dvpsm_file_location)
    
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
    tooltip = array([[0.0, -1.0, 0.0, 0.0], [ 0.0,  0.0,  1.0,  0.1016 + increment_of_change_array[4] + offsets_list[4] ], [-1.0,  0.0,  0.0,  0.0], [ 0.0,  0.0,  0.0,  1.0]])

    #set up tooltip offset
    tt = robManipulator()
    tt.Rtw0 = tooltip
    r.Attach(tt)

    all_joint_data_array = []
    all_forward_kinematics_array = []
    all_cartesian_positions_array = []
    all_named_coordinates_under_testing = []

    #import real value data
    reader=csv.reader(open("Atracsys_joint_motion_output.csv","rb"),delimiter=',')
    full_data_list_actual=list(reader)
    del full_data_list_actual[0]
    for item in full_data_list_actual:
        del item[3:]
    all_coordinates_actual=numpy.array(full_data_list_actual).astype(float)

    #import test value data
    with open('Atracsys_joint_motion_output.csv', 'rb') as f_test:
        reader = csv.reader(f_test)
        for row in reader:
            all_joint_data_array.append(row)
    del all_joint_data_array[0]
    for item in all_joint_data_array:
        del item[:-7]

    #change data from str to float
    for arrayElement in all_joint_data_array:
        for jointElement in range(len(arrayElement)):
            arrayElement[jointElement] = float(arrayElement[jointElement])

    #calculate forward kinematics for each joint set
    for arrayElement in all_joint_data_array:
        FK = r.ForwardKinematics(numpy.array(arrayElement))
        all_forward_kinematics_array.append(FK)

    #create list of only cartesian positions
    for arrayElement in all_forward_kinematics_array:
        xyz = []
        for axis in range(3):
            xyz.append(arrayElement[axis][3])
        all_cartesian_positions_array.append(xyz)
    nb_of_positions = len(all_cartesian_positions_array)
    #create numpy array for use in nmrRegistrationRigid
    coordinates_being_tested = numpy.zeros(shape=(nb_of_positions,3))
    
    for coordinate in range(len(all_cartesian_positions_array)):
         coordinates_being_tested[coordinate] = [all_cartesian_positions_array[coordinate][0], all_cartesian_positions_array[coordinate][1], all_cartesian_positions_array[coordinate][2]]
    all_coordinates_under_testing = coordinates_being_tested.astype(float)

    #calculate fre
    fre = nmrRegistrationRigid(all_coordinates_actual, all_coordinates_under_testing)[1]

    #return fre and used offsets
    return_array = [fre, 
                    round(increment_of_change_array[0] + offsets_list[0], 5), 
                    round(increment_of_change_array[1] + offsets_list[1], 5), 
                    round(increment_of_change_array[2] + offsets_list[2], 5), 
                    round(increment_of_change_array[3] + offsets_list[3], 5), 
                    round(increment_of_change_array[4] + offsets_list[4], 5)]
    return return_array


def optimal_offsets(offsets_list, sample_range):
    offset_ideals = []
    ideal_error = 100000 #set to unobtainably-large number so that a new ideal will always be accepted
    #set the percent dependent on the scale size
    global progress
    if sample_range == (1.0/10.0)**1:
        progress = 0.0
    elif  sample_range == (1.0/10.0)**2:
        progress = float((11**5))
    elif  sample_range == (1.0/10.0)**3:
        progress = float((2.0 * (11**5)))
    elif  sample_range == (1.0/10.0)**4:
        progress = float((3.0 * (11**5)))
    
    #check 11 possible DH offset changes(+-5) for each joint in given sample range
    for joint2 in range(-5,6):
        for joint3 in range(-5,6):
            sys.stdout.write('\rProgress %02.3f%%' %( progress / (11**5) *25))
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
                        #if two ideals are found with the same fre, use the one with less overall offset change
                        elif output[0] == ideal_error:
                            old_change = 0
                            new_change = 0
                            for joint in range(1,6):
                                old_change = old_change + abs(offset_ideals[joint])
                                new_change = new_change + abs(output[joint])
                            if old_change < new_change:
                                ideal_error = output[0]
                                offset_ideals = [output[1],output[2],output[3],output[4],output[5]]

    #display final percent
    if sample_range == (1.0/10.0)**1:
        sys.stdout.write('\rProgress %03.3f%%' %(25.0))
    elif  sample_range == (1.0/10.0)**2:
        sys.stdout.write('\rProgress %03.3f%%' %(50.0))
    elif  sample_range == (1.0/10.0)**3:
        sys.stdout.write('\rProgress %03.3f%%' %(75.0))
    elif  sample_range == (1.0/10.0)**4:
        sys.stdout.write('\rProgress %03.3f%%' %(100.0))

    return [offset_ideals, ideal_error]
    


def run():

    #write values to csv
    csv_file_name = 'atracsys-dvrk_DH_calibration_output.csv'
    print "Values will be saved in: ", csv_file_name
    f = open(csv_file_name, 'wb')
    writer = csv.writer(f)

    #begin testing (each itteration of loop is another degree of precision)
    optimal_offset_list = [0.0,0.0,0.0,0.0,0.0]
    for sample_range_size in range(4):
        sample_range = (1.0/10.0)**(sample_range_size +1)
        offset_output = optimal_offsets(optimal_offset_list,sample_range)
        optimal_offset_list = offset_output[0]
        ideal_error = offset_output[1]
        print " \n scale size ", (1.0/10.0)**(sample_range_size +1), "done testing"
    print "\n"
    print "ideal error: ", ideal_error
    print "optimal offsets: ", optimal_offset_list
    print "dvpsm file location: ", dvpsm_file_location
                                
    #record results
    writer.writerow(["ideal error"])
    writer.writerow([ideal_error, " "])
    writer.writerow(["optimal offsets"])
    writer.writerow(optimal_offset_list)

run()
