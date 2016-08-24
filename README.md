# Calibration
(This readme is incomplete and undergoing edits)

## Using the DH Calibration 
### (Step One)


use dh calib to modify offsets in json file

```json
```
Make sure to restart the consol after making changes to the json file

## Creating a predictive model to evealuate tooltip deflection
### Setting up the nodes

set up nodes
(make sure the atracsys and optoForce are on) 
(ensure you are in he dialout group by using the "id" comand )

```sh
rosrun dvrk_robot dvrk_console_json -j console-PSM2.json
rosrun atracsys_ros atracsys_json
rosrun optoforce_ros optoforce_json -s /dev/ttyACM0 -j OMD-10-SE-10N.json
```
### get the transformation matrix
This will save locally a transformation matrix for the atracsys to be put in the cartesian field of the dvrk
```sh
python atracsys-dvrk-cartesian-calibration.py PSM2
```

### collect data
Run the data cllection in shell as follows
```sh
 python force_testing.py PSM2
```
Usualy the data collection is run at 5 depth (z) positions, and gathered 10 times at each. It is suggested that the transfomration matrix is retaken at least once durring data collection

to modify the z position, change the variable zPosition on line 78. Generally a term between -0.105 and -0.205 is used
```python
current_joint_positions = []
zPosition = -0.105  #Default is -0.105
while not rospy.is_shutdown():
```

### data interpretation
```sh
python predictive_linear_fit.py 
```
The above program will gather all data files in the ForceTestingData directory and create a predictive linear model. It can return the corrected and uncorrected error of two diferent test points with either force data from the dvrk or optotrac
