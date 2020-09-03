Test for Power Failure
=========================
This application simulates a hardware fault (power failure) in one of the nodes and demonstrates the fault detection and mitigation capabilities of RIAPS.

App Description
-----------------

The app consists of two actors that need to be deployed to two separate nodes.

- The PowerFailActor contains a PowerController component instance and a PowerDevice device component instance.
- The PowerMonitorActor contains a PowerMonitor component instance.

The normal mode of operation is a simple publish-subscribe mechanism with PowerController acting as the publisher and the PowerMonitor acting as the subscriber. The device component reboots the node once it receives a "shutdown" request message from the PowerController.

Fault Tolerance
--------------------

Once the node is powered off a peer state change notification is sent to the PowerMonitor component running on the other node. Once the node is back online that is also picked up by the peer state change handler. The deplo is able to restart the application on that node based on the data maintained in the persistent lmdb database. Following that, the application resumes normal operation.
