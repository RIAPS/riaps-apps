cmake_minimum_required(VERSION 3.0)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY  ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

include_directories(/usr/include/python3.6m/)
include_directories(${RIAPS_PREFIX}/include/pybind11/include)

include_directories(${RIAPS_PREFIX}/include)
link_directories(${RIAPS_PREFIX}/lib)

include_directories(include)

add_custom_command(
        OUTPUT  ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/TempData.capnp.c++ ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/TempData.capnp.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/TempData.capnp
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/messages
        COMMAND /opt/riaps/amd64/bin/capnp compile TempData.capnp -oc++:./
        COMMENT "=== Generating capnp ==="
)

add_library(tempsensor SHARED src/TempSensor.cc
                              src/base/TempSensorBase.cc
                              ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/TempData.capnp.c++
                              include/base/TempSensorBase.h
                              include/TempSensor.h)
target_link_libraries(tempsensor PRIVATE czmq riaps dl capnp kj)
set_target_properties(tempsensor PROPERTIES PREFIX lib SUFFIX .so)

add_library(tempmonitor SHARED src/TempMonitor.cc
                   			   src/base/TempMonitorBase.cc
							   ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/TempData.capnp.c++
							   include/base/TempMonitorBase.h
							   include/TempMonitor.h)
target_link_libraries(tempmonitor PRIVATE czmq riaps dl capnp kj)
set_target_properties(tempmonitor PROPERTIES PREFIX lib SUFFIX .so)



