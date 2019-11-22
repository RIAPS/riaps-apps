# Weather Monitor

RIAPS nodes gathers and publishes local sensor data every 5 seconds. Each node receives the
each other's local sensor data.  This simple application demonstrates the use of publish/
subscribe message handling types in a RIAPS platform.  Two different language implementations are
provided to allow users to see how to program using Python or C++ for the component code.


## Equipment Utilized
- As many RIAPS nodes as desired
- Local router, if using multiple TI Beaglebone Black boards


## Developer
- RIAPS Team, Vanderbilt University


## C++ Application in Eclipse

The following steps can be used to pull this application into an Eclipse project.

1) Pull the content of this repository.

2) Create a "C/C++" project from "Existing Code as Makefile Project".

3) Select the application files under the "Cpp" folder in the local copy of the repository, and select "Cross GCC" toolchain for indexer settings.  The same can be done for the application under the "Mixed" folder.

4) If the CMakeLists.txt file does not exist, run the **riaps-gen** tool to create the component shells and the CMakeLists.txt file.  Below is an example for the DistributedEstimator example where the model file (.json) for the project is specified and the output directory is the current directory.

```
riaps_gen -m DistributedEstimator.json -o .
```

5) Create build targets for both the amd64 and armhf architectures, along with a realclean target.  Default setup works, names typically used are all-amd64 and all-armhf.  The make commands can be found in the "makefile".

6) For C++ indexing, add include paths to the project properties.  Under "C/C++ General" and then "Paths and Symbols", add the following GNU C++ Includes for this project under the GNU C++:

- /usr/include/python3.6m
- /usr/local/include/python3.6/
- /<project_name>/include (this is a workspace path and depends on the project name, utilize "Workspace" navigation when adding this directory path)

7) To easily access the RIAPS platform tools from within Eclipse, import the [riaps_ctrl.launch](https://github.com/RIAPS/riaps-pycom/blob/master/bin/riaps_ctrl.launch) and [riaps_deplo.launch](https://github.com/RIAPS/riaps-pycom/blob/master/bin/riaps_deplo.launch) files.  

>Note: Once imported, be sure to uncheck the "Build before launch" flag which is automatically checked under the "Build" tab of each of these imported external tool configurations.

## RIAPS Specific Project Files

Python application is straight forward with .py files for each application component and model files for the application and deployment.  See https://riaps.github.io/ for more information.

Information on developing C++ components can be found at https://github.com/RIAPS/riaps-core/wiki.  This application includes component base files (.h and .cc) that are setup based on the model file structure. The component implementation code is in the [component].cc files.  Message structure is defined in the include/messages/TempData.capnp file.
