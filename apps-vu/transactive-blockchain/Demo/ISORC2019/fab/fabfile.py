#!/usr/bin/python3
import fabric.api as fabi
from config10_node import *

fabi.env.password=PASS
fabi.env.user=USER
fabi.env.key_filename = SSHKEY
fabi.env.port=SSHPORT

fabi.env.skip_bad_hosts = True
fabi.env.warn_only = True

@fabi.task
def runCommand(command):
    """run with fab -R '<role to run command on, e.g c2_1>' runCommand:<command to run>
    or to run on a specific host: fab -H '10.0.2.194:2222' runCommand:'hostname'"""
    results = ''
    with fabi.hide('output', 'running', 'warnings', 'aborts'), fabi.settings(warn_only=True):
        results = fabi.run(command)
    print(results)
    return(results)


@fabi.task
@fabi.parallel
def prunCommand(command):
    """run with fab -R '<role to run command on, e.g c2_1>' runCommand:<command to run>
    or to run on a specific host: fab -H '10.0.2.194:2222' runCommand:'hostname'"""
    results = ''
    with fabi.hide('output', 'running', 'warnings', 'aborts'), fabi.settings(warn_only=True):
        results = fabi.run(command)
    print(results)
    return(results)

@fabi.task
def put(src,dst):
	fabi.put(src, dst, use_sudo=True)


@fabi.task
def kill(app_name):
    """kill RIAPS functions and application on hosts"""
    pgrepResult = fabi.run('pgrep \'riaps_\' -l')
    pgrepEntries = pgrepResult.rsplit('\n')
    processList = []

    if pgrepResult:
        for process in pgrepEntries:
            processList.append(process.split()[1])

    if processList:
        for process in processList:
            fabi.sudo('pkill -SIGKILL '+process,combine_stderr=True,warn_only=True)

    hostname = fabi.run('hostname')
    if hostname[0:3] == 'bbb':
        host_last_4 = hostname[-4:]
    # If it doesn't start with bbb, assume it is a development VM
    else:
        vm_mac = fabi.run('ip link show enp0s3 | awk \'/ether/ {print $2}\'')
        host_last_4 = vm_mac[-5:-3] + vm_mac[-2:]

    fabi.sudo('rm -R /home/riaps/riaps_apps/riaps-apps.lmdb/')
    fabi.sudo('rm -R /home/riaps/riaps_apps/'+app_name+'/')
    fabi.sudo('rm -R /home/riaps/riaps_apps/'+app_name+'*')
    fabi.sudo('userdel ' + app_name.lower() + host_last_4)


@fabi.task
@fabi.parallel
def pkill(app_name):
    """kill RIAPS functions and application on hosts"""
    pgrepResult = fabi.run('pgrep \'riaps_\' -l')
    pgrepEntries = pgrepResult.rsplit('\n')
    processList = []

    if pgrepResult:
        for process in pgrepEntries:
            processList.append(process.split()[1])

    if processList:
        for process in processList:
            fabi.sudo('pkill -SIGKILL '+process,combine_stderr=True,warn_only=True)

    hostname = fabi.run('hostname')
    if hostname[0:3] == 'bbb':
        host_last_4 = hostname[-4:]
    # If it doesn't start with bbb, assume it is a development VM
    else:
        vm_mac = fabi.run('ip link show enp0s3 | awk \'/ether/ {print $2}\'')
        host_last_4 = vm_mac[-5:-3] + vm_mac[-2:]

    fabi.sudo('rm -R /home/riaps/riaps_apps/riaps-apps.lmdb/')
    fabi.sudo('rm -R /home/riaps/riaps_apps/'+app_name+'/')
    fabi.sudo('rm -R /home/riaps/riaps_apps/'+app_name+'*')
    fabi.sudo('userdel ' + app_name.lower() + host_last_4)

@fabi.task
@fabi.parallel
def restartDeplo():
    """restart the deplo background service on hosts"""
    fabi.sudo('systemctl restart riaps-deplo.service')
