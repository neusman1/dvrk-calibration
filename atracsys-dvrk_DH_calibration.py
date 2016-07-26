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

class extended_manipulator:
    def __init__(self, robFile):
        self.r = robManipulator()
        self.r.LoadRobot(robFile)
        #set up kinematic offset vairables
        self.l2 = self.r.links[2]
        self.k2 = self.l2.GetKinematics()
        self.k2offset = self.k2.PositionOffset()
        self.l3 = self.r.links[3]
        self.k3 = self.l3.GetKinematics()
        self.k3offset = self.k3.PositionOffset()
        self.l4 = self.r.links[4]
        self.k4 = self.l4.GetKinematics()
        self.k4offset = self.k4.PositionOffset()
        self.l5 = self.r.links[5]
        self.k5 = self.l5.GetKinematics()
        self.k5offset = self.k5.PositionOffset()

        #set up tooltip offset
        self.tt = robManipulator()
        self.r.Attach(self.tt)


class data:
    def __init__(self):
        # import atracsys 3D coordinates data
        reader = csv.reader(open("Atracsys_joint_motion_output.csv","rb"), delimiter=',')
        full_data_list_actual = list(reader)
        del full_data_list_actual[0]
        for item in full_data_list_actual:
            del item[3:]
        # 3 by N matrix
        self.all_coordinates_actual = numpy.array(full_data_list_actual).astype(float)

        # import joint value data (6 by N matrix)
        self.all_joint_data_array = []

        with open('Atracsys_joint_motion_output.csv', 'rb') as f_test:
            reader = csv.reader(f_test)
            for row in reader:
                self.all_joint_data_array.append(row)
        del self.all_joint_data_array[0]
        for item in self.all_joint_data_array:
            del item[:-7]

        # change data from str to float
        for arrayElement in self.all_joint_data_array:
            for jointElement in range(len(arrayElement)):
                arrayElement[jointElement] = float(arrayElement[jointElement])


def average_distance_computation(joint_increment_number_array, sample_range, offsets_list, manip_kin, input_data):
    
    #convert increment
    increment_of_change_array = [round(float(x) * (sample_range), 5) for x in joint_increment_number_array] 

    # modify offsets
    manip_kin.k2.SetPositionOffset(manip_kin.k2offset + increment_of_change_array[0] + offsets_list[0])
    manip_kin.k3.SetPositionOffset(manip_kin.k3offset + increment_of_change_array[1] + offsets_list[1])
    manip_kin.k4.SetPositionOffset(manip_kin.k4offset + increment_of_change_array[2] + offsets_list[2])
    manip_kin.k5.SetPositionOffset(manip_kin.k5offset + increment_of_change_array[3] + offsets_list[3])

    # modify tool tip
    tooltip = array([[0.0, -1.0, 0.0, 0.0], [ 0.0,  0.0,  1.0,  0.0102 + increment_of_change_array[4] + offsets_list[4] ], [-1.0,  0.0,  0.0,  0.0], [ 0.0,  0.0,  0.0,  1.0]])
    manip_kin.tt.Rtw0 = tooltip

    all_forward_kinematics_array = []
    all_cartesian_positions_array = []

    # calculate forward kinematics for each joint set
    for arrayElement in input_data.all_joint_data_array:
        FK = numpy.zeros(shape = (4, 4))
        manip_kin.r.ForwardKinematics(numpy.array(arrayElement), FK)
        all_forward_kinematics_array.append(FK)

    # create list of only cartesian positions
    for arrayElement in all_forward_kinematics_array:
        xyz = []
        for axis in range(3):
            xyz.append(arrayElement[axis][3])
        all_cartesian_positions_array.append(xyz)
    nb_of_positions = len(all_cartesian_positions_array)
    # create numpy array for use in nmrRegistrationRigid
    coordinates_being_tested = numpy.zeros(shape=(nb_of_positions,3))
    
    for coordinate in range(len(all_cartesian_positions_array)):
         coordinates_being_tested[coordinate] = [all_cartesian_positions_array[coordinate][0], all_cartesian_positions_array[coordinate][1], all_cartesian_positions_array[coordinate][2]]
    all_coordinates_under_testing = coordinates_being_tested.astype(float)

    # calculate fre
    fre = nmrRegistrationRigid(input_data.all_coordinates_actual, all_coordinates_under_testing)[1]

    #return fre and used offsets
    return_array = [fre, 
                    round(increment_of_change_array[0] + offsets_list[0], 5), 
                    round(increment_of_change_array[1] + offsets_list[1], 5), 
                    round(increment_of_change_array[2] + offsets_list[2], 5), 
                    round(increment_of_change_array[3] + offsets_list[3], 5), 
                    round(increment_of_change_array[4] + offsets_list[4], 5)]
    return return_array


def optimal_offsets(offsets_list, sample_range, manip_kin, input_data):
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
                        input_array = [joint2, joint3, joint4, joint5, joint6]
                        output = average_distance_computation(input_array, sample_range, offsets_list, manip_kin, input_data)

                        #check if gathered value is better then previous, if so set as new ideal
                        if output[0] < ideal_error:
                            ideal_error = output[0]
                            offset_ideals = [output[1],output[2],output[3],output[4],output[5]]
                        #if two ideals are found with the same fre, use the one with less overall offset change
                        """
                        elif output[0] == ideal_error:
                            old_change = 0
                            new_change = 0
                            for joint in range(1,6):
                                old_change = old_change + abs(offset_ideals[joint])
                                new_change = new_change + abs(output[joint])
                            if old_change < new_change:
                                ideal_error = output[0]
                                offset_ideals = [output[1],output[2],output[3],output[4],output[5]]
                        """

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

    # create kinematic chain for all iterations
    manip_kin = extended_manipulator(dvpsm_file_location)
    # load reference data, i.e. tracker 3D positions and corresponding PSM joint values
    input_data = data()

    #begin testing (each itteration of loop is another degree of precision)
    optimal_offset_list = [0.0,0.0,0.0,0.0,0.0]
    for sample_range_size in range(4):
        sample_range = (1.0/10.0)**(sample_range_size +1)
        offset_output = optimal_offsets(optimal_offset_list, sample_range, manip_kin, input_data)
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
