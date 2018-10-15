# Microgrid Secondary/Resynchronization Control

When a micorgrid opereates in islanded mode, droop control serving as the primary control will introduce frequency and voltage maginitude deviations. The microgrid secondary/resynchronization control application is used to restore the microgrid frequency and voltage maginidue to their nominal values and synchronize the phase of microgrid to the main grid.


## Application Configuration

A microgrid with four DGs is simulated in the OPAL-RT simulator.

Each simulated DG is controlled by a TI TMS320F28377S DSP.

In the RIAPS application, 5 RIAPS nodes are required. They are:
 - one OPAL IO RIAPS node to receive C37.118 messages from OPAL-RT simulator,
 - four DG RIAPS nodes to implement secondary/resynchronization control algorithm proposed in [2].
 
 
## Application Description

The microgrid voltage and main grid voltage are measured in the simulation. The phase angle difference and magnitude difference are calculated in the simulation and sent out to the OPAL IO RIAPS node via C37.118 messages. They are required by the secondary/resynchronization control and they are sent to the voltage regulaton DG.

The OPAL IO RIAPS node is also used to issue commands from the RT-LAB interface to the RIAPS nodes. The commands and the phase angle difference and magnitude difference are grouped in the same C37.118 message.

In the application, DG 2 with IP address 192.168.10.112 is selected as the voltage regulaton DG. It is resposible to regulate the phase angle difference and voltage magnitude difference at the point of interconnection (POI). DGs can communicate with each other to maintain proportional active and reactive power sharing. Different communication topologies can be simulated by configuring the message handler in the application. After the each node calculates the secondary control command, the command is sent to the TI DSP TMS320F28377S via a modbus message. 

The DSPs use the secondary control command to change their droop setpoints. They also send meassurement data such frequency, active power output, and reactive power output back to DG RIAPS nodes via modbus messages.

More detail information can be found in [2].


## Reference
[1] Y. Du, H. Tu, S. Lukic, D. Lubkeman, A. Dubey, and G. Karsai, “Implementation of a distributed microgrid controller on the resilient information architecture platform for smart systems (riaps),” in Power Symposium (NAPS), 2017 North American. IEEE, 2017, pp. 1–6.

[2] Y. Du, H. Tu, and S. Lukic, “Distributed control strategy to achieve synchronized operation of an islanded mg,” IEEE Transactions on Smart Grid, pp. 1–1, 2018.

[3] Laszka, A., Dubey, A., Eisele, S., Walker, M., & Kvaternik, K. Design and Implementation of Safe and Private Forward-Trading Platform for IoT-Based Transactive Microgrids.

[4] H. Tu, Y. Du, H. Yu, S. Lukic, P. Volgyesi, M. Metelko, A. Dubey, and G. Karsai, “An adaptive interleaving algorithm for multi-converter systems,” in 2018 9th IEEE International Symposium on Power Electronicsfor Distributed Generation Systems (PEDG). IEEE, 2018, pp. 1–7.
