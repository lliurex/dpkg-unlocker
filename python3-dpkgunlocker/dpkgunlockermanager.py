#!/usr/bin/env python3

import os
import sys
import psutil
import struct, fcntl
import subprocess


class DpkgUnlockerManager(object):

	"""docstring for DpkgUnlockerManager"""
	def __init__(self):
		super(DpkgUnlockerManager, self).__init__()

		self.lliurexUpLockTokenPath="/var/run/lliurexUp.lock"
		self.aptLockTokenPath="/var/lib/apt/lists/lock"
		self.dpkgLockTokenPath="/var/lib/dpkg/lock"
		self.lockTokenPath="/var/run/dpkgUnlocker.lock"
		self.disableMetaProtectionTokenPath="/var/run/disableMetaProtection.token"
		self.lockeds={}

	#def __init__	

	def createLockToken(self):
		if not os.path.exists(self.lockTokenPath):
			with open(self.lockTokenPath,'w') as fd:
				upPid=os.getpid()
				fd.write(str(upPid))
			
	#def createLockToken

	def cleanLockToken(self):

		if os.path.exists(self.lockTokenPath):
			os.remove(self.lockTokenPath)

	#def cleanLockToken		

	def isLliurexUpLocked(self):

		'''
		 0: Lliurex-Up is not running
		 1: Lliurex-Up is running
		 2: Lliurex-Up is locked for previous failed process
		 ''' 
		if not os.path.exists(self.lliurexUpLockTokenPath):
			return 0

		try:
			with open(self.lliurexUpLockTokenPath,'r') as fd:
				upPid=fd.readline().strip()

			if upPid:
				self.upPid=int(upPid)
				if psutil.pid_exists(self.upPid):
					return 1
				return 2
			
			return 2

		except (ValueError,OSError):
			return 2
		
	#def isLliurexUpLocked
	
	def isAptLocked(self):

		'''
		 0: Apt is not running
		 1: Apt is running
		 2: Apt is locked for previous failed process
		 4: Apt Daemon is locked
		 ''' 

		lsofData=self.checkAptdLock(self.aptLockTokenPath)

		if lsofData:
			self.aptApdRun=self.findProcess("aptd")
			if self.aptApdRun is not None:
				aptApdRun=self.aptApdRun[0]["pid"]
				if aptApdRun in lsofData:
					return 4
		try:
			with open(self.aptLockTokenPath, 'w') as fd:
				fcntl.lockf(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
				return 0

		except FileNotFoundError:
			return 0

		except OSError:
			self.aptRun=self.findProcess("apt-get")
			if self.aptRun is not None:
				return 1
			return 2

	#def isAptLocked
		
	def isDpkgLocked(self):

		'''
		 0: Dpkgis not running
		 1: Dpkg is running
		 2: Dpkg is locked for previous failed process
		 3: Apt is running
		 4: Apt Daemon is running

		 ''' 
		lsofData=self.checkAptdLock(self.dpkgLockTokenPath)

		if lsofData:
			self.dpkgApdRun=self.findProcess("aptd")
			if self.dpkgApdRun is not None:
				dpkgApdRun=self.dpkgApdRun[0]["pid"]
				if dpkgApdRun in lsofData:
					return 4

		try:
			with open(self.dpkgLockTokenPath, 'w') as fd:
				fcntl.lockf(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
				return 0

		except FileNotFoundError:
			return 0

		except OSError:
			self.dpkgRun=self.findProcess("dpkg")
			if self.dpkgRun is not None:
				return 1

			self.aptRun=self.findProcess("apt-get")
			if self.aptRun is not None:
				return 3

			return 2
				
	#def isAptLocked			

	def getProcessList(self,arg=None):
		
		self.processList = []
		
		for proc in psutil.process_iter(['username', 'pid', 'cpu_percent', 'memory_percent', 'status', 'create_time', 'cmdline']):
			try:
				info = proc.info
				cmdline_list = info['cmdline'] or []
				cmd_string = " ".join(cmdline_list)
				
				if not cmd_string:
					continue
					
				if arg == "aptd" and arg in cmd_string:
					command = cmdline_list[1] if len(cmdline_list) > 1 else cmdline_list[0]
				else:
					command = cmdline_list[0] if cmdline_list else ""
					
				process = {
					"user": info['username'],
					"pid": str(info['pid']),
					"cpu": str(info['cpu_percent']),
					"mem": f"{info['memory_percent']:.1f}" if info['memory_percent'] else "0.0",
					"vsz": str(proc.memory_info().vms // 1024) if proc.is_running() else "0", 
					"rss": str(proc.memory_info().rss // 1024) if proc.is_running() else "0", 
					"tty": "?",
					"stat": info['status'],
					"start": str(info['create_time']),
					"time": "0:00",
					"command": command
				}
				
				self.processList.append(process)
			
			except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
				continue
	
	#def getProcessList			

	def findProcess(self,filter):
		
		self.getProcessList(filter)
		
		retList=[
			process for process in self.processList
			if filter in process["command"]
		]

		return retList if retList else None			

	#def findProcess	

	def checkAptdLock(self,lockfile):

		cmd=["lsof", "-t", lockfile]

		try:
			result=subprocess.run(cmd,capture_output=True,text=True,check=False)
			output=result.stdout.strip()

			if output:
				return output.splitlines()

		except FileNotFoundError:
			pass

		return []

	#def checkAptdLock	

	def checkingLocks(self):

		self.lockeds["Lliurex-Up"]=self.isLliurexUpLocked()
		self.lockeds["Dpkg"]=self.isDpkgLocked()
		self.lockeds["Apt"]=self.isAptLocked()

		return self.lockeds
	
	#def checkingLocks

	def getUnlockerCommand(self, kill=None):

	    unlockerCommands = {}
	    commonCommand = ""
	    cont = 0
	    liveProcess = 0

	    services = {
	        "Lliurex-Up": self.lliurexUpLockTokenPath,
	        "Dpkg": self.dpkgLockTokenPath,
	        "Apt": self.aptLockTokenPath
	    }

	    for name, path in services.items():
	        status = self.lockeds.get(name, 0)
	        if status != 0:
	            if kill or status == 2:
	                unlockerCommands[name] = f"rm -f {path}"
	                cont += 1
	            else:
	                liveProcess += 1

	    if cont > 0 and liveProcess == 0:
	        commonCommand = (
	            "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive dpkg --configure -a; "
	            "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get update; "
	            "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install -f -y "
	            "--allow-downgrades --allow-remove-essential --allow-change-held-packages"
	        )

	    return {
	        "unlockCmd": unlockerCommands,
	        "commonCmd": commonCommand,
	        "liveProcess": liveProcess
	    }

	#def getUnlockerCommand

	def getKillerCommand(self):

		killerCommands = {}

		if self.lockeds.get("Lliurex-Up") == 1 and hasattr(self, 'upPid') and self.upPid:
			killerCommands["Lliurex-Up"] = f"kill -9 {self.upPid}"

		dpkg_status = self.lockeds.get("Dpkg", 0)
		if dpkg_status == 1 and getattr(self, 'dpkgRun', None):
			killerCommands["Dpkg"] = f"kill -9 {self.dpkgRun[0]['pid']}"
		elif dpkg_status == 3 and getattr(self, 'aptRun', None):
			killerCommands["Apt"] = f"kill -9 {self.aptRun[0]['pid']}"

		if self.lockeds.get("Apt", 0) == 1 and getattr(self, 'aptRun', None):
			killerCommands["Apt"] = f"kill -9 {self.aptRun[0]['pid']}"

		return killerCommands
	
	#def getKillerCommand

	def checkMetaProtection(self):

		if os.path.exists(self.disableMetaProtectionTokenPath):
			return False
		else:
			return True

	#def checkMetaProtection

	def changeMetaProtectionStatus(self,enabled):

		result=[]
		try:
			if enabled:
				if os.path.exists(self.disableMetaProtectionTokenPath):
					os.remove(self.disableMetaProtectionTokenPath)
			else:
				if not os.path.exists(self.disableMetaProtectionTokenPath):
					with open(self.disableMetaProtectionTokenPath,'w'):pass

			result=[True,""]		
		except Exception as e:
			result=[False,str(e)]

		return result

	#def changeMetaProtectionStatus

	def getRestoreCommand(self):

		cmd="LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive dpkg --configure -a; LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get update; LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install -f -y --allow-downgrades --allow-remove-essential --allow-change-held-packages"
		return cmd
	
	#def getRestoreCommand

#class UnlockerUpManager


if __name__=="__main__":
	
	dpkgunlocker=DpkgUnlockerManager()
