# Distributed Estimator using GPIOs

Several RIAPS nodes (beaglebone black boards) gather local sensor data at different rates 
(0.5 Hz, 1 Hz and 2 Hz) and toggle one of the blue LEDs on the board when the estimate is 
published. A single RIAPS node subscribes to the estimates and provides a running average 
of the estimates. This node will print out the running average at a 4 Hz rate and toggle 
a blue LED on the board.

The component code is provided in Python.

## Equipment Utilized
- 4 Beaglebone Black boards
	- 3 Local estimators
	- 1 Global aggregator
- Local router

## Dependencies

Utilized the Adafruit BBIO library to control the blue user controlled LEDs, which are 
just GPIOs

```
sudo pip3 install Adafruit_BBIO
```

## Application Configuration to Running Platform

The application deployment model (DistributedEstimatorGpio.depl) needs to be configured to match the system this application is running on.  Be sure to update the deployment locations for each of the deployed actors.

## Developers
- RIAPS Team, Vanderbilt University
