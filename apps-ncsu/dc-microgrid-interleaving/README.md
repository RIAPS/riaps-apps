# DC Microgrid Interleaving

In a DC microgrid, DC sources such as PVs and batteries are coupled to a single DC bus via their converters. If the converters have the same switching frequency and can be properly interleaved, the current and voltage ripple on DC bus can be reduced which can help reduce  the DC bus capacitor size and extend its life time. This application achieves the interleaving of different converters by 

1. implementing the interleaving algorithm in a standard RIAPS application; 
2. synchcronizing different DSPs by RIAPS synchronization service.


## Application Configuration

A DC microgrid with four DGs is simulated in the OPAL-RT simulator.

Each DG is a boost converter and is controlled by a TI TMS320F28377S DSP.

In the RIAPS application, four RIAPS nodes are required. They are:

 - four DG RIAPS nodes to implement interleaving algorithm proposed in [4].
 
 
## Application Description

In the application, DGs can communicate with each other to exchange their current vector information. As the interleaving algorithm requires each converter's information to be global, communication channel exists between any two DGs. After DG RIAPS node calculates the interleaving phase shift, it is sent the TI DSP TMS320F28377S via a modbus message.

The RIAPS node provides a high precision synchronization pulse to the DSP. When receiving the synchronization pulse, the DSPs regulate its carrier phase by tuning the carrier frequency slightly around its nominal value to avoid abrupt change of duty cycle during synchronization event. The DSPs also send necessary meassurement data such current vector to DG RIAPS nodes via modbus messages.

More detail information can be found in [4].


## Reference
[1] Y. Du, H. Tu, S. Lukic, D. Lubkeman, A. Dubey, and G. Karsai, “Implementation of a distributed microgrid controller on the resilient information architecture platform for smart systems (riaps),” in Power Symposium (NAPS), 2017 North American. IEEE, 2017, pp. 1–6.

[2] Y. Du, H. Tu, and S. Lukic, “Distributed control strategy to achieve synchronized operation of an islanded mg,” IEEE Transactions on Smart Grid, pp. 1–1, 2018.

[3] Laszka, A., Dubey, A., Eisele, S., Walker, M., & Kvaternik, K. Design and Implementation of Safe and Private Forward-Trading Platform for IoT-Based Transactive Microgrids.

[4] H. Tu, Y. Du, H. Yu, S. Lukic, P. Volgyesi, M. Metelko, A. Dubey, and G. Karsai, “An adaptive interleaving algorithm for multi-converter systems,” in 2018 9th IEEE International Symposium on Power Electronicsfor Distributed Generation Systems (PEDG). IEEE, 2018, pp. 1–7.
