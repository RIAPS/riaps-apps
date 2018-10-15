# RIAPS Applications Developed by North Carolina State University

This is a collection of applications used for microgrid control. The six major applications are:

1. ac-microgrid-resync: This application is for microgrid resynchronization. It uses the RIAPS platform as a simple communication tool for receving and forwarding C37.118 messages from SEL relay and to Opal-RT simulator. No control algortihm is implemented on the RIAPS platform. All the control algorithms, including power electronics inverter control and microgrid secondary/resynchronziation control, are implemented in Opal-RT simulator. This application was demonstrated at the 2017 ARPA-E Energy Innovation Summit.  

2. ac-microgrid-resync-availability: This application is similar to microgrid-resync. It is augumented with an availability check function to select the available DG to act as microgrid resynchronization DG. More details about the availability check can be found in [1].

3. **ac-microgrid-resync-dsp**: This application is for microgrid synchronization. Compared to microgrid-resync, several major changes have been made:
      - The inverter control algorithms, including inner current loop, outer voltage loop, and droop loop are implemented in the DSP TMS320F28377S from Texas Instruments.
      - A distributed microgrid secondary/resynchronziation control algorithm is used [2].
      - The secondary/resynchronziation control algorithm is implemented on RIAPS platform.

   This application was demonstrated at the 2018 ARPA-E Energy Innovation Summit.
 
4. **ac-microgrid-resync-dsp-RelayInOpal**: This applicaion is the same as **ac-microgrid-resync-dsp** except the relay is simulated in Opal-RT simulator. The demonstration can run without a SEL relay.
 
5. **ac-microgrid-transactive-energy-in-grid-tied**: This application is for microgrid transactive energy trading under grid-tied mode. For detail about the transactive part can be found in [3]. 


6. **dc-microgrid-interleaving**: This application is for interleaving the DC/DC converters in a DC microgrid. More details can be found in [4].


The up-to-date applications are marked as **bold**.


## Developers

- Hao Tu, FREEDM Systems Center, North Carolina State University, Raleigh
- Yuhua Du, FREEDM Systems Center, North Carolina State University, Raleigh
- Rishabh Jain, FREEDM Systems Center, North Carolina State University, Raleigh
- Srdjan Lukic, FREEDM Systems Center, North Carolina State University, Raleigh
- David Lubkeman, FREEDM Systems Center, North Carolina State University, Raleigh

If you have any question, please contact htu@ncsu.edu or ydu7@ncsu.edu.

## Reference
[1] Y.  Du,  H.  Tu,  S.  Lukic,  D.  Lubkeman,  A.  Dubey,  and  G.  Karsai,“Implementation  of  a  distributed  microgrid  controller  on  the  resilient information  architecture  platform  for  smart  systems  (riaps),”  in Power Symposium (NAPS), 2017 North American. IEEE, 2017, pp. 1–6.

[2] Y.  Du,  H.  Tu,  and  S.  Lukic,  “Distributed  control  strategy  to  achieve synchronized operation of an islanded mg,” IEEE Transactions on Smart Grid, pp. 1–1, 2018.

[3] Laszka, A., Dubey, A., Eisele, S., Walker, M., & Kvaternik, K. Design and Implementation of Safe and Private Forward-Trading Platform for IoT-Based Transactive Microgrids.

[4] H. Tu, Y. Du, H. Yu, S. Lukic, P. Volgyesi, M. Metelko, A. Dubey, and G. Karsai, “An adaptive interleaving algorithm for multi-converter systems,” in 2018 9th IEEE International Symposium on Power Electronicsfor Distributed Generation Systems (PEDG). IEEE, 2018, pp. 1–7.

## Acknowledgment

The information, data or work presented herein was funded in part by the
Advanced Research Projects Agency - Energy (ARPA-E), U.S. Department of Energy, under
Award Number DE-AR0000666. The views and opinions of the authors expressed herein do
not necessarily state or reflect those of the United States Government or any agency thereof.
