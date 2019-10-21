'''
Deployment manager service main class
Created on Oct 19, 2016

@author: riaps
'''

import os,signal
import sys
import errno
import time
import json
import hashlib
from os.path import join
from collections import namedtuple
import subprocess
import threading
import logging
import traceback
import psutil
import pwd
import functools
import tarfile
import yaml

import capnp
from concurrent.futures.thread import ThreadPoolExecutor
from _thread import RLock

import zmq
from zmq import devices

try:
    import cPickle
    pickle = cPickle
except:
    cPickle = None
    import pickle

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from riaps.consts.defs import *
from riaps.utils.sudo import is_su
from riaps.utils.config import Config
from riaps.proto import deplo_capnp
from riaps.proto import disco_capnp
from riaps.run.exc import BuildError
from riaps.deplo.resm import ResourceManager
from riaps.deplo.procm import ProcessManager
from riaps.deplo.appdb import AppDbase
from riaps.utils.names import *

# Record of the app
DeploAppRecord = namedtuple('DeploAppRecord', 'model hash file home')
# Record of a user
DeploUserRecord = namedtuple('DeploUserRecord', 'name home uid gid')
# Record of an actor
DeploActorRecord = namedtuple('DeploActorRecord', 'app model actor args device control monitor')
# Record of an device actor
DeviceActorRecord = namedtuple('DeviceActorRecord', 'app model actor args device control monitor')
# Record of an app actor command 
DeploActorCommand = namedtuple('DeploActorCommand', 'app model actor args cmd pid')
# Record of the disco command
DeploDiscoCommand = namedtuple('DeploDiscoCommand', 'cmd pid')

