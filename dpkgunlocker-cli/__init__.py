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
		self.dpkgUnlockerCore.createLockToken()
		
		signal.signal(signal.SIGINT,self.handlerSignal)

	#def __init__		

	def showServices(self,clean=None):

		if clean==None:
			msgLog="Dpkg-Unlocker-Cli. Action: showInfo"
			self.writeLog(msgLog)

		msgLog="Initial services status: %s"%self.dpkgUnlockerCore.lockeds
		self.writeLog(msgLog)

		msgUp=self.getMsgStatus(self.dpkgUnlockerCore.lockeds["Lliurex-Up"])
		msgDpkg=self.getMsgStatus(self.dpkgUnlockerCore.lockeds["Dpkg"])		
		msgApt=self.getMsgStatus(self.dpkgUnlockerCore.lockeds["Apt"])		
		
		if clean==None:
			self.dpkgUnlockerCore.cleanLockToken()
			
		print ("  [Dpkg-Unlocker-Cli]: Current services information availabled:")
		print ("    - Lliurex-Up: " + msgUp)
		print ("    - Dpkg: " + msgDpkg)
		print ("    - Apt: " + msgApt)

	#def showServices

	def getMsgStatus(self,code):

		if code==0:
			msg="Unlocked"
		elif code==1:
			msg="Locked. Currently executing"
		elif code==2:
			msg="Locked. Not process found"	
		elif code==3:
			msg="Locked. Apt Currently executing"	
		elif code==4:
			msg="Locked: Apt daemon currently executing"	

		return msg

	#def getMsgStatus		
	
	def unlock(self,mode,kill):

		self.unlockInfo=self.dpkgUnlockerCore.getUnlockerCommand(kill)
		msgLog="Dpkg-Unlocker-Cli. Action: unlock. Mode of execution: Unnattended: "+ str(mode) + "; Kill: "+str(kill)
		self.writeLog(msgLog)
		self.showServices(False)
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
							msgLog="Unlocking process finished successfully"
							self.writeLog(msgLog)
							self.dpkgUnlockerCore.cleanLockToken()
							print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
							return 0
						else:
							self.dpkgUnlockerCore.cleanLockToken()
							return 1
					else:
						self.dpkgUnlockerCore.cleanLockToken()
						return 1
				else:
					msgLog="Unlocking process cancelled"
					self.writeLog(msgLog)
					self.dpkgUnlockerCore.cleanLockToken()
					print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
					return 0
			else:
				msgLog="Some process are running. Wait a moment and try again"
				self.writeLog(msgLog)
				self.dpkgUnlockerCore.cleanLockToken()
				print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
				return 2
		else:
			msgLog="All processes seem correct. Nothing to do"
			self.writeLog(msgLog)
			self.dpkgUnlockerCore.cleanLockToken()
			print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
			return 0

	#def unlock					

	def killProcess(self):
	
		print ("  [Dpkg-Unlocker-Cli]: Killing the blocked processes...")

		killerCommands=self.dpkgUnlockerCore.getKillerCommand()

		if len(killerCommands)>0:
			for item in killerCommands:
				msgLog="Killing process: "+ item
				self.writeLog(msgLog)
				print ("  [Dpkg-Unlocker-Cli]: "+ msgLog)
				p=subprocess.Popen(killerCommands[item],shell=True,stderr=subprocess.PIPE)
				output=p.communicate()
				error=self.readErrorOutput(output[1])
				if error["result"]:
					msgLog="Killing process. Error killing " + item +": "+str(error["content"])
					print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
					self.writeLog(msgLog)
					return False
		else:
			msgLog="Killing process. Nothing to do"
			print ("  [Dpkg-Unlocker-Cli]: "+ msgLog)
			self.writeLog(msgLog)
		return True

	#def killeProcess

	def unlockProcess(self,kill):

		if len(self.unlockInfo["unlockCmd"])>0:
			for command in self.unlockInfo["unlockCmd"]:
				msgLog="Unlocking process. Removing "+command + " lock file"
				self.writeLog(msgLog)
				print ("  [Dpkg-Unlocker-Cli]: " +msgLog)
				p=subprocess.Popen(self.unlockInfo["unlockCmd"][command],shell=True,stderr=subprocess.PIPE)
				output=p.communicate()
				error=self.readErrorOutput(output[1])
				if error["result"]:
					msgLog="Unlocking process. Error removing "+command + " lock file: " + str(error["content"])
					print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
					self.writeLog(msgLog)
					return False

			msgLog="Unlocking proces. Fixing the system"
			self.writeLog(msgLog)
			print ("  [Dpkg-Unlocker-Cli]: "+ msgLog)
			p=subprocess.Popen(self.unlockInfo["commonCmd"],shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error["result"]:
				msgLog="Unlocking proces. Error fixing the system: "+str(error["content"])
				print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
				self.writeLog(msgLog)
				return False
		else:
			msgLog="Unlocking process.Nothing to do"
			self.writeLog(msgLog)
			print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
		
		return True

	#def unlockProcess				

	def readErrorOutput(self,output):

		readError={}
		cont=0
		if type(output) is bytes:
			output=output.decode()
		lines=output.split('\n')
		readError["content"]=output
		for line in lines:
			if "E: " in line:
				cont=cont+1

		if cont>0:
			readError["result"]=True
		else:
			readError["result"]=False

		return readError

	#def readErrorOutput			

	def handlerSignal(self,signal,frame):

		msgLog="Cancel process with Ctrl+C signal"
		self.dpkgUnlockerCore.cleanLockToken()
		self.writeLog(msgLog)
		print("\n  [Dpkg-Unlocker-Cli]: "+msgLog)
		sys.exit(0)

	#def handlerSignal

	def showProtection(self,clean=None):

		self.currentProtectionStatus=self.dpkgUnlockerCore.checkMetaProtection()
		msgHead=""

		if clean==None:
			msgLog="Dpkg-Unlocker-Cli. Action: showProtection"
			self.writeLog(msgLog)

		msgProtection="System metapackage protection"

		if not self.currentProtectionStatus:
			msgStatus="is disabled"
			msgHead="WARNING "
		else:
			msgStatus="is enabled"

		if clean==None:
			self.dpkgUnlockerCore.cleanLockToken()
		
		print ("  [Dpkg-Unlocker-Cli]: Current configuration: %s%s %s"%(msgHead,msgProtection,msgStatus))
		
		self.writeLog("Inital status: %s enabled: %s"%(msgProtection,str(self.currentProtectionStatus)))

	#def showProtection

	def disableProtection(self,mode):

		msgLog="Dpkg-Unlocker-Cli. Action: disableProtection.Mode of execution: Unnattended: %s"%(str(mode))
		self.writeLog(msgLog)
		self.showProtection(False)

		if not self.currentProtectionStatus:
			msgLog="System metapackage protection is already disable. Nothing to do"
			self.writeLog(msgLog)
			print("  [Dpkg-Unlocker-Cli]: %s"%msgLog)
			self.dpkgUnlockerCore.cleanLockToken()
			return 0
		else:
			print("  [Dpkg-Unlocker-Cli]: WARNING Disabling system metapackage protection can cause certain applications to be uninstalled automatically and cause system inconsistencies")
			if not mode:
				response=input("  [Dpkg-Unlocker-Cli]: Do you want to disable system metapackage protection?(yes/no)")
			else:
				response='yes'

			if response.startswith('y'):
				result=self.dpkgUnlockerCore.changeMetaProtectionStatus(False)
				msgLog="Disable system metapackage protection result: %s"%str(result)
				self.writeLog(msgLog)
				self.dpkgUnlockerCore.cleanLockToken()
				if result[0]:
					print ("  [Dpkg-Unlocker-Cli]: System metapackage protecion is now disable")
					return 0
				else:
					print("   [Dpkg-Unlocker-Cli]: Error disabling system metapackage protection. Details: %s"%str(result[1]))
					return 1
			else:
				msgLog="Action cancelled"
				print("  [Dpkg-Unlocker-Cli]: %s"%msgLog)
				self.writeLog(msgLog)
				self.dpkgUnlockerCore.cleanLockToken()
				return 0

	#def disableProtection

	def enableProtection(self,mode):

		msgLog="Dpkg-Unlocker-Cli. Action: enable Protection.Mode of execution: Unnattended: %s"%(str(mode))
		self.writeLog(msgLog)
		self.showProtection(False)
		
		if self.currentProtectionStatus:
			msgLog="System metapackage protection is already enable. Nothing to do"
			self.writeLog(msgLog)
			print ("  [Dpkg-Unlocker-Cli]: %s"%msgLog)
			self.dpkgUnlockerCore.cleanLockToken()
			return 0
		else:
			if not mode:
				response=input("  [Dpkg-Unlocker-Cli]: Do you want to enable system metapackage protection?(yes/no)")
			else:
				response='yes'

			if response.startswith('y'):
				result=self.dpkgUnlockerCore.changeMetaProtectionStatus(True)
				msgLog="Enable system metapackage protection result: %s"%str(result)
				self.writeLog(msgLog)
				self.dpkgUnlockerCore.cleanLockToken()
				if result[0]:
					print ("  [Dpkg-Unlocker-Cli]: System metapackage protecion is now enable")
					return 0
				else:
					print("   [Dpkg-Unlocker-Cli: Error enabling system metapackage protection. Details: %s"%str(result[1]))
					return 1
			else:
				msgLog="Action cancelled"
				print("  [Dpkg-Unlocker-Cli]: %s"%msgLog)
				self.dpkgUnlockerCore.cleanLockToken()
				self.writeLog(msgLog)
				return 0

	#def enableProtection

	def restore(self,mode):

		self.unlockInfo=self.dpkgUnlockerCore.getUnlockerCommand(False)
		msgLog="Dpkg-Unlocker-Cli. Action: restore. Mode of execution: Unnattended: "+ str(mode)
		self.writeLog(msgLog)
		self.showServices(False)
		result=True
		
		if len(self.unlockInfo["unlockCmd"])==0:

			if self.unlockInfo["liveProcess"]==0:
				if not mode:
					response=input('  [Dpkg-Unlocker-Cli]: Do you want to execute the services restore process (yes/no)): ')
				else:
					response='yes'
				if response.startswith('y'):
					result=self.restoreProcess()
					if result:
						msgLog="Restore process finished successfully"
						self.writeLog(msgLog)
						self.dpkgUnlockerCore.cleanLockToken()
						print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
						return 0
					else:
						self.dpkgUnlockerCore.cleanLockToken()
						return 1
				else:
					msgLog="Restoring process cancelled"
					self.writeLog(msgLog)
					self.dpkgUnlockerCore.cleanLockToken()
					print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
					return 0
			else:
				msgLog="Some process are running. Wait a moment and try again"
				self.writeLog(msgLog)
				self.dpkgUnlockerCore.cleanLockToken()
				print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
				return 2
		else:
			msgLog="Some processes seem locked. Unable to launch the services restore process"
			self.writeLog(msgLog)
			self.dpkgUnlockerCore.cleanLockToken()
			print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
			return 0

	#def restore

	def restoreProcess(self):

		command=self.dpkgUnlockerCore.getRestoreCommand()
		msgLog="Restoring services"
		self.writeLog(msgLog)
		print ("  [Dpkg-Unlocker-Cli]: " +msgLog)
		p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
		output=p.communicate()
		error=self.readErrorOutput(output[1])
		if error["result"]:
			msgLog="Restoring process. Error: " + str(error["content"])
			print ("  [Dpkg-Unlocker-Cli]: "+msgLog)
			self.writeLog(msgLog)
			return False

		return True

	#def restoreProcess

	def writeLog(self,msg):

		syslog.openlog("DpkgUnlocker")
		syslog.syslog(msg)
																
		return

	#def writeLog	

#def DpkgUnlockerCli	