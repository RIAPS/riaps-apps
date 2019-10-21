# Blockchain based Energy Trading Market

<Place a short description of your application>
 
 This application is a simulation of a set of 10 traders which post offers to produce or consume energy in future intervals. The values of the offers are drawn from static traces stored as CSV files, and specify the intervals for which the offer is valid. An interval is a time period of 15 minutes, but is represented by 2 minutes of simulation time. The offers are posted to a private ethereum blockchain. The posted offers broadcast are then matched using the CPLEX MILP solver which in turn posts the solution back to the blockchain, which notifies the traders of their respective energy responsibilities. 


Some demo and presentation videos may be found here: https://www.youtube.com/playlist?list=PLZ5EcK0kbWDwzZ6fab0bFwE26EIlt3A1M

A paper related to this work may be found here: http://www.isis.vanderbilt.edu/node/4868

## Developers

This application was developed by Scott Eisele, Vanderbilt University in collaboration with Aron Laszka, University of Houston, Abhishek Dubey, Vanderbilt University and Karla Kvaternik, Siemens, CT under partial sponsorship from Siemens, CT, Princeton NJ.


## Application Setup
This README assumes that the RIAPS platform is installed and there is ssh access to all nodes. 

Clone the repository
 * git clone https://github.com/RIAPS/riaps-apps.git
 
In the repository this application is at
`riaps-apps/apps-vu/transactive-blockchain/`
From this point on we assume this is the starting directory. 

* In `Demo/.env` set `DIR` and `PROJECT` to reflect the install location of this application.

### Set parameters

* ```Demo/cli/TransactiveEnergy.depl``` Specify which nodes will host which actors

The environment variablels are set in `Demo/.env`. If using eclipse files beginning with `.` are hidden. To make them visible do `Project Explorer -> View -> Filers -> uncheck .’* resources’`

* In `Demo/.env` Match `SOLVER`, `MINER`,`CTRL`, `DSO`, `RECORDER`, `T101`, and `T106` with TransactiveEnergy.depl. 
* Rename `.sysenv` in `Demo` to `.myenv`, to prevent accidental upload to git and since `.env` expects it to be called that. It is used for the launch script to work and is intended for private environment variables. 

## Install App Dependencies
To facilitate setup this command can be used to execute the setup commands listed below simultaneously on all nodes :
  * ensure `BBBs` in `Demo/.env` and all variables in `Demo/.myenv` are up to date with your system.
  * `cd Demo/fab`
  * `fab -R ALL runCommand:"<cmd>`
  
Example: `Demo/fab$ fab -R ALL runCommand:"sudo apt install tmux"`
  
To excute on only the BBB's replace `ALL` with `BBBs`.

To excute on only the CTRL node replace `ALL` with `CTRL`

### All Nodes (may require sudo)
* `apt install tmux`
* `pip3 install python-dotenv`
* `apt-get install libcurl4-openssl-dev`
* `pip3 install pycurl`
* `pip3 install influxdb`
* All nodes should have UTC as the timezone. If not
  * `sudo timedatectl set-timezone UTC`
### Control Node
* Install 64 bit Geth version 1.7.0
  * https://github.com/ethereum/go-ethereum/wiki/Installing-Geth#download-standalone-bundle
    * https://gethstore.blob.core.windows.net/builds/geth-linux-amd64-1.7.0-6c6c7b2a.tar.gz
  * set `GETH` and `GETHEXE` in `Demo/.env` corresponding to the location of the bundle.
  * Add `genesis-data.json` and `password.txt` from `miner` folder into the standalone bundle folder`GETH`(specified in `Demo/.env`)
This application was devloped and tested with the version 1.7.0 of the standalone bundle, other options could be made to work but may require some modification to the launch script, as well as the python rpc client.
* Install CPLEX
  * https://ibm.onthehub.com/WebStore/ProductSearchOfferingList.aspx?srch=ilog%20cplex
  * setup python api
    * https://www.ibm.com/support/knowledgecenter/SSSA5P_12.7.0/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html
  
There is a free edition of CPLEX, however with the current app configuration the optimization problem becomes too complex for that license. It is likely possible to simplify the problem to make it work but it has only been fully tested with the full version of CPLEX which has a complementary edition for academics. 
      
* Install grafana on control node
  * http://docs.grafana.org/installation/debian/#apt-repository
  * In dashboard set timezone to UTC 
  * A dashboard that can be imported from the dashboard can be found in `transactive-blockchain/Grafana-dashboard`
* Install influxDB server of control node
  * https://docs.influxdata.com/influxdb/v1.6/introduction/installation/
  * set `INFLUX_DBASE_HOST` in `Demo/.env`
  * verify that the influxdb is running `systemctl status influxd.service`
* `pip3 install 'fabric<2.0`
* `pip3 install scipy`

run `$ ./pack.sh` which is in `Demo/cli` after updating to update the files that will be sent to remote nodes. 

## Running the Application

```shell
$ cd Demo
$ source ./tmux-launch.sh
```
This will start a tmux session with a window with panes for 1) running the riaps ctrl gui, 2) running the miner, 3) running the recorder, and a window for 1) Running the Solver, 2) Running the DSO, 3 and 4) Running two traders.

Switch between windows with `ctrl-b` then press `p` for previous.
Switch between panes with `ctrl-b` then press an arrow key to move to that pane. 

If the nodes have not been accessed with ssh previously they will request to be added to known hosts and the application will need to be reset and re-run.

In the control gui, click the folder icon, press enter.
Click the 'Model' button. Select the .json filetype from the dropdown in the lower right. Select TransactiveEnergy.json.
Click the 'Depl' button. Select the .json filetype from the dropdown in the lower right.  TransactiveEnergy-deplo.json.
Click the 'Deploy' button.
Click the new 'TransactiveEnergy' button. Click 'Launch'

The app can take approximately 90 seconds to deploy.


Logs for each actor are on the respective host at `/tmp/<actorName>/log`.

Additional logging for the platform can be viewed by running `sudo journalctl -f -u riaps-deplo.service --since "10 min ago"` on the node of interest.

## Stopping the Application

```shell
$ cd Demo
$./resetDemo.sh
```
This kills and removes everything

## Modifying the application to set the resource constraints.

```shell
$ cd Demo/cli
```
update `TransactiveEnergy.riaps` to apply resource constraints.

run `Demo/cli$ ./pack.sh` to run the interpreter and put the json in `Demo/pkg`.
