# Accurate Clock for Distributed Voltage Example

This is a simple application to show a streamlined approach to reading a specific Modbus registers
and report the values back to a python component.

## Developers

 - Istvan Madari <istvan.madari@vanderbilt.edu>

## Software Setup Requirements

This project uses a third party library (libmodbus).  The code provided is the source code used to create the shared library.  Before an application is deployed, both libmodbus must be installed and this software must be compile into a shared library.

### Install libmodbus (Development Machine and BBB)

This library should be installed on the machine where the library will be built and on the BBBs where the
library will be call from the RIAPS Modbus UART shared library.

- To build on the BBBs:

    ```
    git clone https://github.com/cmjones01/libmodbus.git
    sudo apt-get install autoconf libtool pkg-config
    cd libmodbus
    ./autogen.sh
    ./configure
    make

        libmodbus 3.1.2
        ===============
        prefix:                 /usr/local
        sysconfdir:             ${prefix}/etc
        libdir:                 ${exec_prefix}/lib
        includedir:             ${prefix}/include

    sudo make install

    `----------------------------------------------------------------
    Libraries have been installed in:
        /usr/local/lib
    `----------------------------------------------------------------
    ```

- To cross-compile on the development machine, libmodbus needs to be cross compiled on the VM.  
    The above method applies, but use the following configuration statement.

    ```
    ac_cv_func_malloc_0_nonnull=yes ./configure --host=arm-linux-gnueabihf --prefix=/usr/arm-linux-gnueabihf
    ```

> Note: cmjones01 fork was used to allow option for asynchronous operation in the future
- See https://martin-jones.com/2015/12/16/modifying-libmodbus-for-asynchronous-operation/

## Importing C++ Application into Eclipse

The following steps can be used to pull this application into an Eclipse project.  

1) Pull the content of this repository.

2) Create a "C/C++" project from "Existing Code as Makefile Project".

3) Select the application files under the "Cpp" folder in the local copy of the repository, and select "Cross GCC" toolchain for indexer settings.  

5) Create build targets for the armhf architectures (since it will be deployed to a armhf architecture), along with a realclean target.  Default setup works, names typically is all-armhf.  The make commands can be found in the "makefile".

6) For C++ indexing, add include paths to the project properties.  Under "C/C++ General" and then "Paths and Symbols", add the following GNU C++ Includes for this project under the GNU C++:

- /usr/include/python3.6m
- /opt/riaps/amd64/include
- /opt/riaps/amd64/include/pybind11/include
- /<project_name>/include (this is a workspace path and depends on the project name, utilize "Workspace" navigation when adding this directory path)

7) To easily access the RIAPS platform tools from within Eclipse, import the [riaps_ctrl.launch](https://github.com/RIAPS/riaps-pycom/blob/master/bin/riaps_ctrl.launch) and [riaps_deplo.launch](https://github.com/RIAPS/riaps-pycom/blob/master/bin/riaps_deplo.launch) files.  

>Note: Once imported, be sure to uncheck the "Build before launch" flag which is automatically checked under the "Build" tab of each of these imported external tool configurations.

## UART Configuration
* port = 'UART2'
* baud rate = 115200
* 8 bit, parity = None, 1 stopbit   
* timeout = 3 seconds

## Modbus Configuration
* Slave Address:  10 or (0x0A)
* InputRegs (read only)
  - [0]=outputCurrent,
  - [1]=outputVolt,
  - [2]=voltPhase,
  - [3]=time
* For Inverter control:  HoldingRegs (read/write)
  - [0]=unused
  - [1]=startStopCmd
  - [2]=power

## HW Configuration
### Enable UART on the BBB
* Tools used to test UART2:  
  - Terminal tool on the host
  - USB to 3.3 V TTL Cable (TTL-232R-3V3 by FTDI Chip)
    - How to connect with BBB (P9 connector)
      - White (RX) to BBB TX (pin 21),
      - Green (TX) to BBB RX (pin 22),
      - GND on BBB pins 1, 2, 45, 46
    - Cable information from https://www.adafruit.com/product/954?gclid=EAIaIQobChMIlIWZzJvX1QIVlyOBCh3obgJjEAQYASABEgImJfD_BwE

* To turn on the UART2, on the beaglebone, modify /boot/uEnv.txt by uncommenting the following line and adding BB-UART2
(which points to an overlay in /lib/firmware)

   ```
   ###Master Enable
   enable_uboot_overlays=1
   ...
   ###Additional custom capes
   uboot_overlay_addr4=/lib/firmware/BB-UART2-00A0.dtbo
   ```

* Reboot the beaglebone to see the UART2 enabled. UART2 device is setup as ttyO2 (where the fourth letter
is the letter 'O', not zero) that references ttyS2 (a special character files)

* To verify that UART2 is enabled, do the following

   ```
   ls -l /dev/ttyO*

   lrwxrwxrwx 1 root root 5 Mar  6 22:54 /dev/ttyO0 -> ttyS0
   lrwxrwxrwx 1 root root 5 Mar  6 22:54 /dev/ttyO2 -> ttyS2
   ```

If the enabled UART does not show up in the verification step, check that the eMMC bootloader is not blocking the uboot overlay.  

```
   sudo /opt/scripts/tools/version.sh | grep bootloader
```

You might find that the eMMC bootloader is older than 2018 (as shown below).  

```
bootloader:[microSD-(push-button)]:[/dev/mmcblk0]:[U-Boot 2018.09-00002-g0b54a51eee]:[location: dd MBR]
bootloader:[eMMC-(default)]:[/dev/mmcblk1]:[U-Boot 2016.01-00001-g4eb802e]:[location: dd MBR]
```

Then go to [Flasher - eMMC: All BeagleBone Varients with eMMC section of the Ubuntu BeagleBone website](https://elinux.org/BeagleBoardUbuntu) and follow the instructions to update the eMMC bootloader.

### Connecting the BBB to the DSP Modbus UART Connection
* DSP:  C2000(TM) Microcontrollers (TMS320F28377S) LaunchPad Development Kit (LAUNCHXL-F28377S)
* Can buy from Newark (http://www.newark.com/texas-instruments/launchxl-f28377s/dev-board-tms320f28377s-c2000/dp/49Y4795)
  - powered by USB connection
* Code Composer Studio (CCS) by TI used to download software provide by NCSU (source code in library)
* Use CCS to start DSP application

### BBB UART to DSP Modbus Connection
* BBB TX (P9, pin 21) --> DSP RX (J4, pin 37, SCITXDB, GPIO15)
* BBB RX (P9, pin 22) --> DSP TX (J4, pin 38, SCIRXDB, GPIO14)

## Tools used for Debugging Modbus Interface  
* BBB is master, so to debug this interface a slave simulator was used: MODBUS RTU RS-232 PLC
  - Simulator found at www.plcsimulator.org
* DSP is slave, so to debug this interface a master simulator was used: QModMaster 0.4.7
  - libmodbus 3.1.4 found at https://sourceforge.net/projects/qmodmaster
* Modbus Message Parser
  - http://modbus.rapidscada.net/
