#!/usr/bin/env python3

import os
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

		self.lockeds={}

	#def __init__	


	def createLockToken(self):

		if not os.path.exists(self.lockTokenPath):
			f=open(self.lockTokenPath,'w')
			up_pid=os.getpid()
			f.write(str(up_pid))
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
			up_pid=f.readline().split('\n')[0]
			if up_pid !="":
				self.up_pid=int(up_pid)
				check_pid=psutil.pid_exists(self.up_pid)
				if check_pid:
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
		 ''' 

		f= open(self.aptLockTokenPath, 'w')
		try:
			fcntl.lockf(f, fcntl.LOCK_EX|fcntl.LOCK_NB)
			code=0
		except IOError:
			self.apt_run=self.find_process("apt-get")
			if self.apt_run!=None:
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

		 ''' 

		f= open(self.dpkgLockTokenPath, 'w')
		try:
			fcntl.lockf(f, fcntl.LOCK_EX|fcntl.LOCK_NB)
			code=0
		except IOError:
			self.dpkg_run=self.find_process("dpkg")
			if self.dpkg_run!=None:
				code =1
			else:
				self.apt_run=self.find_process("apt-get")
				if self.apt_run!=None:
					code=3
				else:
					code=2	

		return code		
			

	#def isAptLocked			


	def get_process_list(self):
		
		self.process_list=[]
		
		p=subprocess.Popen(["ps","aux"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]
		if type(output) is bytes:
			output=output.decode()

		lst=output.split("\n")
		lst.pop(0)
		
		for item in lst:
			processed_line=item.split(" ")
			tmp_list=[]
			
			if len(processed_line) >= 10:
				for object in processed_line:
					if object!="":
						tmp_list.append(object)
				processed_line=tmp_list
				
				process={}
				process["user"]=processed_line[0]
				process["pid"]=processed_line[1]
				process["cpu"]=processed_line[2]
				process["mem"]=processed_line[3]
				process["vsz"]=processed_line[4]
				process["rss"]=processed_line[5]
				process["tty"]=processed_line[6]
				process["stat"]=processed_line[7]
				process["start"]=processed_line[8]
				process["time"]=processed_line[9]
				cmd=""
				for line in processed_line[10:]:
					if cmd!="":
						cmd+=" "
					cmd+=line
					
				process["command"]=cmd.split(" ")[0]
				self.process_list.append(process)

	#def get_process_list			

	def find_process(self,filter):
		
		self.get_process_list()
		ret_list=[]
		for process in self.process_list:
			if filter in process["command"]:
				ret_list.append(process)
				
				
		if len(ret_list)>0:
			return ret_list
		else:
			return None

	#def find_process	


	def checkingLocks(self):

		self.createLockToken()
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
			killerCommands["Lliurex-Up"]="kill -9 "+ str(self.up_pid)

		if self.lockeds["Dpkg"]==1:
			killerCommands["Dpkg"]="kill -9 "+str(self.dpkg_run[0]["pid"])
		elif self.lockeds["Dpkg"]==3:
			killerCommands["Apt"]="kill -9 "+str(self.apt_run[0]["pid"])
				
				
		if self.lockeds["Apt"]==1:
			killerCommands["Apt"]="kill -9 " + str(self.apt_run[0]["pid"]) 

		return killerCommands

	#def getKillerCommand
	
		

#class UnlockerUpManager


if __name__=="__main__":
	
	dpkgunlocker=DpkgUnlockerManager()
