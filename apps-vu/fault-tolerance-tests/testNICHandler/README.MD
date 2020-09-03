(Extended the testNICHandler app in riaps-test to include an additional actor which has a component that gets peer state change notifications.)

Test for Network Fault
=========================
This application simulates a network interface fault in one of the nodes and demonstrates the fault detection and mitigation capabilities of RIAPS.

App Description
-----------------

The app consists of two actors that need to be deployed to two separate nodes.

- The NicFailActor contains a CompReq component instance and a NicDevice device component instance.
- The NicMonitorActor contains a NicMonitor component instance.

The CompReq component publishes some values which the NicMonitor component subscribes to. The CompReq component has a sporadic timer which sends a NIC 'up' or 'down' request to the device component. When the NicDevice component receives a request it brings the network interface up or down according to the request received.

Fault Tolerance
--------------------

Once the network interface state changes, a NIC state change notification is generated internal to the actor which is detected by the handleNICStateChange method in the CompReq component. Additionally, when the NicMonitorActor loses contact with the NicFailActor, a peer state change notification is generated which is detected by the handlePeerStateChange handler invoked in the NicMonitor component. Once the NIC state is brought down, the CompReq component sends another request to bring it up in the next timer invocation to recover the application. Since, both CompReq and NicDevice are colocated in the same actor, their inter-communication can still take place when the network interface is down.
