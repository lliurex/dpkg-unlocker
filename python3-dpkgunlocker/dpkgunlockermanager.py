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
			f=open(self.lockTokenPath,'w')
			upPid=os.getpid()
			f.write(str(upPid))
			f.close()
			
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

		if os.path.exists(self.lliurexUpLockTokenPath):
			f=open(self.lliurexUpLockTokenPath,'r')
			upPid=f.readline().split('\n')[0]
			if upPid !="":
				self.upPid=int(upPid)
				checkPid=psutil.pid_exists(self.upPid)
				if checkPid:
					code=1
				else:
					code=2
			else:
				code=1
		else:
			code=0

		return code	

	#def isLliurexUpLocked
	
	def isAptLocked(self):

		'''
		 0: Apt is not running
		 1: Apt is running
		 2: Apt is locked for previous failed process
		 4: Apt Daemon is locked
		 ''' 
		checkLock=False
		lsofData=self.checkAptdLock(self.aptLockTokenPath)

		if len(lsofData)>0:
			self.aptApdRun=self.findProcess("aptd")
			if self.aptApdRun!=None:
				for item in lsofData:
					if item==self.aptApdRun[0]["pid"]:
						code=4
						break
					else:
						checkLock=True	
			else:
				checkLock=True
		else:
			checkLock=True

		if checkLock:
			f= open(self.aptLockTokenPath, 'w')
			try:
				fcntl.lockf(f, fcntl.LOCK_EX|fcntl.LOCK_NB)
				code=0
					
			except IOError:
				self.aptRun=self.findProcess("apt-get")
				if self.aptRun!=None:
					code =1
				else:
					code=2

		return code	

	#def isAptLocked
		
	def isDpkgLocked(self):

		'''
		 0: Dpkgis not running
		 1: Dpkg is running
		 2: Dpkg is locked for previous failed process
		 3: Apt is running
		 4: Apt Daemon is running

		 ''' 
		checkLock=False
		lsofData=self.checkAptdLock(self.dpkgLockTokenPath)

		if len(lsofData)>0:
			self.dpkgApdRun=self.findProcess("aptd")
			if self.dpkgApdRun!=None:
				for item in lsofData:
					if item==self.dpkgApdRun[0]["pid"]:
						code=4
						break
					else:
						checkLock=True
			else:
				checkLock=True
		else:
			checkLock=True

		if checkLock:
			f= open(self.dpkgLockTokenPath, 'w')
			try:
				fcntl.lockf(f, fcntl.LOCK_EX|fcntl.LOCK_NB)
				code=0
				
			except IOError:
				self.dpkgRun=self.findProcess("dpkg")
				if self.dpkgRun!=None:
					code =1
				else:
					self.aptRun=self.findProcess("apt-get")
					if self.aptRun!=None:
						code=3
					else:
						code=2	

		return code		
			
	#def isAptLocked			

	def getProcessList(self,arg=None):
		
		self.processList=[]
		
		p=subprocess.Popen(["ps","aux"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]
		if type(output) is bytes:
			output=output.decode()

		lst=output.split("\n")
		lst.pop(0)
		
		for item in lst:
			processedLine=item.split(" ")
			tmp_list=[]
			
			if len(processedLine) >= 10:
				for object in processedLine:
					if object!="":
						tmp_list.append(object)
				processedLine=tmp_list
				
				process={}
				process["user"]=processedLine[0]
				process["pid"]=processedLine[1]
				process["cpu"]=processedLine[2]
				process["mem"]=processedLine[3]
				process["vsz"]=processedLine[4]
				process["rss"]=processedLine[5]
				process["tty"]=processedLine[6]
				process["stat"]=processedLine[7]
				process["start"]=processedLine[8]
				process["time"]=processedLine[9]
				cmd=""
				for line in processedLine[10:]:
					if cmd!="":
						cmd+=" "
					cmd+=line
				
				if arg=="aptd":
					if arg in cmd:
						process["command"]=cmd.split(" ")[1]
					else:		
						process["command"]=cmd.split(" ")[0]
				else:
					process["command"]=cmd.split(" ")[0]
				self.processList.append(process)

	#def getProcessList			

	def findProcess(self,filter):
		
		self.getProcessList(filter)
		retList=[]
		for process in self.processList:
			if filter in process["command"]:
				retList.append(process)
					
		if len(retList)>0:
			return retList
		else:
			return None

	#def findProcess	

	def checkAptdLock(self,lockfile):

		cmd="lsof -t "+lockfile
		p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()

		lsofData=output.split("\n")
		del lsofData[-1]

		return lsofData

	#def checkAptdLock	

	def checkingLocks(self):

		self.lockeds["Lliurex-Up"]=self.isLliurexUpLocked()
		self.lockeds["Dpkg"]=self.isDpkgLocked()
		self.lockeds["Apt"]=self.isAptLocked()

		return self.lockeds
	
	#def checkingLocks

	def getUnlockerCommand(self,kill=None):

		unlockInfo={}
		unlockerCommands={}
		commonCommand=""

		cont=0
		removeUp=False
		removeDpkg=False
		removeApt=False
		liveProcess=0

		if self.lockeds["Lliurex-Up"]!=0:
			if kill:
				removeUp=True
			else:
				if self.lockeds["Lliurex-Up"]==2:
					removeUp=True
				else:
					liveProcess+=1
		
		if removeUp:
			cmd="rm -f "+self.lliurexUpLockTokenPath
			unlockerCommands["Lliurex-Up"]=cmd
			cont+=1

		if self.lockeds["Dpkg"]!=0:
			if kill:
				removeDpkg=True
			else:
				if self.lockeds["Dpkg"]==2:
					removeDpkg=True
				else:
					liveProcess+=1
	
		if removeDpkg:
			cmd="rm -f " +self.dpkgLockTokenPath
			unlockerCommands["Dpkg"]=cmd
			cont+=1

		if self.lockeds["Apt"]!=0:
			if kill:
				removeApt=True
			else:
				if self.lockeds["Apt"]==2:
					removeApt=True
				else:
					liveProcess+=1

		if removeApt:
			cmd="rm -f " + self.aptLockTokenPath	
			unlockerCommands["Apt"]=cmd
			cont+=1

		if cont>0:
			if liveProcess==0:
				cmd="LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive dpkg --configure -a; LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get update; LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive apt-get install -f -y --allow-downgrades --allow-remove-essential --allow-change-held-packages"
				commonCommand=cmd

		unlockInfo["unlockCmd"]=unlockerCommands
		unlockInfo["commonCmd"]=commonCommand
		unlockInfo["liveProcess"]=liveProcess		

		return unlockInfo

	#def getUnlockedCommand

	def getKillerCommand(self):

		killerCommands={}

		if self.lockeds["Lliurex-Up"]==1:
			killerCommands["Lliurex-Up"]="kill -9 "+ str(self.upPid)

		if self.lockeds["Dpkg"]==1:
			killerCommands["Dpkg"]="kill -9 "+str(self.dpkgRun[0]["pid"])
		elif self.lockeds["Dpkg"]==3:
			killerCommands["Apt"]="kill -9 "+str(self.aptRun[0]["pid"])
				
		if self.lockeds["Apt"]==1:
			killerCommands["Apt"]="kill -9 " + str(self.aptRun[0]["pid"]) 

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
