# Internet of Things - MQTT communication interface

This application includes and demonstrates the use of the MQTT device driver for publishing and subscribing with an 
external broker. 

The Device component is implemented in Python and provides the following communication ports:
 - outgoing (sub): for sending an arbitrary Python object to the broker. The object is serialized as a UTF-8 encoded JSON string
 - incoming (pub): for receiving Python objects from the broker service. Incoming data is de-serialized from a UTF-8 encoded string 

The device component subscribes and publishes to a single topic. It supports the following parameters:
 - host: name or IP address of the MQTT broker service
 - port: TCP port number of the broker service
 - topic: the name of the topic to subscribe and publish to
 - qos: the quality of service for all outgoing messages (0,1,2)

The example application also contains two additional components: Publisher uses the outgoing interface for periodically broadcasting a measurement value to MQTT, Subscriber receives from the same topic and logs the incoming messages.

## Requirements

The MQTT device component depends on the Eclipse Paho Python Client library. This library is small and ideally could be included as a subdirectory of the device component, however due to current limitations of the `library` primitive, we need to install this dependency explicitly:

	sudo pip3 install paho-mqtt


## Limitations


 - Due to limitations in the device component framework, only one MQTT device driver can be active in the application. Thus, the application is restricted to subscribe and publish to a single MQTT topic.
 - The current implementation builds a reasonable MQTT Client ID during run-time, which cannot be changed or customized.
 - The QoS parameter is specified as a parameter for the device component, thus this cannot be changed on the individual outgoing message level
 - The sending and receiving logic assumes JSON-encoded data. This works in loop-back mode, but might be problematic with arbitrary external sources.

## Testing

Once the application has been launched, you should observe the publisher and subscriber log messages. You need to verify that the subscriber receives the measurements from the publisher (through the MQTT broker).
Also, you can use any MQTT client (suggested: MQTT.fx, a multi-platform client) to observe the messages while the application is running. You need to connect to `iot.eclipse.org`, port 1883 with no authentication and subscribe to the `RIAPS/MQTTExample` topic.

## Developers

 - Peter Volgyesi <peter.volgyesi@gmail.com>
