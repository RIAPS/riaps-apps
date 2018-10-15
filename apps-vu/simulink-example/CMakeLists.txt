cmake_minimum_required(VERSION 3.0)
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_CXX_FLAGS "-std=c++11")
set(CMAKE_C_FLAGS "-std=c99")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/${ARCH}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY  ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
#Library Dependencies
set(DEPENDENCIES ${RIAPS_PREFIX})
set (LIBALLPATH_INCLUDE ${DEPENDENCIES}/include)
set (LIBALLPATH_LIB ${DEPENDENCIES}/lib)
link_directories(${LIBALLPATH_LIB})
include_directories(${CMAKE_SOURCE_DIR}//messages-gen)
include_directories(${CMAKE_SOURCE_DIR}/cpp/include)
include_directories(${CMAKE_SOURCE_DIR}/simulink)

# Generating the headers and cpp for message edu.vanderbilt.riaps.app.impl.FStructTypeImpl@77f11117 (name: ForceType)
add_custom_command(OUTPUT  "${CMAKE_SOURCE_DIR}/messages-gen/ForceType.capnp.c++"
				   DEPENDS "${CMAKE_SOURCE_DIR}/messages-gen/ForceType.capnp" 
				   WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}//messages-gen"  
				   COMMAND ${CMAKE_COMMAND} -E env "PATH=/opt/riaps/amd64/bin" capnp compile -oc++ "${CMAKE_SOURCE_DIR}/messages-gen/ForceType.capnp" --import-path="${CMAKE_SOURCE_DIR}//messages-gen"
				   )

# Generating the headers and cpp for message edu.vanderbilt.riaps.app.impl.FStructTypeImpl@49990996 (name: PositionType)
add_custom_command(OUTPUT  "${CMAKE_SOURCE_DIR}/messages-gen/PositionType.capnp.c++"
				   DEPENDS "${CMAKE_SOURCE_DIR}/messages-gen/PositionType.capnp" 
				   WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}//messages-gen"  
				   COMMAND ${CMAKE_COMMAND} -E env "PATH=/opt/riaps/amd64/bin" capnp compile -oc++ "${CMAKE_SOURCE_DIR}/messages-gen/PositionType.capnp" --import-path="${CMAKE_SOURCE_DIR}//messages-gen"
				   )

# Creating Libraries for Component edu.vanderbilt.riaps.app.impl.ComponentImpl@54ee020a (name: Sensor) (language: python, realtime: false)
add_library(sensor 
			SHARED ${CMAKE_CURRENT_SOURCE_DIR}/cpp/Sensor.cc
			${CMAKE_CURRENT_SOURCE_DIR}/cpp/SensorBase.cc
			${CMAKE_SOURCE_DIR}/messages-gen/PositionType.capnp.c++
			)
			
target_link_libraries(sensor czmq riaps dl capnp kj)
install(TARGETS sensor DESTINATION lib)

# Creating Libraries for Component edu.vanderbilt.riaps.app.impl.ComponentImpl@1c807f2d (name: Actuator) (language: python, realtime: false)
add_library(actuator 
			SHARED ${CMAKE_CURRENT_SOURCE_DIR}/cpp/Actuator.cc
			${CMAKE_CURRENT_SOURCE_DIR}/cpp/ActuatorBase.cc
			${CMAKE_CURRENT_SOURCE_DIR}/cpp/include/ActuatorBase.h
			${CMAKE_CURRENT_SOURCE_DIR}/cpp/include/Actuator.h
			${CMAKE_SOURCE_DIR}/messages-gen/ForceType.capnp.c++
			)
			
target_link_libraries(actuator czmq riaps dl capnp kj)
install(TARGETS actuator DESTINATION lib)

# Creating Libraries for Component edu.vanderbilt.riaps.app.impl.ComponentImpl@7c42b8c6 (name: Controller) (language: python, realtime: false)
add_library(controllersl 
			SHARED ${CMAKE_CURRENT_SOURCE_DIR}/cpp/ControllerSL.cc
			${CMAKE_CURRENT_SOURCE_DIR}/cpp/ControllerSLBase.cc
            ${CMAKE_CURRENT_SOURCE_DIR}/cpp/include/ControllerSL.h
            ${CMAKE_CURRENT_SOURCE_DIR}/cpp/include/ControllerSLBase.h
			${CMAKE_SOURCE_DIR}/messages-gen/ForceType.capnp.c++
			${CMAKE_SOURCE_DIR}/messages-gen/PositionType.capnp.c++
            ${CMAKE_SOURCE_DIR}/simulink/Controller.cc
            ${CMAKE_SOURCE_DIR}/simulink/Controller.h
            ${CMAKE_SOURCE_DIR}/simulink/Controller_private.h
            ${CMAKE_SOURCE_DIR}/simulink/Controller_types.h
            ${CMAKE_SOURCE_DIR}/simulink/rt_defines.h
            ${CMAKE_SOURCE_DIR}/simulink/rtwtypes.h
			)
			
target_link_libraries(controllersl czmq riaps dl capnp kj)
install(TARGETS controllersl DESTINATION lib)

