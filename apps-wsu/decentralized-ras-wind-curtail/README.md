# Decentralized Remedial Action Scheme (RAS) for Wind Curtailment

This application uses linear optimization to detect and curtail overloads in an IEEE 14-bus system with wind power. The application is fault tolerant and will work as long as either the leader or backup node is running.

## Developers

- Vignesh Venkata Gopala Krishnan - v.venkatagopalakris@wsu.edu
- Alex Askerman - alexanderask2@gmail.com
- Ren Liu - liuren248@gmail.com
- Shyam Gopal - shyam.gopal@wsu.edu

## Installation

Hardware used:
  1. 3 BBBs
  2. RTDS
  3. 1 SEL Hardware PMU

This application works with RTDS and a combination of hardware and software PMUs. The setup consists of three software PMUs and one hardware PMU. The RIAPS nodes, RTDS, hardware and software PMUs are on the same network and are connected through ethernet. The IEEE C37.118 protocol is used to communicate with the PMUs. 

SciPy must be installed on the all nodes to run the application.  NumPy is a dependency of SciPy and will also be installed.

```
sudo pip3 install scipy
```

or

```
sudo apt-get install python3-numpy python3-scipy
```


Python's xlrd module must be installed on the Leader and Backup nodes. This module is used to read the "Demo.xlsx" file which contains information required to run the linear optimization.

```
sudo pip3 install xlrd
```

The "Variable.xlsx" file contains values required for computation. This file must be copied to all nodes for the application to work. The values in each table are as follows: H is the power injection bus. B is the imaginary part of the Nodal admittance matrix. C is the system connection matrix. bb is the line rating on each transmission line.

## Running the Application

  1. Run the VM and open 6 terminals.
  2. Start rpyc_registry.py in the first terminal
  3. Start riaps_ctrl in the second terminal. The RIAPS GUI should start.
  4. Copy the Variable.xlsx file and the extracted pypmu folder to the $RIAPS_APPS/DRAS directory in all nodes.
  5. start riaps_deplo on the VM.
  6. In terminals 4, 5, and 6, ssh to the BBBs and start riaps_deplo
  7. Start the simulation and open a listening port on RTDS.
  8. Load the dras.riaps and dras.depl files in riaps_ctrl and deploy the application.
 
 You should see:
  1. All nodes receive some communication from RTDS and performs some calculations. Intermediate results are logged on screen.
  2. The node with group_no = 1 should display the result of the calculation.
  3. In case of an overload, the application should detect and mitigate the overload.
