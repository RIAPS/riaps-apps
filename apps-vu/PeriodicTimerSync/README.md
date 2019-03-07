# Periodic Timer Synchronization

Periodic timers start after the component thread is initialized, an action which is not synchronized in the RIAPS deployment 
process. This application shows a solution to starting periodic timers in sync across a RIAPS application using only a sporadic 
timer. 

`TimerComp.py` works in this manner:

1) The component thread is initialized in an `INIT` state, starting the periodic timer in an unsynchronized manner.
2) After one period, the periodic timer fires. In the `INIT` state, the handler calculates the amount of time until the next 10th 
second of UNIX time begins *and* the periodic timer has fully elapsed and reached an inactive state. The sporadic timer is started
with the calculated delay, the periodic timer halted, and the component set to a `SYNC` state.
3) The sporadic timer fires. As this event was calculated to happen at the next 10th second of UNIX time, this firing of sporadic 
timers is synchronized across all RIAPS nodes. The periodic timer is restarted and the app set to a `RUNNING` state.
4) The periodic timers have now been started in a synchronized fashion, and actions performed in the `RUNNING` state will be 
performed roughly in sync.

## Requirements
The synchronization is based on reads of the local system clock, so all system clocks should be synchronized with 
[RIAPS-timesync](https://github.com/RIAPS/riaps-timesync), which is included with the default RIAPS image. As long as timesync
is running, any role will do fine. If you want to run a node in `slave` mode, make sure you have one node in the same network run as `master`.

## Limitations

- This only performs a single synchronization step, starting all periodic timers at the same time. It doesn't do anything to keep 
the periodic timers from drifting apart the longer the app is run.
- If separate component threads are initialized in different 10s quanta of UNIX time, components starting in an earlier 10s 
interval will synchronize to a different point in UNIX time and start earlier. For example, a component that was initialized at 
5:00:37 will wait until 5:00:40 to start its periodic timer, but a component within the same application that happened to 
initialize at 5:00:41 will wait until 5:00:50.

## Developers
- Tim Krentz <tim.krentz@vanderbilt.edu>

