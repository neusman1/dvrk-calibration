# Calibration for dVRK
(This readme is incomplete and undergoing edits)

## Creating a predictive model to evealuate tooltip deflection

All force compliance work can be found in the folder named: "JointForceTesting" all other folders can be disreguarded as old work.

###First:
Start up the dVRK console

```sh
rosrun dvrk_robot dvrk_console_json -j console-PSM2.json
```

###Second:
Run force_joint_space_data_collection.py

```sh
python force_joint_space_data_collection.py
```

When running the data collection, the varibales dX and jointUnderTesting can be changed. dX will alter the poistive/negative direction and amount of joint movement (Typically +-0.00025 was used). jointUnderTesting can be changed from index 0 or 1.

After running, a CSV file will be created. After 4 tests--each joint positive and negative--there will be 4 CSVs.

###Third:

The python script force_joint_space_graphing_evaluation.py can now be run:

```sh
python force_joint_space_graphing_evaluation.py
```

This will take all data files (with proper name "force_joint_space_data_collection_output....." from the local folder "ForceTestingDataJointSpace" to which the data collection saves each csv, and create a compliance model based upon the force, depth and displacment.
A final csv will be saved for each joint which was tested. The csv will have the four A,B,C and D vaules whcih represent the coeefeicents of an equation y = Ax^3+Bx^2+Cx+D. The equation is a model of depth (x) vs Compliance (y), where compliance in the slope of the force (x) vs deflection (y).


###Fourth:

Finally, the force_joint_space_check_model_against_existing_data.py code can be run to check the model against the existing data sets.
It is important to note that the csv file must be speified for hte reader on line 19.

Any and all questions can be directed to Nick Eusman at nick.eusman@gmail.com
