# MQTT Modbus

The Green Energy Hub Testbed of The FREEDM Systems Center is made up of eight BBBs serially connected to DSPs. The BBBs are needed to communicate with a user interface through MQTT. The user can receive info from the system and send commands to all the devices. The command goes to the BBBs via MQTT, and then uses Modbus communication protocol to send commands to the DSP that is attached to the desired Hardware.  Measurements data runs the reverse path.


## Developers

The codes have been developed by Danny Crescimone thanks to the help of RIAPS developers like Mary Metelko and Peter Volgesy and also all the people of FREEDM Systems Center.

## Installation
Follow these instructions to install the Modbus-MQTT application:
1. Install RIAPS on a Computer (follow the instruction of https://github.com/RIAPS/riaps-integration/blob/master/riaps-x86runtime/README.md)
2. Flash the BBB (follow the instruction of https://github.com/RIAPS/riapsintegration/blob/master/riaps-bbbruntime/README.md)
3. (only for RIAPS 1.1.15) Turn off the security by editing/usr/local/riaps/etc/riaps.conf and changing “security = off” on both the VM and BBBs.
4. (only for RIAPS 1.1.15) Log into the VM and copy the public key to the authorized keys – “sudo cp/usr/local/riaps/keys/id_rsa.pub ~/.ssh/authorized_keys
5. Connect via Ethernet both VM and BBBs to a router (with a working internet connection)
6. Install the MQTT library both on VM and BBBs
```
sudo pip3 install paho-mqtt
```

7. Test MQTT (follow the instruction of https://github.com/RIAPS/riaps-apps/tree/master/apps-vu/MQTTExample)
8. In the VM, open the folder MQTTModbus and check the .deplo file (see if the IP addresses match the wanted devices) it could be useful to know or set the topics of MQTT
9. Inside the .riaps file check the IP address of the BROKER (it is written twice inside the code) that one wants to use: or a private broker created on the computer or free online broker such as iot.eclipse.org test.mosquitto.org
10. For Modbus connection follow the instruction of https://github.com/RIAPS/riaps-library/tree/master/ModbusTesting/ModbusUartReqRepTesting
11. Check the slave addresses and baud rate inside the .riaps file (they have to match those ones of the Modbus slaves)
12. Launch the RIAPS CTRL and deploy the application code.

## Running the Application
Once the installation part is finished it is possible to use the RIAPS CTRL window to start the application. Now it can use MQTT.FX (MQTT client that one can retrieve on https://mqttfx.jensd.de/) using the same broker of the application to subscribe to the topics defined in the ".deplo" file, and also to Publish the commands.


## Others
More detail about the meaning and the working process of the code can be found in the pdf: [README_MQTTModbus_code_explanation.pdf](https://github.com/RIAPS/riaps-apps/tree/master/apps-ncsu/MQTTModbus/README_MQTTModbus_code_explanation.pdf)
