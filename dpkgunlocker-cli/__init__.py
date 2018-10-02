#!/usr/bin/env python3

import os
import subprocess
import sys
import syslog

import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import signal
signal.signal(signal.SIGINT,signal.SIG_IGN)

class DpkgUnlockerCli(object):

	def __init__(self,app):

		self.dpkgUnlockerCore=DpkgUnlockerManager.DpkgUnlockerManager()
		self.dpkgUnlockerCore.checkingLocks()
		signal.signal(signal.SIGINT,self.handler_signal)


	#def __init__		

	def showInfo(self,mode,kill,clean=None):

		msg_log="Dpkg-Unlocker-Cli.Mode of execution: Unnattended: "+ str(mode) + "; Kill: "+str(kill)
		self.write_log(msg_log)

		msg_up=self.get_msg_status(self.dpkgUnlockerCore.lockeds["Lliurex-Up"])
		msg_log="Lliurex-Up: "+ msg_up
		self.write_log(msg_log)

		msg_dpkg=self.get_msg_status(self.dpkgUnlockerCore.lockeds["Dpkg"])		
		msg_log="Dpkg: "+msg_dpkg
		self.write_log(msg_log)
	
		msg_apt=self.get_msg_status(self.dpkgUnlockerCore.lockeds["Apt"])		
		msg_log="Apt: "+msg_log
		self.write_log(msg_log)	

		if clean==None:
			self.dpkgUnlockerCore.cleanLockToken()
			
		print ("  [Dpkg-Unlocker-Cli]: Information availabled:")
		print ("    - Lliurex-Up: " + msg_up)
		print ("    - Dpkg: " + msg_dpkg)
		print ("    - Apt: " + msg_apt)



	#def showInfo

	def get_msg_status(self,code):


		if code==0:
			msg="Unlocked"
		elif code==1:
			msg="Locked. Currently executing"
		elif code==2:
			msg="Locked. Not process found"	
		elif code==3:
			msg="Locked. Apt Currently executing"	

		return msg	
	#def get_msg_status		
	

	def unlock(self,mode,kill):

		self.unlockInfo=self.dpkgUnlockerCore.getUnlockerCommand(kill)
		self.showInfo(mode,kill,False)
		result=True
		
		if len(self.unlockInfo["unlockCmd"])>0:

			if self.unlockInfo["liveProcess"]==0 or kill:
				if not mode:
					response=input('  [Dpkg-Unlocker-Cli]: Do you want to execute the unlocking process (yes/no)): ')

				else:
					response='yes'

				if response.startswith('y'):
					
					if kill:
						result=self.killProcess()
					if result:
						result=self.unlockProcess(kill)
						if result:
							msg_log="Unlocking process finished successfully"
							self.write_log(msg_log)
							self.dpkgUnlockerCore.cleanLockToken()
							print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
							return 0
						else:
							self.dpkgUnlockerCore.cleanLockToken()
							return 1

					else:
						self.dpkgUnlockerCore.cleanLockToken()
						return 1
				else:
					msg_log="Unlocking process cancelled"
					self.write_log(msg_log)
					self.dpkgUnlockerCore.cleanLockToken()
					print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
					return 0
			else:
				msg_log="Some process are running. Wait a moment and try again"
				self.write_log(msg_log)
				self.dpkgUnlockerCore.cleanLockToken()
				print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
				return 2

		else:
			msg_log="All processes seem correct. Nothing to do"
			self.write_log(msg_log)
			self.dpkgUnlockerCore.cleanLockToken()
			print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
			return 0


	#def unlock					


	def killProcess(self):
	
		print ("  [Dpkg-Unlocker-Cli]: Killing the blocked processes...")

		killerCommands=self.dpkgUnlockerCore.getKillerCommand()

		if len(killerCommands)>0:
			for item in killerCommands:
				msg_log="Killing process: "+ item
				self.write_log(msg_log)
				print ("  [Dpkg-Unlocker-Cli]: "+ msg_log)
				p=subprocess.Popen(killerCommands[item],shell=True,stderr=subprocess.PIPE)
				output=p.communicate()
				error=self.readErrorOutput(output[1])
				if error["result"]:
					msg_log="Killing process. Error killing " + item +": "+str(error["content"])
					print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
					self.write_log(msg_log)
					return False
		else:
			msg_log="Killing process. Nothing to do"
			print ("  [Dpkg-Unlocker-Cli]: "+ msg_log)
			self.write_log(msg_log)
			
		
		return True

	#def killeProcess
	

	def unlockProcess(self,kill):

		
		#unlockedCommands,commonCommand=self.dpkgUnlockerCore.getUnlockedCommand(kill)

		if len(self.unlockInfo["unlockCmd"])>0:

			for command in self.unlockInfo["unlockCmd"]:
				msg_log="Unlocking process. Removing "+command + " lock file"
				self.write_log(msg_log)
				print ("  [Dpkg-Unlocker-Cli]: " +msg_log)
				p=subprocess.Popen(self.unlockInfo["unlockCmd"][command],shell=True,stderr=subprocess.PIPE)
				output=p.communicate()
				error=self.readErrorOutput(output[1])
				if error["result"]:
					msg_log="Unlocking process. Error removing "+command + " lock file: " + str(error["content"])
					print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
					self.write_log(msg_log)
					return False

			msg_log="Unlocking proces. Fixing the system"
			self.write_log(msg_log)
			print ("  [Dpkg-Unlocker-Cli]: "+ msg_log)
			p=subprocess.Popen(self.unlockInfo["commonCmd"],shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error["result"]:
				msg_log="Unlocking proces. Error fixing the system: "+str(error["content"])
				print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
				self.write_log(msg_log)
				return False
		else:
			msg_log="Unlocking process.Nothing to do"
			self.write_log(msg_log)
			print ("  [Dpkg-Unlocker-Cli]: "+msg_log)
							
		
		return True

	#def unlockProcess				

	
	def readErrorOutput(self,output):

		readError={}
		cont=0
		if type(output) is bytes:
			output=output.decode()
		lines=output.split('\n')
		readError["content"]=lines
		for line in lines:
			if "E: " in line:
				cont=cont+1

		if cont>0:
			readError["result"]=True
		else:
			readError["result"]=False

		return readError


	#def readErrorOutput			


	def handler_signal(self,signal,frame):

		msg_log="Cancel process with Ctrl+C signal"
		self.dpkgUnlockerCore.cleanLockToken()
		self.write_log(msg_log)
		print("\n  [Dpkg-Unlocker-Cli]: "+msg_log)
		sys.exit(0)

	#def handler_signal
	

	def write_log(self,msg):

		syslog.openlog("DpkgUnlocker")
		syslog.syslog(msg)
																
		return

	#def write_log	

#def DpkgUnlockerCli	