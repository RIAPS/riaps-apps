# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.10

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/riaps/riaps_apps/Distributed_Voltage_Observer

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf

# Include any dependencies generated for this target.
include CMakeFiles/modbusuart.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/modbusuart.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/modbusuart.dir/flags.make

../../include/messages/distributedvoltage.capnp.c++: ../../distributedvoltage.capnp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold --progress-dir=/home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "=== Generating capnp ==="
	cd /home/riaps/riaps_apps/Distributed_Voltage_Observer && capnp compile ./distributedvoltage.capnp -oc++:./include/messages/

CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o: CMakeFiles/modbusuart.dir/flags.make
CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o: ../../src/ModbusUART.cc
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o"
	/usr/bin/arm-linux-gnueabihf-g++-7  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o -c /home/riaps/riaps_apps/Distributed_Voltage_Observer/src/ModbusUART.cc

CMakeFiles/modbusuart.dir/src/ModbusUART.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/modbusuart.dir/src/ModbusUART.cc.i"
	/usr/bin/arm-linux-gnueabihf-g++-7 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/riaps/riaps_apps/Distributed_Voltage_Observer/src/ModbusUART.cc > CMakeFiles/modbusuart.dir/src/ModbusUART.cc.i

CMakeFiles/modbusuart.dir/src/ModbusUART.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/modbusuart.dir/src/ModbusUART.cc.s"
	/usr/bin/arm-linux-gnueabihf-g++-7 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/riaps/riaps_apps/Distributed_Voltage_Observer/src/ModbusUART.cc -o CMakeFiles/modbusuart.dir/src/ModbusUART.cc.s

CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.requires:

.PHONY : CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.requires

CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.provides: CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.requires
	$(MAKE) -f CMakeFiles/modbusuart.dir/build.make CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.provides.build
.PHONY : CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.provides

CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.provides.build: CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o


CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o: CMakeFiles/modbusuart.dir/flags.make
CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o: ../../src/base/ModbusUARTBase.cc
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o"
	/usr/bin/arm-linux-gnueabihf-g++-7  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o -c /home/riaps/riaps_apps/Distributed_Voltage_Observer/src/base/ModbusUARTBase.cc

CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.i"
	/usr/bin/arm-linux-gnueabihf-g++-7 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/riaps/riaps_apps/Distributed_Voltage_Observer/src/base/ModbusUARTBase.cc > CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.i

CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.s"
	/usr/bin/arm-linux-gnueabihf-g++-7 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/riaps/riaps_apps/Distributed_Voltage_Observer/src/base/ModbusUARTBase.cc -o CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.s

CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.requires:

.PHONY : CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.requires

CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.provides: CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.requires
	$(MAKE) -f CMakeFiles/modbusuart.dir/build.make CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.provides.build
.PHONY : CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.provides

CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.provides.build: CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o


CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o: CMakeFiles/modbusuart.dir/flags.make
CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o: ../../include/messages/distributedvoltage.capnp.c++
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building CXX object CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o"
	/usr/bin/arm-linux-gnueabihf-g++-7  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o -c /home/riaps/riaps_apps/Distributed_Voltage_Observer/include/messages/distributedvoltage.capnp.c++

CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.i"
	/usr/bin/arm-linux-gnueabihf-g++-7 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/riaps/riaps_apps/Distributed_Voltage_Observer/include/messages/distributedvoltage.capnp.c++ > CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.i

CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.s"
	/usr/bin/arm-linux-gnueabihf-g++-7 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/riaps/riaps_apps/Distributed_Voltage_Observer/include/messages/distributedvoltage.capnp.c++ -o CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.s

CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.requires:

.PHONY : CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.requires

CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.provides: CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.requires
	$(MAKE) -f CMakeFiles/modbusuart.dir/build.make CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.provides.build
.PHONY : CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.provides

CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.provides.build: CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o


# Object files for target modbusuart
modbusuart_OBJECTS = \
"CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o" \
"CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o" \
"CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o"

# External object files for target modbusuart
modbusuart_EXTERNAL_OBJECTS =

../../libmodbusuart.so: CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o
../../libmodbusuart.so: CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o
../../libmodbusuart.so: CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o
../../libmodbusuart.so: CMakeFiles/modbusuart.dir/build.make
../../libmodbusuart.so: CMakeFiles/modbusuart.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Linking CXX shared library ../../libmodbusuart.so"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/modbusuart.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/modbusuart.dir/build: ../../libmodbusuart.so

.PHONY : CMakeFiles/modbusuart.dir/build

CMakeFiles/modbusuart.dir/requires: CMakeFiles/modbusuart.dir/src/ModbusUART.cc.o.requires
CMakeFiles/modbusuart.dir/requires: CMakeFiles/modbusuart.dir/src/base/ModbusUARTBase.cc.o.requires
CMakeFiles/modbusuart.dir/requires: CMakeFiles/modbusuart.dir/include/messages/distributedvoltage.capnp.c++.o.requires

.PHONY : CMakeFiles/modbusuart.dir/requires

CMakeFiles/modbusuart.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/modbusuart.dir/cmake_clean.cmake
.PHONY : CMakeFiles/modbusuart.dir/clean

CMakeFiles/modbusuart.dir/depend: ../../include/messages/distributedvoltage.capnp.c++
	cd /home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/riaps/riaps_apps/Distributed_Voltage_Observer /home/riaps/riaps_apps/Distributed_Voltage_Observer /home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf /home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf /home/riaps/riaps_apps/Distributed_Voltage_Observer/build/armhf/CMakeFiles/modbusuart.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/modbusuart.dir/depend

