Test for Actor level fault
=========================
This application simulates a memory fault (segmentation fault) in one of the actors and demonstrates the fault detection and mitigation capabilities of RIAPS.

App Description
-----------------

The app consists of two actors that need to be deployed to two separate nodes.

- The MemFailActor contains a MemPublisher component instance and a MemDevice device component instance.
- The MemMonitorActor contains a MemSubscriber component instance.

The normal mode of operation is a simple publish-subscribe mechanism with MemPublisher acting as the publisher and the MemSubscriber acting as the subscriber. The device component injects a segmentation fault after a period of 10 seconds.

Fault Tolerance
--------------------

Once deplo detects the exception it restarts the actor process and the application resumes normal operation. The state of the actor is detected by writing a file when the actor initially starts and then checking if the file exists when the actor is restarted.
