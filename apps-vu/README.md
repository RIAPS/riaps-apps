# RIAPS Applications Developed by Vanderbilt University

This is a collection of applications used to demonstrate the features of the RIAPS platform

1. **distributed-phase-estimation**: This application demonstrates the time-sync capabilities of the
RIAPS Framework.

2. **DistributedEstimator**:  This application demonstrates two different basic message handling 
types:  publish/subscribe and request/reply.  Examples of how to structure both Python and C++ 
application code are provided.

3. **DistributedEstimatorGpio**: This application shows several RIAPS nodes communicating to
determine an estimated value then providing user feedback by controlling the node hardware (gpio).

4. **mqtt-interface**: This application demonstrates the use of the MQTT device driver for publishing
and subscribing with an external broker.

5. **mqtt-multi-interface**: This application demonstrates the suggested way to create multiple MQTT
device driver instances for publishing and subscribing to multiple topics.

6. **simulink-example**: This example shows a potential integration approach for RIAPS applications
with Simulink.

7. **transactive-blockchain**: This application demonstrates the advanced features of the RIAPS application;
specifically Resource and Fault Management, along with time sensitive messaging.

8. **transactive-energy**: This application demonstrates two distributed RIAPS nodes in a network
interacting with a distribution level power system simulator (GridLAB-D) and each other.

    This application was demonstrated at the 2017 ARPA-E Energy Innovation Summit.

9. **TSyncGpio**:  This example demonstrates the accuracy of the RIAPS time synchronized coordinated action.

    This application was demonstrated at the 2018 ARPA-E Energy Innovation Summit.
    
10. **WeatherMonitor**:  This simple application demonstrates the use of publish/subscribe message handling 
types in a RIAPS platform.  Examples of how to structure both Python and C++ application code are provided.