class DeploymentManager(threading.Thread):
    '''
    Deployment manager service main class, implemented as a thread 
    '''    
    DISCONAME = 'riaps.disco'
    
    def __init__(self,parent,resm,fm):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.context = parent.context
        self.hostAddress = parent.hostAddress
        self.macAddress = parent.macAddress
        self.suffix = self.macAddress
        self.riapsApps = parent.riapsApps
        self.riapsHome = parent.riapsHome
        self.launchMap = { }            # Map of launched actors
        self.launchRefs = { }           # Reference count for device actors
        self.mapLock = RLock()          # Lock to protect launchMap
        self.discoLock = RLock()        # Lock to protect disco 
        self.disco = None
        self.dbaseHost = None 
        self.dbasePort = None
        self.fm = fm                    # Fault manager
        self.resm = resm                # Resource manager
        self.procm = ProcessManager(self)
        # self.devm.setProcessManager(self.procm)
        self.appModels = { }            # App models loaded
        self.users = { } 
        self.setupUser(Config.TARGET_USER)
        self.appUser = { }
        self.actors = { }       # Actors started
        self.peerQueue = { }    # Peer messages for actors
        self.devices = { }      # Device actors started
        self.monitors = { }     # Monitors of actor messages
        self.poller = None

        self.riaps_actor_file = 'riaps_actor'   # Default name for the executable riaps actor shell
        try:
            import riaps.riaps_actor            # Try to import the python riaps_actor first so that we know is correct file name
            self.riaps_actor_file = riaps.riaps_actor.__file__
        except:
            pass
        
        self.riaps_device_file = 'riaps_device'       # Default name for the executable riaps device shell
        try:
            import riaps.riaps_device          # We try to import the python riaps_device first so that we know is correct file name
            self.riaps_device_file = riaps.riaps_device.__file__
        except:
            pass       
        
        self.riaps_disco_file = 'riaps_disco'   # Default name for the executable riaps disco 
        try:
            import riaps.riaps_disco            # Try to import the python riaps_disco first so that we know is correct file name
            self.riaps_disco_file = riaps.riaps_disco.__file__
        except:
            pass
        
        self.riaps_device_file = 'riaps_device'       # Default name for the executable riaps device shell
        try:
            import riaps.riaps_device          # We try to import the python riaps_device first so that we know is correct file name
            self.riaps_device_file = riaps.riaps_device.__file__
        except:
            pass
        
        self.depmCommandEndpoint = parent.depmCommandEndpoint
        # self.devmCommandEndpoint = parent.devmCommandEndpoint
        self.procMonEndpoint = parent.procMonEndpoint
        
        self.command = self.context.socket(zmq.PAIR)        # Socket to recv commands from main
        self.command.setsockopt(zmq.RCVTIMEO,const.depmRecvTimeout)
        self.command.bind(self.depmCommandEndpoint)
        
        self.discoCommand = None
        
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.appDbase = AppDbase()
        self.is_su = is_su()
        self.uuid = None
        self.started = False
        self.pendingCall = False

    def doCommand(self,cmd):
        self.logger.info("doCommand: %s" % str(cmd))
        self.command.send_pyobj(cmd)
    
    def callCommand(self,cmd):
        self.logger.info("callCommand: %s" % str(cmd))
        if self.pendingCall == False:
            self.command.send_pyobj(cmd)
            self.pendingCall = True
        reply = None
        while True:
            try:
                reply = self.command.recv_pyobj()
                self.pendingCall = False
                break
            except zmq.error.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    continue
                else:
                    raise
        return reply
        
    def setupUser(self,user_name):
        if user_name in self.users: return
        pw_record = pwd.getpwnam(user_name)
        user_record = DeploUserRecord(
                    name = pw_record.pw_name, 
                    home = pw_record.pw_dir, 
                    uid = pw_record.pw_uid, 
                    gid = pw_record.pw_gid)
        self.users[user_name] = user_record
        
    def delUser(self,user_name):
        if user_name == Config.TARGET_USER: return
        if user_name not in self.users: return
        del self.users[user_name]
    
    def makeLdLibEnv(self,os_env,libs=[]):
        if libs != []:
            ld_libs = os.getenv('LD_LIBRARY_PATH')
            if ld_libs != None:
                ld_libs += ':' + ':'.join(str(l) for l in libs)
            else:
                ld_libs = ':'.join(str(l) for l in libs)
            os_env['LD_LIBRARY_PATH'] = ld_libs
        
    def makeUserEnv(self,user_name,ld_libs=[]):
        user_env = os.environ.copy()
        user_record = self.users[user_name]
        user_env[ 'HOME'     ]  = user_record.home
        user_env[ 'LOGNAME'  ]  = user_record.name
        user_env[ 'PWD'      ]  = os.getcwd()
        user_env[ 'USER'     ]  = user_record.name
        if ld_libs != []:
            self.makeLdLibEnv(user_env,ld_libs)
        return user_env

    @staticmethod
    def demote(user_uid,user_gid,is_su):
        def result():
            if is_su:
                os.setgid(user_gid)
                os.setuid(user_uid)
        return result
    

    def connectDisco(self):        
        self.discoCommand = self.context.socket(zmq.REQ)           # Socket to command disco
        self.discoCommand.setsockopt(zmq.RCVTIMEO,const.discoEndpointRecvTimeout)
        self.discoCommand.setsockopt(zmq.SNDTIMEO,const.discoEndpointSendTimeout)
        self.discoCommand.connect(const.discoEndpoint)
        
    def startDisco(self):
        '''
        Start the Discovery Service process 
        '''
        self.logger.info("starting disco")
        disco_prog = 'riaps_disco'
        disco_mod = self.riaps_disco_file   # File name for python script riaps_disco.py

        disco_arg1 = '--database'
        disco_arg2 = '%s:%s' % (self.dbaseHost,self.dbasePort)
        user_record = self.users[Config.TARGET_USER]
        user_env = self.makeUserEnv(Config.TARGET_USER)
        user_uid = user_record.uid
        user_gid = user_record.gid
        user_cwd = os.getcwd()
        command = [disco_prog,disco_arg1,disco_arg2]
        try:
            self.disco = psutil.Popen(command,
                                      preexec_fn=self.demote(user_uid, user_gid,self.is_su), 
                                      cwd=user_cwd, env=user_env)
    
        except FileNotFoundError:
            try:
                command = ['python3',disco_mod] + command[1:]
                self.disco = psutil.Popen(command,
                                          preexec_fn=DeploymentManager.demote(user_uid, user_gid,self.is_su), 
                                          cwd=user_cwd, env=user_env)    
            except:
                self.logger.error("Error while starting disco: %s" % sys.exc_info()[0])
                raise
        self.procm.monitor(self.DISCONAME,self.disco)
        self.connectDisco()
        proc = self.disco
        pid = proc.pid
        cmdline = [p.info for p in psutil.process_iter(attrs=['pid','cmdline'])
                   if pid == p.info['pid']][0]['cmdline']
        self.appDbase.setDiscoCommand(DeploDiscoCommand(cmd=cmdline,pid=pid))
        self.logger.info("disco started")


    def setupDisco(self,msg):
        assert type(msg) == tuple and len(msg) == 2
        self.dbaseHost, self.dbasePort = msg
        if self.disco == None:
            self.appDbase.setDisco(msg)
            self.startDisco()
        else:
            self.logger.info('disco already started')
            self.connectDisco()
            pass
    
    
    def setupApp(self,msg):
        ''' Set up model and unique user name for app'''
        assert type(msg) == tuple and len(msg) == 2
        
        appName,appModelName = msg
        appFolder = join(self.riapsApps, appName)
        appModelPath = join(appFolder, appModelName)
        
        if not os.path.isdir(appFolder):
            raise BuildError('app folder is missing: %s' % appFolder)
        
        # Load the app model
        self.loadModel(appName,appModelPath)
        # Make it unique (to last 4 digits of suffix)
        userName = appName.lower() + self.suffix[-4:]  
        # self.appUser[appName] = userName
        self.fm.setupApp(appName,appFolder)
        self.resm.setupApp(appName,appFolder,userName)  # Adds user 
        userName = self.resm.getUserName(appName)       # resm may revert to default user
        self.appUser[appName] = userName
        self.setupUser(userName)
        self.appDbase.addApp(appName)
        
    def verifyPackage(self,keyName,sigName,dataName):
        with open(keyName, 'rb') as f: key = f.read()
        with open(sigName,'rb') as f: sig = f.read()
        with open(dataName, 'rb') as f: data = f.read()
        rsakey = RSA.importKey(key)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(data)
        return signer.verify(digest, sig)
    
    def installPackage(self,msg):
        '''
        Install a downloaded app package
        '''
        assert type(msg) == tuple and len(msg) == 1
        (appName,) = msg
        res = None
        try:
            tgz_file = join(self.riapsApps,appName + '.tgz')
            sha_file = tgz_file + '.sha256'
            #rsa_public_key = join(self.riapsHome,"keys/" + str(const.ctrlPublicKey))
            #res = self.verifyPackage(rsa_public_key,sha_file,tgz_file)
        except:
            return "Error while verifying app '%s'" % appName
        
        #if not res:
        #    return '%s:Signature verification failed' % appName
    
        try:
            with tarfile.open(tgz_file, "r:gz") as tar:
                tar.extractall(self.riapsApps+'/')
        except:
            return 'Content extraction failed' 

        try:
            os.remove(tgz_file)
            os.remove(sha_file)
        except:
            return 'App package removal failed'
        
        return True
    
    def installApp(self,msg):
        reply = self.installPackage(msg)
        self.ctrl.send_pyobj(reply)
        
    def cleanupApp(self,msg):
        ''' Clean up everything related to an app'''
        assert type(msg) == tuple and len(msg) == 1
        (appName,) = msg
        if appName not in self.appModels:
            return
        del self.appModels[appName]
        self.resm.cleanupApp(appName)
        self.fm.cleanupApp(appName)
        self.appDbase.delApp(appName)
        if appName not in self.appUser:
            return
        userName = self.appUser[appName]
        del self.appUser[appName]
        self.delUser(userName)
    
    def cleanupApps(self,msg):
        ''' Clean up all known apps '''
        assert type(msg) == tuple and len(msg) == 0
        for k in self.appModels.keys():
            del self.appModels[k]
            self.appDbase.delApp(k)
        self.resm.cleanupApps()
        self.fm.cleanupApps()
                
    def loadModel(self,appName,modelFileName):
        try:
            fp = open(modelFileName, 'rb')  
        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            raise
        except:
            self.logger.error("Unexpected error:", sys.exc_info()[0])
            raise
        # Check if the app model is already loaded
        _fileHash = 0
        fileData = fp.read()
        fileHash = hashlib.md5(fileData).digest()
        fp.close()
        if appName in self.appModels:   # There is an app with this name
            appRecord = self.appModels[appName]
            appHash = appRecord.hash
            if fileHash == appHash:     # Hash is the same, we have the model loaded
                return
        else:
            pass 
        # Not loaded yet (or new)
        fp = open(modelFileName, 'r')  
        try:
            model = json.load(fp)
        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            raise
        except:
            self.logger.error("Unexpected error:", sys.exc_info()[0])
            raise
        home = ''
        try:
            with open(os.path.join(os.path.dirname(modelFileName),const.sigFile),'r') as f:
                org = yaml.load(f)
                home = org.home
        except:
            pass
        self.appModels[appName] = DeploAppRecord(hash=fileHash, model=model, file=modelFileName, home=home)
        fp.close()
    
    def getAppRecord(self,appName):
        if appName not in self.appModels:
            raise BuildError('App "%s" unknown' % appName)
        return self.appModels[appName]
    
    def getAppModel(self,appName):
        return self.getAppRecord(appName).model
    
    def getAppHome(self,appName):
        return self.getAppRecord(appName).home
        
    def startActor(self,msg):
        '''
        Start an actor of an application 
        '''
        assert type(msg) == tuple and len(msg) == 4
        appName,appModel,actorName,actorArgs = msg
        
        appHome = self.getAppHome(appName)
        
        # Starter
        riaps_prog = 'riaps_actor'

        appFolder = join(self.riapsApps, appName)
        appModelPath = join(appFolder, appModel)
         
        if not os.path.isdir(appFolder):
            raise BuildError('App folder is missing: %s' % appFolder)
    
        componentTypes = self.getComponentTypes(appName, actorName)
        if len(componentTypes) == 0:
            raise BuildError('Actor has no components: %s.%s.' % (appName,actorName))
        for componentType in componentTypes:
            # Look up the Python version first
            pyFilePath = join(appFolder, componentType + '.py')
            if os.path.isfile(pyFilePath): continue
            # Look up the C++version 
            ccFilePath = join(appFolder, 'lib' + componentType.lower() + '.so')
            if not os.path.isfile(ccFilePath):
                raise BuildError('Implementation of component %s is missing' % componentType)

        self.resm.addActor(appName, actorName, self.getActorModel(appName, actorName))
        self.fm.addActor(appName, actorName, self.getActorModel(appName, actorName))
        riaps_mod = self.riaps_actor_file   #  File name for python script 'riaps_actor.py'
    
        userName = self.appUser[appName]
        user_record = self.users[userName]
        user_ld_libs = self.getAppLibs(appName)
        user_env = self.makeUserEnv(userName,user_ld_libs)
        
        user_env['PATHS_FROM_ECLIPSE_TO_PYTHON'] = '[[\"%s\",\"%s\"]]' %(appHome,appFolder)
        
        user_uid = user_record.uid
        user_gid = user_record.gid
        user_cwd = appFolder
        
        riaps_arg1 = appName
        riaps_arg2 = appModelPath
        riaps_arg3 = actorName
        command = [riaps_prog,riaps_arg1,riaps_arg2,riaps_arg3]
        for arg in actorArgs:
            command.append(arg)
        if Config.APP_LOGS == 'log':
            logFileName = os.path.join(self.riapsApps,appName,actorName + '.log')
            logFile = open(logFileName ,"ab")
        else:
            logFile = None
        self.logger.info("Launching %s " % str(command))
        try:
            proc = psutil.Popen(command,
                                preexec_fn=self.demote(user_uid, user_gid,self.is_su), 
                                cwd=user_cwd, env=user_env, 
                                stdout=logFile, stderr=subprocess.STDOUT)
        except (FileNotFoundError,PermissionError):
            try:
                # if isPython:
                command = ['python3',riaps_mod] + command[1:]
                # else:
                #    command = [riaps_prog] + command[1:]
                proc = psutil.Popen(command,
                                    preexec_fn=self.demote(user_uid, user_gid,self.is_su), 
                                    cwd=user_cwd, env=user_env,
                                    stdout=logFile, stderr=subprocess.STDOUT)
            except:
                self.logger.error("Error while starting actor: %s -- %s" % (command,sys.exc_info()[0]))
                raise
        try:
            rc = proc.wait(const.depmStartTimeout)
        except:
            rc = None
        if rc != None:
            raise BuildError("Actor failed to start: %s.%s " % (appName,actorName))
        
        pid = proc.pid
        cmdline = [p.info for p in psutil.process_iter(attrs=['pid','cmdline']) 
                   if pid == p.info['pid']][0]['cmdline']
                   
        self.resm.startActor(appName, actorName, proc)
        self.fm.startActor(appName, actorName, proc)
        key = str(appName) + "." + str(actorName)
        with self.mapLock:
            self.launchMap[key] = proc
            self.actors[key] = DeploActorRecord(app=appName, model=appModel, actor=actorName, args = actorArgs, 
                                                device=None, control = None, monitor = None)
            self.peerQueue[key] = [ ]
        self.appDbase.addAppActor(appName, DeploActorCommand(app=appName, model=appModel, actor=actorName,args=actorArgs,
                                                             cmd=cmdline,pid=pid))
        self.procm.monitor(key,proc)
        self.logger.info("Started %s" % key)

    def getActorModel(self,appName,actorName):
        model = self.getAppModel(appName)
        
        if actorName in model["actors"]:
            actorModel = model["actors"][actorName]
        elif actorName in model["devices"]:
            actorModel = model["devices"][actorName]    # TODO:needs a proper actor model
        else:
            raise BuildError('Actor "%s" unknown' % actorName)
        
        return actorModel

    def getAppLibs(self,appName):
        model = self.getAppModel(appName)
        app_libs = []
        libraries = model["libraries"]
        for lib in libraries:
            app_libs += [lib['name']]
        return app_libs
        
    def getComponentTypes(self,appName, actorName):
        '''
        Collects all the component types of an actor.
        '''
        componentTypes = []
        appModel = self.getAppModel(appName)
        componentDefs = appModel["components"]
        actorModel = self.getActorModel(appName,actorName)

        for key in actorModel["instances"]:
            compType = actorModel["instances"][key]["type"]
            if compType in componentDefs:           # Component
                componentTypes.append(compType)
            else:
                pass                                # Device component
            
        return componentTypes
    
    def terminateActor(self,proc,appName,actorName):
        '''
        Terminate actor (runs in a background thread)
        '''
        qualName = str(appName) + "." + str(actorName)
        proc.poll()
        if proc.returncode == None:
            self.logger.info("Terminating %s" % qualName)
            try:          
                proc.terminate()                    # Should check for errors
                proc.wait(const.depmTermTimeout)    # Wait here
                self.logger.info("Actor %s terminated" % qualName)
            except psutil.TimeoutExpired:
                self.logger.info("Actor %s did not terminate - killing it" % qualName)
                self.unRegisterActor(appName,actorName,proc.pid)
                proc.send_signal(signal.SIGKILL)
                time.sleep(1.0)
            except:
                traceback.print_exc()
    
    def stopActor(self,appName,actorName):
        '''
        Stop the actor of an application.
        '''
        qualName = str(appName) + "." + str(actorName)
        proc = None
        with self.mapLock:
            assert qualName in self.launchMap
            proc = self.launchMap[qualName]
            del self.launchMap[qualName]
        if proc != None:
            self.logger.info("Stopping actor %s" % qualName)
            self.resm.stopActor(appName, actorName, proc)
            self.fm.stopActor(appName, actorName, proc)
            assert qualName in self.actors
            record = self.actors[qualName]
            device = record.device
            _control = record.control
            _monitor = record.monitor
            # TODO: Stop the zmqdevice, disconnect/destroy sockets
            device._context.term()          # Terminate context for zmqDevice
            device.join()
            # control.close()                # TODO remove sockets from poller
            # monitor.close()                
            del self.actors[qualName]
            self.procm.release(qualName)
            self.appDbase.delAppActor(appName, actorName)
            self.executor.submit(self.terminateActor,proc,appName,actorName)
        self.logger.info("Stopped %s" % qualName)

    def haltActor(self,msg):
        '''
        Ask the background thread to stop the actor of an application  
        '''
        assert type(msg) == tuple and len(msg) == 2
        appName,actorName = msg 
        try:
            self.stopActor(appName,actorName)
        except BuildError as buildError:
            self.logger.error(str(buildError.args[1]))
    
    def unRegisterActor(self,appName,actorName,actorPid):
        '''
        Unregister a dead actor from the disco service
        '''
        with self.discoLock:
            reqt = disco_capnp.DiscoReq.new_message()
            appMessage = reqt.init('actorUnreg')
            appMessage.appName = appName
            appMessage.version = '0.0.0'
            appMessage.actorName = actorName
            appMessage.pid = actorPid
                      
            msgBytes = reqt.to_bytes()
            
            try:
                self.discoCommand.send(msgBytes)
            except Exception as e:
                self.logger.error("Unable to unregister app with discovery: %s" % e.args)
                return
            
            try:
                respBytes = self.discoCommand.recv()
            except Exception as e:
                self.logger.error("No response from discovery service: %s" % e.args)
                return
            
            resp = disco_capnp.DiscoRep.from_bytes(respBytes)
            
            which = resp.which()
            if which == 'actorUnreg':
                respMessage = resp.actorUnreg
                status = respMessage.status
                if status == 'ok':
                    self.logger.info("unregistered '%s.%s'" % (appName,actorName))
                else:
                    self.logger.error("Bad response from disco service at app unregistration")
            else:
                self.logger.error("Unexpected response from disco service at app unregistration")
                
                
    def queryApps(self):
        reply = {}
        # This should be self.actors 
        for key in self.launchMap.keys():
            appName,actorName = key.split('.')
            if appName in reply.keys():
                actors = reply[appName]
                actors += [actorName]
                reply[appName] = actors
            else:
                reply[appName] = [actorName]
        self.ctrl.send_pyobj(reply)
    
    def reclaimApp(self,msg):
        assert type(msg) == tuple and len(msg) == 1
        appName = msg[0]
        self.resm.reclaimApp(appName)
        self.ctrl.send_pyobj('ok')
            
    def handleCommand(self,msg):
        self.logger.info("handleCommand: %s" % (str(msg)))
        try: 
            cmd = msg[0]
            if cmd == 'launch':             # Launch an actor
                self.startActor(msg[1:])
            elif cmd == "halt":             # Halt an actor
                self.haltActor(msg[1:])
            elif cmd == "setupApp":         # Setup an app
                self.setupApp(msg[1:])
            elif cmd == "cleanupApp":       # Cleanup an app
                self.cleanupApp(msg[1:])
            elif cmd == "cleanupApps":      # Cleanup all apps
                self.cleanupApps(msg[1:])
            elif cmd == "setDisco":         # Set up disco 
                self.setupDisco(msg[1:])
            elif cmd == "query":            # Query running apps
                self.queryApps()
            elif cmd == "reclaim":          # Reclaim app files (for riaps)
                self.reclaimApp(msg[1:])
            elif cmd == "install":          # Install downloaded package
                self.installApp(msg[1:])
            else:
                pass
        except: 
            info = sys.exc_info()
            self.logger.error("Error in handleCommand '%s': %s %s" % (cmd, info[0], info[1]))
            traceback.print_exc()
    
    def kill(self,what,pid):
        self.logger.info("killing %s [%d]" % (what,pid))
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as err:
            if err.errno == errno.ESRCH:
                return
        cnt = 0 
        while cnt < 10:
            time.sleep(1.0)
            try:
                os.kill(pid,0)
            except OSError as err:
                if err.errno == errno.ESRCH:
                    self.logger.info("terminated [%d]" % pid)
                    return
                cnt += 1
        self.logger.info("killing [%d]" % pid)
        try:
            os.kill(pid, signal.SIGKILL)
            time.sleep(1.0)
            os.kill(pid,0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                self.logger.info("killed [%d]" % pid)
                return
        
    def stopOrphanDisco(self):
        record = self.appDbase.getDiscoCommand()
        if record != None:
            cmdline = record.cmd
            pid = record.pid 
            infoList = [p.info for p in psutil.process_iter(attrs=['pid','cmdline'])
                        if pid == p.info['pid']]
            for info in infoList:
                if cmdline == info['cmdline']:
                    self.logger.info("stopping orphan disco [%d] '%s'" % (pid,' '.join(cmdline)))
                    self.kill('orphan disco',pid)
                    self.appDbase.delDiscoCommand()
                    
        
    def stopOrphanActor(self,record):
        cmdline = record.cmd
        pid,appName,actorName = record.pid, record.app, record.actor
        infoList = [p.info for p in psutil.process_iter(attrs=['pid','cmdline'])
                    if pid == p.info['pid']]
        for info in infoList:
            if cmdline == info['cmdline']:
                self.logger.info("stopping orphan actor [%d] '%s'" % (pid,' '.join(cmdline)))
                self.kill('orphan actor',pid)
        self.appDbase.delAppActor(appName, actorName)
                
    def unregisterOrphanActor(self,record):
        pid,appName,actorName = record.pid, record.app, record.actor
        self.unRegisterActor(appName,actorName,pid)
        
    def recover(self):
        disco = self.appDbase.getDisco()
        apps = self.appDbase.getApps()
        cmds = { } 
        recs = [ ]
        for app in apps:                            # Stop orphan actors 
            acts = self.appDbase.getAppActors(app)
            cmds[app] = acts
            for act in acts:
                self.stopOrphanActor(act)
                recs += [act]
        if disco != None:                           # Recover discovery
            self.stopOrphanDisco()
            self.logger.info("recover: disco = %s" % str(disco))
            self.setupDisco(disco)
        for act in recs:                            # Unregister orphan actors from disco
            self.unregisterOrphanActor(act)
        for app in apps:
            appSet = False
            self.logger.info("recover: app = %s" % str(app))
            acts = cmds[app]
            for act in acts:
                appName = str(act.app)
                actName = str(act.actor)
                try:
                    if not appSet:
                        self.setupApp((act.app,act.model))
                        appSet = True
                    self.logger.info("recover: actor = %s.%s" % (appName,actName))
                    self.startActor((act.app,act.model,act.actor,act.args))
                except:
                    self.logger.error("recovery failed: actor = %s.%s" % (appName,actName))
                    self.appDbase.delAppActor(appName,actName)
    
    def pollMonitor(self,appName,actorName,sock):
        if self.poller != None:
            self.monitors[(appName,actorName)] = sock
            self.monitors[sock] = (appName,actorName)
            self.poller.register(sock,zmq.POLLIN)

    def run(self):
        '''
        Main loop of the depl service
        '''
        self.logger.info("starting")
        # self.printApps()
        try:
            # Server socket for client requests
            self.server = self.context.socket(zmq.REP)  
            endpoint = const.deplEndpoint
            self.server.bind(endpoint)
            # Control socket to receive commands from main thread
            self.ctrl = self.context.socket(zmq.PAIR)
            self.ctrl.connect(self.depmCommandEndpoint)
            # Socket to communicate with procmon threads
            self.procmon = self.context.socket(zmq.ROUTER)        
            self.procmon.bind(self.procMonEndpoint)
            # Socket for communication with fault monitor
            self.fmmon = self.fm.setupFMMon()
            self.uuid = self.fm.getUUID()
            # Socket for communication with NIC manager
            self.nicmon = self.fm.setupNICMon()
            # Poller for commands, requests, and procmon messages             
            self.poller = zmq.Poller()                   
            self.poller.register(self.server,zmq.POLLIN)
            self.poller.register(self.ctrl,zmq.POLLIN)
            self.poller.register(self.procmon,zmq.POLLIN)
            self.poller.register(self.fmmon,zmq.POLLIN)
            self.poller.register(self.nicmon,zmq.POLLIN)
            # Map of clients
            self.clients = { }  
            # Event for termination
            self.terminated = threading.Event()     # Event flag to signal termination
            self.terminated.clear()
            self.logger.info("running")
            self.started = True
        # 
        except:
            self.logger.error("start failed")
            self.stop()
            raise
        self.recover()
        while True:
            if self.terminated.is_set(): break
            sockets = dict(self.poller.poll(1000.0)) # Poll client messages, with timeout 1 sec
            if len(sockets) == 0:                    # If no message but timeout expired, 
                if self.terminated.is_set(): 
                    break                           # break out if terminated
            toDelete = []           
            for s in sockets:
                if s == self.ctrl:                  # Handle commands from main
                    msg = self.ctrl.recv_pyobj()
                    self.handleCommand(msg)
                elif s == self.server:              # Handle client requests
                    msg = self.server.recv()
                    self.handleClient(msg)
                elif s == self.procmon:             # Handle procmon messages
                    self.handleProcmon()
                elif s == self.fmmon:               # Handle fault monitor messages
                    self.handleFMMon()
                elif s == self.nicmon:              # Handle NIC monitor messages
                    self.handleNICMon()
                else:
                    if s in self.monitors:
                        (appName,actorName) = self.monitors[s]
                        msgBytes = s.recv()
                        self.handleActorMessage(appName,actorName,msgBytes)
                    else:
                        self.logger.error("unknown socket")
                toDelete += [s]
            for s in toDelete:
                del sockets[s]                
        self.stop()
    
            
    def handleClient(self,msgBytes):
        '''
        Handle a message from a client (i.e. an actor) 
        '''
        self.logger.info("handleClient")
        try:
            msg = deplo_capnp.DeplReq.from_bytes(msgBytes)
            which = msg.which()
            if which == 'actorReg':
                self.handleActorReg(msg)
            elif which == 'deviceGet':
                self.handleDeviceReq(msg)
            elif which == 'deviceRel':
                self.handleDeviceRel(msg)
            elif which == 'reportEvent':
                self.handleReportEvent(msg)
            else:
                pass
        except: 
            info = sys.exc_info()
            self.logger.error("Error in handleClient '%s': %s %s" % (which, info[0], info[1]))
            traceback.print_exc()


    def setupClient(self,appName,_appVersion,appActorName):
        '''
        Set up a new client of the deplo manager. The client actors are to register with
        the manager using the 'server' (REQ/REP) socket. The manager will then create a dedicated
        (PAIR) socket for the client to connect to. This socket is used as a private communication
        channel between a specific client actor and the service.   
        '''
        sock = self.context.socket(zmq.PAIR)
        port = sock.bind_to_random_port('tcp://127.0.0.1')
        clientKeyBase = "/" + appName + '/' + appActorName + "/"
        self.clients[clientKeyBase] = sock
        clientKeyLocal = clientKeyBase + self.macAddress
        self.clients[clientKeyLocal] = port
        clientKeyGlobal = clientKeyBase + self.hostAddress
        self.clients[clientKeyGlobal] = port
        sock.close()
        time.sleep(0.1)
        return port
    
    def binder(self):
        binder = self.context.socket(zmq.REQ)
        iface = 'tcp://127.0.0.1'
        port = binder.bind_to_random_port(iface)
        binder.close()
        return port
    
    def handleActorReg(self,msg):
        '''
        Handle the registration of an application actor with the service. 
        '''
        actReg = msg.actorReg
        appName = actReg.appName
        appVersion = actReg.version   
        appActorName = actReg.actorName
        isDevice = actReg.isDevice
    
        self.logger.info("handleActorReg: %s %s %s" 
                         % (appName, appActorName, '[device]' if isDevice else ''))
        
        qualName = str(appName) + "." + str(appActorName)
        err = True        
        if qualName in self.launchMap:
            if not isDevice and qualName in self.actors:
                _actorRecord = self.actors[qualName]
                err = False
            elif isDevice and qualName in self.devices:
                _actorRecord = self.devices[qualName]
                err = False
        
        if err:
            self.logger.error('unknown actor: %s - rejected' % qualName)
            rsp = deplo_capnp.DeplRep.new_message()
            rspMessage = rsp.init('actorReg')
            rspMessage.status = 'err'
            rspBytes = rsp.to_bytes()
            self.server.send(rspBytes)   
            return
        
        clientPort = self.setupClient(appName,appVersion,appActorName)
        clientPID  = self.launchMap[qualName].pid
        
        zmqDevice = devices.ThreadProxy(zmq.DEALER,zmq.PAIR,zmq.PUB)
        identity = actorIdentity(appName, appActorName, clientPID)
        self.logger.info("zmqDevice ID = %s" % identity)
        zmqDevice.setsockopt_in(zmq.IDENTITY, identity.encode(encoding='utf_8'))
        # device.setsockopt_in(zmq.RCVTIMEO,const.deplEndpointRecvTimeout)
        # device.setsockopt_out(zmq.SNDTIMEO,const.deplEndpointSendTimeout)
        zmqDevice.bind_out('tcp://127.0.0.1:%i' % clientPort)      # 
        
        self.resm.addClientDevice(appName,appActorName,zmqDevice)
        
        # Socket for sending control messages to the actor
        actorControl = self.context.socket(zmq.ROUTER)
        actorPort = actorControl.bind_to_random_port('tcp://127.0.0.1')
        zmqDevice.connect_in('tcp://127.0.0.1:%i' % actorPort)
        
        # Monitoring socket to intercept messages going to the actor
        monPort = self.binder()
        monAddr = 'tcp://127.0.0.1:%i' % monPort
        zmqDevice.bind_mon(monAddr)

        actorMonitor = self.context.socket(zmq.SUB)
        actorMonitor.setsockopt(zmq.SUBSCRIBE, b'')
        actorMonitor.connect(monAddr)
        
        self.pollMonitor(appName,appActorName,actorMonitor)
        self.fm.addClientDevice(appName,appActorName,zmqDevice)
        
        time.sleep(0.1)
        zmqDevice.start()
        time.sleep(0.1)

        actorArgs = _actorRecord.args
        appModel = _actorRecord.model
        if isDevice:
            self.devices[qualName] = DeviceActorRecord(app=appName, model=appModel, actor=appActorName, args=actorArgs,
                                                       device=zmqDevice, 
                                                       control = actorControl, monitor = actorMonitor)
        else:
            self.actors[qualName] = DeploActorRecord(app=appName, model=appModel, actor=appActorName, args=actorArgs,
                                                     device=zmqDevice, 
                                                     control = actorControl, monitor = actorMonitor)
                
        rsp = deplo_capnp.DeplRep.new_message()
        rspMessage = rsp.init('actorReg')
        rspMessage.status = "ok"
        rspMessage.port = clientPort
        rspMessage.uuid = self.uuid.decode()
        rspBytes = rsp.to_bytes()
        self.server.send(rspBytes)
        if not isDevice:
            self.handlePeerQueue(qualName)

    def handlePeerQueue(self,qualName):
        '''
        Process delayed messages from peer message queue
        '''
        with self.mapLock:
            record = self.actors[qualName]
            control = record.control
            assert control != None
            msgs = self.peerQueue[qualName]
            for msg in msgs:
                cmd,appName,actorName,peer = msg
                assert cmd in ('peer+','peer-')
                key = str(appName) + "." + str(actorName)
                assert key == qualName
                msg = deplo_capnp.DeplCmd.new_message()
                msgMessage = msg.init('peerInfoMsg')
                msgMessage.peerState = 'on' if cmd == 'peer+' else 'off'
                msgMessage.uuid = peer.decode()
                msgBytes = msg.to_bytes()
                payload = zmq.Frame(msgBytes)
                pid = self.launchMap[qualName].pid
                identity = actorIdentity(appName, actorName, pid)
                header = identity.encode(encoding='utf-8')
                control.send_multipart([header,payload])
            self.peerQueue[qualName] = []
        
    def startDevice(self,appName,appModel,actorName,actorArgs):
        '''
        Start a device actor for an application 
        '''
        key = str(appName) + "." + str(actorName)
        with self.mapLock:
            if key in self.launchMap:
                self.launchRefs[key] += 1 
                return
        
        appHome = self.getAppHome(appName)
        
        # Starter 
        riaps_prog = 'riaps_device'      #
        
        riaps_mod = self.riaps_device_file  # Module file name for script 
        
        appFolder = join(self.riapsApps,appName)
        appModelPath = join(appFolder,appModel)
        
        if not os.path.isdir(appFolder):
            raise BuildError('App folder is missing: %s' % appFolder)
        
        componentType = actorName 
        # Look up the Python version first
        pyFilePath = join(appFolder, componentType + '.py')
        if os.path.isfile(pyFilePath):
            pass                # Use the Python implementation
        else:                   # Find C++ implementation
            ccFilePath = join(appFolder, 'lib' + componentType.lower() + '.so')
            if not os.path.isfile(ccFilePath):
                raise BuildError('Implementation of component %s is missing' % componentType)
        
        self.resm.addActor(appName, actorName, self.getActorModel(appName, actorName))
        self.fm.addActor(appName, actorName, self.getActorModel(appName, actorName))
        
        dev_env = os.environ.copy()          
        
        dev_env['PATHS_FROM_ECLIPSE_TO_PYTHON'] = '[[\"%s\",\"%s\"]]' %(appHome,appFolder)
           
        app_libs = self.getAppLibs(appName)
        self.makeLdLibEnv(dev_env,app_libs)
        
        riaps_arg1 = appName 
        riaps_arg2 = appModelPath
        riaps_arg3 = actorName
        command = [riaps_prog,riaps_arg1,riaps_arg2,riaps_arg3]
        for arg in actorArgs:
            command.append(arg)
        if Config.APP_LOGS == 'log':
            logFileName = os.path.join(self.riapsApps,appName,actorName + '.log')
            logFile = open(logFileName ,"ab")
        else:
            logFile = None
        self.logger.info("Launching %s " % str(command))
        try:
            proc = psutil.Popen(command,cwd=appFolder,env=dev_env)
        except FileNotFoundError:
            try:
                command = ['python3',riaps_mod] + command[1:]
                proc = psutil.Popen(command,
                                        cwd=appFolder,env=dev_env,
                                        stdout=logFile, stderr=subprocess.STDOUT)
            except:
                raise BuildError("Error while starting device: %s" % sys.exc_info()[1])
        try:
            rc = proc.wait(const.depmStartTimeout)
        except:
            rc = None
        if rc != None:
            raise BuildError("Device failed to start: %s " % (command,))
        self.resm.startActor(appName, actorName, proc)
        self.fm.startActor(appName, actorName, proc)
        key = str(appName) + "." + str(actorName)
        with self.mapLock:
            self.launchMap[key] = proc
            self.launchRefs[key] = 1
            self.devices[key] = DeviceActorRecord(app=appName, model=appModel, actor=actorName, args = actorArgs, 
                                                  device=None, control = None, monitor = None)
        self.procm.monitor(key,proc)
        self.logger.info("Started %s" % key)

    def terminateDevice(self,proc,appName,actorName):
        '''
        Ultimate operation to terminate a device
        '''
        qualName = str(appName) + "." + str(actorName)
        try: 
            proc.terminate()            # Should check for errors
            proc.wait(const.depmTermTimeout)   
            self.logger.info("Device %s terminated" % qualName) # 
        except psutil.TimeoutExpired:
            self.logger.info("Device %s did not stop - killing it" % qualName)
            self.unRegisterActor(appName,actorName,proc.pid)    # Clean discovery service
            proc.send_signal(signal.SIGKILL)
            time.sleep(1.0)
        except:
            traceback.print_exc()
    
    def stopDevice(self,appName,actorName):
        '''
        Stop a device actor of an application 
        '''        
        qualName = str(appName) + "." + str(actorName)
        proc = None
        running = False
        with self.mapLock:
            if qualName not in self.launchMap:
                return
            proc = self.launchMap[qualName]
            proc.poll()
            if proc.returncode == None:
                running = True
                if self.launchRefs[qualName] == 1:
                    del self.launchMap[qualName]
                    del self.launchRefs[qualName]
                else:
                    self.launchRefs[qualName] -= 1
                    return
            else:
                running = False
                del self.launchMap[qualName]
                del self.launchRefs[qualName]
        if proc != None:
            self.logger.info("Stopping device %s" % qualName)
            assert qualName in self.devices
            self.procm.release(qualName)
            if running:       
                self.terminateDevice(proc,appName,actorName) 
        self.logger.info("Stopped %s" % qualName)
        
    def handleDeviceReq(self,msg):
        '''
        Handle the request for a device 
        '''
        devGet = msg.deviceGet
        appName = devGet.appName 
        modelName = devGet.modelName
        typeName = devGet.typeName
        self.logger.info("handleDeviceReq: %s,%s,%s " % (appName,typeName,str(devGet.deviceArgs)))
        
        cmdArgs = []
        for deviceArg in devGet.deviceArgs:
            argName = deviceArg.name
            argValue = deviceArg.value
            cmdArgs.append('--' + argName)
            cmdArgs.append(argValue)
        
        ok = True
        try:
            self.startDevice(appName, modelName, typeName, cmdArgs)
        except BuildError as buildError:
            ok = False
            self.logger.error(str(buildError.args[0]))

        #      
        rsp = deplo_capnp.DeplRep.new_message()
        rspMessage = rsp.init('deviceGet')
        rspMessage.status = "ok" if ok else "err"
        rspBytes = rsp.to_bytes()
        self.server.send(rspBytes)
        self.logger.info("handleDeviceReq: done")

    def handleDeviceRel(self,msg):
        '''
        Handle the release of a device 
        '''
        devRel = msg.deviceRel
        appName = devRel.appName 
        _modelName = devRel.modelName
        typeName = devRel.typeName
        self.logger.info("handleDeviceRel: %s,%s" % (appName,typeName))
        
        ok = True
        try:
            # self.stopDevice(appName, typeName)
            self.executor.submit(self.stopDevice,appName,typeName)
        except BuildError as buildError:
            ok = False
            self.logger.error(str(buildError.args[1]))
        #      
        rsp = deplo_capnp.DeplRep.new_message()
        rspMessage = rsp.init('deviceRel')
        rspMessage.status = "ok" if ok else "err"
        rspBytes = rsp.to_bytes()
        self.server.send(rspBytes)
        self.logger.info("handleDeviceRel: done")
    
    def handleReportEvent(self,msg):
        '''
        Handle the event report from actor 
        '''
        repEvt = msg.reportEvent
        appName = repEvt.appName
        _appVersion = repEvt.version   
        actorName = repEvt.actorName
        msg = repEvt.msg

        self.logger.info("handleReportEvent: %s.%s" % (appName,actorName))
        
        ok = True
        try:
            # self.stopDevice(appName, typeName)
            self.logger.error('Event from %s.%s = %s' % (appName,actorName,msg))
        except BuildError as buildError:
            ok = False
            self.logger.error(str(buildError.args[1]))
        #      
        rsp = deplo_capnp.DeplRep.new_message()
        rspMessage = rsp.init('reportEvent')
        rspMessage.status = "ok" if ok else "err"
        rspBytes = rsp.to_bytes()
        self.server.send(rspBytes)
        self.logger.info("handleReportEvent: done")
    
    def stop(self):
        self.logger.info("stopping")
        # Clean up everything
        # Logout from service
        # Kill actors
        toHalt = []
        for key in self.launchMap.keys():
            appName,actorName = key.split('.')
            toHalt += [(appName,actorName)]
        for h in toHalt:
            self.haltActor(h)
        # time.sleep(3.0) # Allow actors terminate cleanly
        self.executor.shutdown()    # Ensure all actors have terminated 
        # Cleanup resm 
        self.resm.cleanupApps()
        # Cleanup fm
        self.fm.cleanupApps()
        # Terminate disco
        if self.disco != None:
            self.procm.release(self.DISCONAME)
            self.disco.terminate()
            self.disco = None
        self.appDbase.closeDbase()
        self.logger.info("stopped")
        

    def reinstate(self):
        '''
        Ask actors to reinstate their connections to deplo
        '''
        for qualName,proc in self.launchMap.items():
            proc.poll()
            if proc.returncode == None:
                if qualName in self.actors:
                    record = self.actors[qualName]
                elif qualName in self.devices:
                    record = self.devices[qualName]
                control = record.control
                appName, actName = record.app, record.actor
                if control != None: 
                    msg = deplo_capnp.DeplCmd.new_message()
                    msgMessage = msg.init('reinstateCmd')
                    msgMessage.msg = 'doit'
                    msgBytes = msg.to_bytes()
                    payload = zmq.Frame(msgBytes)
                    identity = actorIdentity(appName,actName,proc.pid)
                    header = identity.encode(encoding='utf-8')
                    control.send_multipart([header,payload])
                    self.logger.info('reinstate req to %s' % qualName)
                else:
                    # TODO queue up reinstate command for later send
                    pass
        
    def handleProcmon(self):
        '''
        Handle messages from process monitor: restart disco/actor/device 
        '''
        msgFrames = self.procmon.recv_multipart()
        identity = msgFrames[0]
        msg = pickle.loads(msgFrames[1])
        (qualName,) = msg
        if qualName == self.DISCONAME:
            self.startDisco()
            self.reinstate()
        else:
            appName,actorName = qualName.split('.')
            if qualName in self.actors:
                record = self.actors[qualName]
                assert appName == record.app and actorName == record.actor                
                appModel = record.model
                actorArgs = record.args
                assert qualName in self.launchMap
                proc = self.launchMap[qualName]
                actorPid = proc.pid    
                self.stopActor(appName, actorName)
                self.unRegisterActor(appName,actorName,actorPid)
                self.appDbase.delAppActor(appName, actorName)
                msg = (appName,appModel,actorName,actorArgs)
                self.startActor(msg)
            elif qualName in self.devices:
                record = self.devices[qualName]
                appModel = record.model
                actorArgs = record.args
                self.stopDevice(appName,actorName)
                self.startDevice(appName, appModel, actorName, actorArgs)
        py_response = 'ok'
        response = pickle.dumps(py_response)
        payload = zmq.Frame(response)
        self.procmon.send_multipart([identity,payload])
    
    def handleFMMon(self):
        '''
        Handle fault monitor messages (peer changes from the network)
        '''
        msg = self.fmmon.recv_pyobj()
        self.logger.info("handleFMMon: %s " % str(msg))
        cmd,appName,actorName,peer = msg
        assert cmd in ('peer+','peer-')
        qualName = str(appName) + "." + str(actorName)
        with self.mapLock:
            if qualName in self.actors and qualName in self.launchMap:
                record = self.actors[qualName]
                pid = self.launchMap[qualName].pid
                control = record.control
                if control != None:
                    msg = deplo_capnp.DeplCmd.new_message()
                    msgMessage = msg.init('peerInfoMsg')
                    msgMessage.peerState = 'on' if cmd == 'peer+' else 'off'
                    msgMessage.uuid = peer.decode()
                    msgBytes = msg.to_bytes()
                    payload = zmq.Frame(msgBytes)
                    pid = self.launchMap[qualName].pid
                    identity = actorIdentity(appName,actorName,pid)
                    header = identity.encode(encoding='utf-8')
                    control.send_multipart([header,payload])
                else:
                    self.peerQueue[qualName].append(msg)        # TODO: limit the queue size

    
    def handleNICMon(self):
        '''
        Handle NIT state changes messages from NIC monitor
        '''
        msg = self.nicmon.recv_pyobj()
        assert type(msg) == tuple and len(msg) == 1
        flag = msg[0]
        assert flag in ('nic+','nic-')
        self.logger.info("handleNICMon: %s " % str(msg))
        for qualName in self.actors:
            record = self.actors[qualName]
            appName,actName = record.app,record.actor
            control = record.control
            if control == None: continue
            msg = deplo_capnp.DeplCmd.new_message()
            msgMessage = msg.init('nicStateMsg')
            msgMessage.nicState = 'up' if flag == 'nic+' else 'down'
            msgBytes = msg.to_bytes()
            payload = zmq.Frame(msgBytes)
            pid = self.launchMap[qualName].pid
            identity = actorIdentity(appName,actName,pid)
            header = identity.encode(encoding='utf-8')
            control.send_multipart([header,payload])

        
    def handleActorMessage(self,appName,actorName,msgBytes):
        '''
        Handle a  message that has been sent to the actor
        '''
        msg = deplo_capnp.DeplCmd.from_bytes(msgBytes)      

        which = msg.which()
        if which == 'resourceMsg':      # Resource violation
            what = msg.resourceMsg.which()
            self.logger.info('handleActorMessage: %s.%s - %s' 
                             % (appName,actorName,what))
            # TODO: send message to fault manager
        elif which == 'reinstateCmd':   # Reinstate command - ignore
            pass
        elif which == 'nicStateMsg':    # NIC state has changed - ignore
            pass
        elif which == 'peerInfoMsg':    # Peer info has changed - ignore
            pass
        else:
            self.logger.error("unknown msg from monitor: '%s'" % which)
            pass
    
    def terminate(self):
        if self.started:
            self.terminated.set()
