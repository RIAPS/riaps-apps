# CMakeLists.txt that works with RIAPS v1.1.17 and later
cmake_minimum_required(VERSION 3.10)
project(Sltest)

option(arch "amd64/armhf/arm64" "amd64")
set(CMAKE_SYSTEM_NAME Linux)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-Wno-psabi")

set(PYBIND11_CPP_STANDARD -std=c++17)

#Set the platform
if (${arch} STREQUAL "armhf")
 set(TOOLCHAIN_PREFIX /usr/bin/arm-linux-gnueabihf)
 set(CMAKE_C_COMPILER ${TOOLCHAIN_PREFIX}-gcc)
 set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}-g++-7)
 set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_PREFIX})
 set (CMAKE_C_FLAGS "-std=c99")
elseif(${arch} STREQUAL "arm64")
 set(TOOLCHAIN_PREFIX /usr/bin/aarch64-linux-gnu)
 set(CMAKE_C_COMPILER ${TOOLCHAIN_PREFIX}-gcc)
 set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}-g++-7)
 set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_PREFIX})
 set (CMAKE_C_FLAGS "-std=c99")
else()
 set(CMAKE_C_COMPILER gcc-7)
 set(CMAKE_CXX_COMPILER g++-7)
 set (CMAKE_C_FLAGS "-std=c99")
endif()

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (${arch} STREQUAL "armhf")
 set(riaps_prefix /usr/arm-linux-gnueabihf)
elseif (${arch} STREQUAL "arm64")
 set(riaps_prefix /usr/aarch64-linux-gnu)
else()
 set(riaps_prefix /usr/local)
endif()

set(DEPENDENCIES ${riaps_prefix})
set (LIBALLPATH_INCLUDE ${DEPENDENCIES}/include)
set (LIBALLPATH_LIB ${DEPENDENCIES}/lib)
include_directories(${LIBALLPATH_INCLUDE})
include_directories(/usr/include/python3.6m/)
include_directories(/usr/local/include/python3.6/)
link_directories(${LIBALLPATH_LIB})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

include_directories(include)

# riaps:keep_cmake:begin

# riaps:keep_cmake:end


add_custom_command(
        OUTPUT  "${CMAKE_SOURCE_DIR}/include/messages/sltest.capnp.c++"
        DEPENDS "${CMAKE_SOURCE_DIR}/sltest.capnp"
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        COMMAND /opt/riaps/amd64/bin/capnp compile ./sltest.capnp -oc++:./include/messages/
        COMMENT "=== Generating capnp ==="
)

# riaps:keep_controllersl:begin
add_library(controllersl SHARED
        src/ControllerSL.cc
        src/base/ControllerSLBase.cc
        include/base/ControllerSLBase.h
        include/ControllerSL.h
        include/messages/sltest.capnp.c++
        simulink/Controller.cc
		simulink/Controller.h
		simulink/Controller_private.h
		simulink/Controller_types.h
		simulink/rt_defines.h
		simulink/rtwtypes.h
        )
target_link_libraries(controllersl PRIVATE czmq riaps dl capnp kj)
set_target_properties(controllersl PROPERTIES PREFIX lib SUFFIX .so)
# riaps:keep_controllersl:end

# riaps:keep_sensor:begin
add_library(sensor SHARED
        src/Sensor.cc
        src/base/SensorBase.cc
        include/base/SensorBase.h
        include/Sensor.h
        include/messages/sltest.capnp.c++
        )
target_link_libraries(sensor PRIVATE czmq riaps dl capnp kj)
set_target_properties(sensor PROPERTIES PREFIX lib SUFFIX .so)
# riaps:keep_sensor:end

# riaps:keep_actuator:begin
add_library(actuator SHARED
        src/Actuator.cc
        src/base/ActuatorBase.cc
        include/base/ActuatorBase.h
        include/Actuator.h
        include/messages/sltest.capnp.c++
        )
target_link_libraries(actuator PRIVATE czmq riaps dl capnp kj)
set_target_properties(actuator PROPERTIES PREFIX lib SUFFIX .so)
# riaps:keep_actuator:end
