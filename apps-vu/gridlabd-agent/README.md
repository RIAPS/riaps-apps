# Gridlab-D agent

A simple agent to run Gridlab-D simulations (under fncs control).

## Developer

- Purboday Ghosh, Vanderbilt University

## Installation

1. Install RIAPS.

2. Install Gridlab-D. For FNCS to work the specific branch containing FNCS support needs to be installed.

3. Install FNCS. Specify the location of the ZeroMQ and CZMQ installation paths using *--prefix* flag.

## Package Description

- The gla package contains the code of the agent, to be started by the riaps_gla.py script.
The script takes 1 argument: the base name of the model file, and it has to be run
in a folder which contains that model file and other files for configuring the agent.

- The models folder has a folder with and example called loadshed_multi - these files are needed
to run the agent. The files have follow the naming convention (basename + {.glm,.gll,.yaml,})
which are the problem-specific files plus a file called gla.yaml for global settings. The glm file is the Gridlab-D model definition, the gll file specifies which of the values that are subscribed will be sent to influxdb to be logged and the yaml file specifies configuration options like the simulation time-step and what values are published/subscribed.

- The riaps folder contains the RIAPS application related files. It consists of a Controller component that controls one of the 32 switches in the network. The interfacing with Gridlab-D through FNCS is handled by a special device component GridlabD.

## Operation

The agent launches the simulator and acts as a broker for clients that can

(1) subscribe to selected messages (that are published by the simulation model)

(2) publish messages that make changes to the simulation model during execution.

(3) The RIAPS Controller components (one for each switch) subscribe to the Distribution load of the substation and determine the switch status (On or Off) and publishes it back to the simulation.

>*Pre-requisite*: the rpyc_registry must be running so that the client(s) can connect to the agent.
