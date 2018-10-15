# Transactive Energy

> ***Note:  This is an older application and has not been tested with the current released platform***

This application demonstrates two distributed RIAPS nodes in a network interacting with a distribution level power system simulator (GridLAB-D) and each other.  Each RIAPS node is hosting a different application actor, one is a Generator Actor and the other a Consumer Actor.  The Generator Actor is setting the price of the energy based on the consumer usage, while the Consumer Actor is adjusting their heating setpoint based on the price.  Each actor is responsible for two components:  a controller and a device interface which communicates with GridLAB-D via a RPC.

## Developers

- Gabor Karsai - Institute for Software Integrated Systems at Vanderbilt University
- Abhishek Dubey - Institute for Software Integrated Systems at Vanderbilt University
- Scott Eisele - Institute for Software Integrated Systems at Vanderbilt University

## Installation

1. Install Gridlab-D on the controller host -
* https://sourceforge.net/projects/gridlab-d/files/gridlab-d/Candidate%20release/
  - rpm suggested installing using alien instead https://help.ubuntu.com/community/RPM/AlienHowto
  - Used gridlabd-3.2.0-1.x86_64.rpm file
* sudo apt install alien
* sudo alien -i <package>.rpm
* sudo dpkg -i <package>.deb

2. Install Date and Time Parsing
   ```
   pip3 install aniso8601
   ```

3. RIAPS BBB image installed on BBBs with extra installation of InfluxDB.

   ```
   $ sudo pip3 install influxdb
   ```

4. RIAPS VM installed with extra installation of InfluxDB and Grafana.

   For Grafana:

   ```

      $ wget https://grafanarel.s3.amazonaws.com/builds/grafana_4.1.2-1486989747_amd64.deb     
      $ sudo apt-get install -y adduser libfontconfig      
      $ sudo dpkg -i grafana_4.1.2-1486989747_amd64.deb        
      $ sudo systemctl enable grafana-server.service   
      $ sudo systemctl start grafana-server.service  
      $ rm -rf grafana_4.1.2-1486989747_amd64.deb
   ```

   For InfluxDB:

   ```
      $ sudo apt install curl –y  
      $ curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -      
      $ source /etc/lsb-release     
      $ echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list     
      $ sudo apt-get update -y && sudo apt-get install influxdb -y      
      $ sudo systemctl start influxdb
      $ pip3 install influxdb
   ```

5. Setup a database for Grafana to utilize (this demo used a database named traffic)

## InfluxDB Database Setup on Controller Host (Virtual Machine)

1. Start InfluxDB.  Get back new interactive prompt ('>')

```
      $ influx
      >
```

2. Create database, setup user name and password, and set access permissions

```
      > create database "newDB"
      > create user "riaps" with password "riaps"
      > grant all on "newDB" to "riaps"
      > quit
```

Only value that may need changing is db_host which should be the IP address of your virtual machine (as seen from the Beaglebone)

### Good tutorials on InfluxDB and Graphana

- http://www.andremiller.net/content/grafana-and-influxdb-quickstart-on-ubuntu
- https://community.openhab.org/t/influxdb-grafana-persistence-and-graphing/13761

## App setup
grunner.py dependency
1) ```pip3 install aniso8601```

## Running the Application

1) Login as riaps apps developer
2) Browse to riaps-pycom/tests/TransEn/scripts
3) Run ```./launch-terminals```
4) Use Gridlab-D Control GUI to launch Gridlab-D
 *** configuration files are under gridlabd_configs/ ***
5) Use RIAPS Control to launch generator and consumer controllers
6) Browse to grafana http://localhost:3000/dashboard/db/traffic
7) When done run reset-bones.sh and reset-host.sh

## RIAPS Component Interactions

### GenGridlabD

- Connect to GridLAB-D server with rpc
- Publishes current user heating setpoint data via GenSensorData messages (which are subscribed to by the GenController)
- Subscribes to actuation commands from controller via GenActuatorCommand messages which contain the new price setpoint, and updates the server to that value

### GenController

- Publishes new price setpoint via GenActuatorCommand messages (which are received by GenGridlabD)
- Subscribes to current heating demand of customers in GenGridLAB-D via GenSensorData messages
	- If demand exceeds threshold set price to high value
	- If demand is below threshold set price to low value

### CustGridlabD

- Connect to GridLAB-D server with rpc
- Publishes current generator price data via CustSensorData messages (which are subscribed to by the CustController)
- Subscribes to actuation command from controller via CustActuatorCommand messages which contain the new heating setpoint, and updates the server to that value

### CustController

- Publishes desired heating setpoint to GenGridLAB-D via CustActuatorCommand messages (which are received by CustGridlabD)
- Subscribes to current generator price sensor data from GenGridLAB-D via CustSensorData messages
	- If cost($/MW) exceeds the threshold, set heating setpoint to low value
	- If cost($/MW) is below threshold set heating setpoint to high value
