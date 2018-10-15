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
        OUTPUT  ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/distributedestimator.capnp.c++ ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/distributedestimator.capnp.h
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/distributedestimator.capnp
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/messages
        COMMAND /opt/riaps/amd64/bin/capnp compile distributedestimator.capnp -oc++:./
        COMMENT "=== Generating capnp ==="
)

add_library(globalestimator SHARED src/GlobalEstimator.cc
                                   src/base/GlobalEstimatorBase.cc
                                   ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/distributedestimator.capnp.c++)
target_link_libraries(globalestimator czmq riaps dl capnp kj)
set_target_properties(globalestimator PROPERTIES PREFIX lib SUFFIX .so)

add_library(localestimator SHARED src/LocalEstimator.cc
                                  src/base/LocalEstimatorBase.cc
                                  ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/distributedestimator.capnp.c++)
target_link_libraries(localestimator czmq riaps dl capnp kj)
set_target_properties(localestimator PROPERTIES PREFIX lib SUFFIX .so)

add_library(sensor SHARED src/Sensor.cc
                          src/base/SensorBase.cc
                          ${CMAKE_CURRENT_SOURCE_DIR}/include/messages/distributedestimator.capnp.c++)
target_link_libraries(sensor czmq riaps dl capnp kj)
set_target_properties(sensor PROPERTIES PREFIX lib SUFFIX .so)
