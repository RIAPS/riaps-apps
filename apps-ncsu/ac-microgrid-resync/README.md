# Microgrid Resynchronization

This application was presented at the 2017 ARPA-E Energy Innovation Summit (March) and refined for the Year 1 Demo of the ARPA-E Open 2015 grant program.

This application is used for microgrid resynchronization.

This application uses two RIAPS nodes. One node is receiving the C37 message from SEL relay and then forwards this message back to OPAL-RT. This message contains the voltage difference between the two sides of the relay. The inverter model in OPAL-RT will use this difference for resynchronization. The other is a data logging node whose task is to record and display the data.

A video of this demonstration can be seen at https://youtu.be/-xI4aiDZlwQ.


## Developers

- Hao Tu, FREEDM System Center, North Carolina State University, Raleigh
- Yuhua Du, FREEDM System Center, North Carolina State University, Raleigh
- Rishabh Jain, FREEDM System Center, North Carolina State University, Raleigh
- Srdjan Lukic, FREEDM System Center, North Carolina State University, Raleigh
- David Lubkeman, FREEDM System Center, North Carolina State University, Raleigh

If you have any question, please contact htu@ncsu.edu or ydu7@ncsu.edu.


## Installation

Hardware used: 

1. Two BBBs, 
2. OPAL-RT simulator, 
3. OPAL-RT I/O expansion unit, 
4. SEL Relay. 

All the hardware should be connected to the same network using LAN cables. OPAL-RT I/O expansion unit is connected to SEL Relay through hard wires. The voltage of microgrid and main grid are sent to SEL Relay through those wires in the form of analog signals.

Software packages:

1. RIAPS BBB image installed on BBBs with extra installation of InfluxDB. 
    
   $sudo pip3 install influxdb
   
2. RIAPS VM installed with extra installation of InfluxDB and Grafana.
   
   For Grafana:
   
   ```
      $ sudo apt install curl –y     
      $ wget https://grafanarel.s3.amazonaws.com/builds/grafana_4.1.2-1486989747_amd64.deb     
      $ sudo apt-get install -y adduser libfontconfig      
      $ sudo dpkg -i grafana_4.1.2-1486989747_amd64.deb      
      $ sudo systemctl start grafana-server      
      $ sudo systemctl enable grafana-server.service     
      $ rm -rf grafana_4.1.2-1486989747_amd64.deb
   ```
      
   For InfluxDB:
   
   ```
      $ curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -      
      $ source /etc/lsb-release     
      $ echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list     
      $ sudo apt-get update -y && sudo apt-get install influxdb -y      
      $ sudo systemctl start influxdb
   ```
   
## Running the Application

To start the application:
1. Start VM and open 4 terminals.
2. Start rpyc_regisration.py service in 1st terminal.
3. Start riaps_ctrl in 2nd terminal, the RIAPS GUI should start.
4. In the 3rd terminal, ssh to the first BBB and start riaps_deplo.
5. In the 4th terminal, ssh to the second BBB and start riaps_deplo.
6. In RIAPS GUI, load the .riaps file and .depl file and hit launch.
7. Start the simulation in OPAL-RT.
8. In OPAL-RT simulation, disconnect the relay to island the microgrid.
9. In OPAL-RT simulation, start secondary control.
10. In OPAL-RT simulation, start resynchronization.


You should see:
1. The first BBB should receive C37 configuration message from the relay.
2. The second BBB should be connected to the InfluxDB database on VM. In Grafana, the data is displayed in realtime.
3. In OPAL-RT simulation, the voltage magnitude and angle difference starts to grow after step 8 islanding.
4. Once the secondary control is started, the voltage magnitude difference will be eliminated. The angle difference will become constant.
5. After start resynchronization, the angle difference will be reducing until it enters the reclosing range (around 3 degree). Then, you should hear the click of the relay when it is reclosing.


## Others

This application demonstrates the communication capability of RIAPS platform. The data flow is as follow:

1. During simulation, the three phase voltage of microgrid and main grid are sent from OPAL-RT I/O expansion unit to SEL Relay in form of analog signals.
2. SEL Relay senses the voltages and calculates the voltage magnitude and phase angle of the microgrid and main grid.
3. SEL Relay sends out the calculated voltage magnitudes and phase angles using C37.118 protocol to the first BBB base on IP addresses (This is initiated by the first BBB as C37.118 is like a client-server protocol).
4. The first BBB receives the C37 frames and publish the data as RIAPS messages.
5. The second BBB receives the RIAPS messages and stores the data in database.
6. The first BBB receives the RIAPS messages and rebuild C37 frames.
7. The first BBB sends rebuilt C37 frames to OPAL-RT simulator where the data are used for resynchronization purpose.
