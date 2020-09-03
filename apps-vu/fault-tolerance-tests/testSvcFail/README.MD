RIAPS Services Failure
==========================

This application tests the scenario where one of the RIAPS services, either the deployment service or the discovery service, crashes. The service name is configurable as an argument passed to the actor.

App Description
-----------------

The app consists of two actors that need to be deployed to two separate nodes.

- The SvcFailActor contains a SvcController component instance and a SvcDevice device component instance. The service name is passed as an argument to this actor which is then passed to the SvcController component.
- The SvcMonitorActor contains a SvcMonitor component instance.

The normal mode of operation is a simple publish-subscribe mechanism with SvcController acting as the publisher and the SvcMonitor acting as the subscriber. The device component shuts down the requested service once it receives a message from the SvcController component.

Fault tolerance
--------------------

- Deplo crashes : A peer state change notification is sent to the PowerMonitor component running on the other node. Based on the systemd configuration the deplo is restarted automatically. Once deplo is back online that is also picked up by the peer state change handler. Following that, the application resumes normal operation.
- Disco crashes : The crash is detected by deplo and it restarts the discovery process. This can be detected by the SvcDevice device which polls on the list of process ids to find the current status of the service specified.
