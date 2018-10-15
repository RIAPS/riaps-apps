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

The following steps can be used to pull this application into an eclipse project.

1) Create a "C/C++" project from "Existing Code as Makefile Project".

2) Locate the application files under the "Cpp" folder and select "Linux GCC"
toolchain for indexer settings.  

3) Build files are provided with the project to allow compilation for both amd64
and armhf libraries of the components.  The makefile will utilize the project specific
CMakeLists.txt file and toolchain specific .cmake files (.toolchain.amd64.cmake
and .toolchain.arm-linux-gnueabihf.cmake).  The CMakeList.txt file has application specific instructions.

4) Create build targets for both the amd64 and armhf architectures, along with
a generic clean target.  Default setup works, names typically used are build-amd64
and build-armhf.  

5) For C++ indexing, add include paths to the project properties.  Under "C/C++ General" and then
"Paths and Symbols", add the following GNU C++ Includes for this project:

- /usr/include/python3.6m
- /opt/riaps/amd64/include
- /opt/riaps/amd64/include/pybind11/include
- /DistributedEstimatorCpp/include (this is a workspace path)

6) To easily access the RIAPS platform tools from within Eclipse, import the [riaps_ctrl.launch](https://github.com/RIAPS/riaps-pycom/blob/master/bin/riaps_ctrl.launch) and [riaps_deplo.launch](https://github.com/RIAPS/riaps-pycom/blob/master/bin/riaps_deplo.launch) files.  

>Note: Once imported, be sure to uncheck the "Build before launch" flag which is automatically checked under the "Build" tab of each of these imported external tool configurations.

## RIAPS Specific Project Files

Python application is straight forward with .py files for each application component and model files for the application and deployment.  See https://riaps.github.io/ for more information.

Information on developing C++ components can be found at https://github.com/RIAPS/riaps-core/wiki.  This application includes component base files (.h and .cc) that are setup based on the model file structure. The component implementation code is in the [component].cc files.  Message structure is defined in the include/messages/TempData.capnp file.
