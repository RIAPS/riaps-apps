# CMakeLists.txt that works with RIAPS v1.1.17 and later
cmake_minimum_required(VERSION 3.10)
project(DistributedEstimator)

option(arch "amd64/armhf" "amd64")
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
else()
 set(CMAKE_C_COMPILER gcc-7)
 set(CMAKE_CXX_COMPILER g++-7)
 set (CMAKE_C_FLAGS "-std=c99")
endif()

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (${arch} STREQUAL "armhf")
 set(riaps_prefix /usr/arm-linux-gnueabihf)
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
        OUTPUT  "${CMAKE_SOURCE_DIR}/include/messages/distributedestimator.capnp.c++"
        DEPENDS "${CMAKE_SOURCE_DIR}/distributedestimator.capnp"
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        COMMAND /opt/riaps/amd64/bin/capnp compile ./distributedestimator.capnp -oc++:./include/messages/
        COMMENT "=== Generating capnp ==="
)

# riaps:keep_localestimator:begin
add_library(localestimator SHARED
        src/LocalEstimator.cc
        src/base/LocalEstimatorBase.cc
        include/base/LocalEstimatorBase.h
        include/LocalEstimator.h
        include/messages/distributedestimator.capnp.c++
        )
target_link_libraries(localestimator PRIVATE czmq riaps dl capnp kj)
set_target_properties(localestimator PROPERTIES PREFIX lib SUFFIX .so)
# riaps:keep_localestimator:end
