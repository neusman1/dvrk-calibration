# Calibration for dVRK
(This readme is incomplete and undergoing edits)

## Using the DH Calibration 
#### (Step One)


use dh calib to modify offsets in json file

```json
```
Make sure to restart the consol after making changes to the json file

####(Step Two)----needs to be finished

## Creating a predictive model to evealuate tooltip deflection
### Setting up the nodes

set up nodes
(make sure the atracsys and optoForce are on) 
(ensure you are in the dialout group by using the "id" comand )

```sh
rosrun dvrk_robot dvrk_console_json -j console-PSM2.json
rosrun atracsys_ros atracsys_json
rosrun optoforce_ros optoforce_json -s /dev/ttyACM0 -j OMD-10-SE-10N.json

//for the optoforce, the exact directory may need to be specified:
rosrun optoforce_ros optoforce_json -s /dev/ttyACM0 -j /home/neusman1/catkin_ws/src/cisst-saw/sawOptoforceSensor/share/OMD-10-SE-10N.json
```

While testing, it's good to watch the values using rostopic echo:
```sh
rostopic echo /dvrk/PSM3/wrench_body_current
rostopic echo /atracsys/fiducials 
rostopic echo /optoforce/wrench
```


### get the transformation matrix
This will save locally a transformation matrix for the atracsys to be put in the cartesian field of the dvrk
```sh
python atracsys-dvrk-cartesian-calibration.py PSM2
```

### collect data
Run the data cllection in shell as follows
```sh
 python force_data_collection.py PSM3
```
Usualy the data collection is run at 5 depths (z positions), for the x, y and z axis. Data is gathered 10 times at each depth with forces being applied to each of three axis. It is suggested that the transfomration matrix is retaken at least once durring data collection


### data interpretation
```sh
python force_evaluation.py
```
The above program will gather all data files in the ForceTestingData directory and create a predictive linear model. 

### verify created model against test points
```sh
python force_test_points.py
```
The model can return the corrected and uncorrected error of 6 diferent test points across 3 axis, 2 depths
