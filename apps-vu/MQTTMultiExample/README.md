# Internet of Things - MQTT communication interfacei - multiple instances

This application demonstrates the suggested way to create multiple MQTT device driver instances for publishing and subscribing to multiple topics. It uses class inheritance for the actual device component instances.

## Requirements

The MQTT device component depends on the Eclipse Paho Python Client library. This library is small and ideally could be included as a subdirectory of the device component, however due to current limitations of the `library` primitive, we need to install this dependency explicitly:

	sudo pip3 install paho-mqtt

See the `MQTTExample` folder for more details w.r.t the MQTT interface and running the app.
