# Time Synchronized Coordinated Action Example

> ***Note: This is an older application and has not been tested with the current released platform***

This example demonstrates the accuracy of the RIAPS time synchronized coordinated action. In the example four BBBs are running the same RIAPS application. The applications are periodically (default: every 5th seconds) proposing an `<action, time>` pair to the leader. The participating nodes are voting about whether to execute the `action` at `time` or not.

* The `action` is an action ID, well known by all members.
* The `time` is absolute time, represented in [`timespec`](http://en.cppreference.com/w/c/chrono/timespec) structure. Its value calculated periodically by the following formula: `current_time+random(1,4)` seconds.
* The leader forwards the proposed `<action, time>` pair to the participating nodes and it sets up a timeout for the voting process. If the majority is not reached in the given time the leader rejects the proposed action.
* When a proposed value arrives to a group member then it checks whether the proposed action may already accepted OR already pending. If the proposed action is not pending (not scheduled yet) AND not accepted then the member sends an `ACCEPT` vote to the leader. (Note: this is not a mandatory step but this example excludes the "overlapping" actions in order to measure the accuracy on the oscilloscope).
* If the majority is achieved the leader announces the results and the members schedules the action. (Note: if the schedule fails, the node is able to veto the action by notifying the leader about the unsuccessful scheduling).
* When the `time` has come, then `action` is called automatically (the GPIO ports are toggled).
* By connecting the oscilloscope to the GPIO port 31 the accuracy can be measured. 

## Prerequisites

* 4 BeagleBone Black (BBB), connected to the same router
* Oscilloscope (with 4ch)
* Installed [riaps-core](https://github.com/RIAPS/riaps-core/releases/tag/0.6.3rc4) v0.6.4
* Installed [riaps-externals](https://github.com/RIAPS/riaps-externals/releases/tag/0.6.1) v0.6.1
* Install libsoc on BBBs

## Installing libsoc

```
git clone https://github.com/jackmitch/libsoc.git libsoc.git
sudo apt-get install autoconf libtool-bin pkg-config
cd libsoc.git
autoreconf -i
./configure --disable-debug --enable-board=beaglebone_black
make
make install
```

## Build the project

```sh
git clone https://github.com/RIAPS/riaps-apps.git
cd ./riaps-apps/TSyncGpio
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=.toolchain.arm-linux-gnueabihf.cmake -DCMAKE_INSTALL_PREFIX="/" ../
```

(Note: As an alternative you can build the example in Eclipse with the [riaps-dsml](https://github.com/RIAPS/riaps-dsml) plugin)

## Setup Time Synchronization on BBBs
 
* Setup NTP master for one BBB and the other BBBs are slaves
```
sudo /opt/riaps/armhf/bin/tsman config ntp-master
sudo /opt/riaps/armhf/bin/tsman config slave
```

## Deploy the application

Copy the built output to the BBBs using `scp`:

```sh
scp libtscagpio.so TSyncGpio_app.json riaps@<BBBaddress>:/home/riaps/riaps_apps/TSyncGpio/
```

(Note: As an alternative, the `riaps_deplo` and `riaps_ctrl` can be used for deployment.) `//TODO: LINK!!!`

## Turn off riaps-deplo service (if enabled)

If the 'riaps-deplo.service' is started and running on the BBBs, 'rdiscoveryd' will already be running.  For this implementation of the application, we want to use 'rdiscoveryd' alone.  So, check that the 'riaps-deplo.service' is running on the BBBs and stop it, if it is.

```
sudo systemctl status riaps-deplo.service
sudo systemctl stop riaps-deplo.service
```

## Running the example

Do the following on each BBB node:

1) Start the discovery service

```sh
rdiscoveryd
```

2) Setup real-time capability for start_actor (only needed the first time this is run on the node)
```
sudo setcap cap_sys_nice+ep /opt/riaps/armhf/bin/start_actor
```

3) Start the application by `start_actor` 
```sh
cd ~/riaps_apps/TSyncGpio
start_actor TSyncGpio TSyncGpio_app.json ActOne
```
