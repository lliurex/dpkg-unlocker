#!/usr/bin/env python3

import os
import subprocess
import sys
import syslog

import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import signal
signal.signal(signal.SIGINT,signal.SIG_IGN)

class DpkgUnlockerCli(object):

	def __init__(self):

		self.dpkgUnlockerCore=DpkgUnlockerManager.DpkgUnlockerManager()
		self.dpkgUnlockerCore.checkingLocks()
		self.dpkgUnlockerCore.createLockToken()
		
		signal.signal(signal.SIGINT,self.handlerSignal)

	#def __init__		

	def showServices(self,clean=None):

		if clean==None:
			msgLog="Dpkg-Unlocker-Cli. Action: showInfo"
			self._writeLog(msgLog)

		msgLog=f"Initial services status: {self.dpkgUnlockerCore.lockeds}"
		self._writeLog(msgLog)

		msgUp=self._getMsgStatus(self.dpkgUnlockerCore.lockeds["Lliurex-Up"])
		msgDpkg=self._getMsgStatus(self.dpkgUnlockerCore.lockeds["Dpkg"])		
		msgApt=self._getMsgStatus(self.dpkgUnlockerCore.lockeds["Apt"])		
		
		if clean==None:
			self.dpkgUnlockerCore.cleanLockToken()
			
		print ("  [Dpkg-Unlocker-Cli]: Current services information availabled:")
		print (f"    - Lliurex-Up: {msgUp}")
		print (f"    - Dpkg: {msgDpkg}")
		print (f"    - Apt: {msgApt}")

	#def showServices

	def _getMsgStatus(self,code):

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

	#def _getMsgStatus		
	
	def unlock(self,mode,kill):

		self.unlockInfo=self.dpkgUnlockerCore.getUnlockerCommand(kill)
		msgLog=f"Dpkg-Unlocker-Cli. Action: unlock. Mode of execution: Unnattended: {mode}; Kill: {kill}"
		self._writeLog(msgLog)
		self.showServices(False)
		
		if len(self.unlockInfo["unlockCmd"])==0:
			msgLog="All processes seem correct. Nothing to do"
			return self._sendFeedBack(msgLog,0)

		if self.unlockInfo["liveProcess"]!=0 and not kill:
			msgLog="Some process are running. Wait a moment and try again"
			return self._sendFeedBack(msgLog,2)

		response="yes" if mode else input('  [Dpkg-Unlocker-Cli]: Do you want to execute the unlocking process (yes/no)): ')

		if not response.startswith('y'):
			msgLog="Unlocking process cancelled"
			return self._sendFeedBack(msgLog,0)

		if kill and not self._killProcess():
			return self._sendFeedBack(None,1)

		if not self._unlockProcess(kill):
			return self._sendFeedBack(None,1)

		msgLog="Unlocking process finished successfully"
		
		return self._sendFeedBack(msgLog,0)
					

	def _killProcess(self):
	
		print("  [Dpkg-Unlocker-Cli]: Killing the blocked processes...")

		killerCommands=self.dpkgUnlockerCore.getKillerCommand()

		if len(killerCommands)==0:
			msgLog="Killing process. Nothing to do"
			self._sendFeedBack(msgLog,None)
			return True

		for item,command in killerCommands.items():
			msgLog=f"Killing process: {item}"
			self._sendFeedBack(msgLog,None)
			p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
			_,perror=p.communicate()
			error=self._readErrorOutput(perror)
			if error["result"]:
				msgLog=f"Killing process. Error killing {item}: {error['content']}"
				self._sendFeedBack(msgLog,None)
				return False

		return True

	#def killeProcess

	def _unlockProcess(self,kill):

		if not self.unlockInfo["unlockCmd"]:
			msgLog="Unlocking process.Nothing to do"
			self._sendFeedBack(msgLog,None)
			return True

		for command,cmdScript in self.unlockInfo["unlockCmd"].items():
			msgLog=f"Unlocking process. Removing {command} lock file"
			self._sendFeedBack(msgLog,None)
			p=subprocess.Popen(cmdScript,shell=True,stderr=subprocess.PIPE)
			_,perror=p.communicate()
			error=self._readErrorOutput(perror)
			
			if error["result"]:
				msgLog=f"Unlocking process. Error removing {command} lock file: {error['content']}"
				self._sendFeedBack(msgLog,None)
				return False

		msgLog="Unlocking proces. Fixing the system"
		self._sendFeedBack(msgLog,None)
		p=subprocess.Popen(self.unlockInfo["commonCmd"],shell=True,stderr=subprocess.PIPE)
		_,perror=p.communicate()
		error=self._readErrorOutput(perror)
		
		if error["result"]:
			msgLog=f"Unlocking proces. Error fixing the system: {error['content']}"
			self._sendFeedBack(msgLog,None)
			return False
		
		return True	

	#def _unlockProcess				

	def _readErrorOutput(self,output):

		if isinstance(output,bytes):
			output=output.decode(errors="ignore")

		hasError=any("E: " in line for line in output.split("\n"))

		return {
			"content":output,
			"result":hasError
		}

	#def _readErrorOutput			

	def handlerSignal(self,signal,frame):

		msgLog="Cancel process with Ctrl+C signal"
		sys.exit(self._sendFeedBack(msgLog,0))
		
	#def handlerSignal

	def showProtection(self,clean=None):

		self.currentProtectionStatus=self.dpkgUnlockerCore.checkMetaProtection()
		if clean is None:
			msgLog="Dpkg-Unlocker-Cli. Action: showProtection"
			self._writeLog(msgLog)

		msgProtection="System metapackage protection"
		isEnabled=self.currentProtectionStatus
		msgHead="WARNING " if not isEnabled else ""
		msgStatus="is enabled" if isEnabled else "is disabled"

		if clean is None:
			self.dpkgUnlockerCore.cleanLockToken()
		
		print (f"  [Dpkg-Unlocker-Cli]: Current configuration: {msgHead}{msgProtection} {msgStatus}")
		
		self._writeLog(f"Inital status: {msgProtection} enabled: {isEnabled}")

	#def showProtection

	def disableProtection(self,mode):

		msgLog=f"Dpkg-Unlocker-Cli. Action: disableProtection.Mode of execution: Unnattended: {mode}"
		self._writeLog(msgLog)
		self.showProtection(False)

		if not self.currentProtectionStatus:
			msgLog="System metapackage protection is already disable. Nothing to do"
			return self._sendFeedBack(msgLog,0)
		
		print("  [Dpkg-Unlocker-Cli]: WARNING Disabling system metapackage protection can cause certain applications to be uninstalled automatically and cause system inconsistencies")
		
		response="yes" if mode else input('  [Dpkg-Unlocker-Cli]: Do you want to disable system metapackage protection?(yes/no)')

		if not response.startswith('y'):
			msgLog="Action cancelled"
			return self._sendFeedBack(msgLog,0)

		result=self.dpkgUnlockerCore.changeMetaProtectionStatus(False)
		msgLog=f"Disable system metapackage protection result: {result}"
		self._writeLog(msgLog)

		if result[0]:
			msgLog= "System metapackage protecion is now disable"
			return self._sendFeedBack(msgLog,0)
		
		msgLog="Error disabling system metapackage protection. Details: {result[1]}"
		return self._sendFeedBack(msgLog,1)
				

	#def disableProtection

	def enableProtection(self,mode):

		msgLog=f"Dpkg-Unlocker-Cli. Action: enable Protection.Mode of execution: Unnattended: {mode}"
		self._writeLog(msgLog)
		self.showProtection(False)
		
		if self.currentProtectionStatus:
			msgLog="System metapackage protection is already enable. Nothing to do"
			return self._sendFeedBack(msgLog,0)

		response="yes" if mode else input('  [Dpkg-Unlocker-Cli]: Do you want to enable system metapackage protection?(yes/no)')

		if not response.startswith('y'):
			msgLog="Action cancelled"
			return self._sendFeedBack(msgLog,0)

		result=self.dpkgUnlockerCore.changeMetaProtectionStatus(True)
		msgLog=f"Enable system metapackage protection result: {result}"
		self._writeLog(msgLog)

		if result[0]:
			msgLog="System metapackage protecion is now enable"
			return self._sendFeedBack(msgLog,0)

		msgLog=f"Error enabling system metapackage protection. Details: {result[1]}"
		return self._sendFeedBack(msgLog,1)

	#def enableProtection

	def restore(self,mode):

		self.unlockInfo=self.dpkgUnlockerCore.getUnlockerCommand(False)
		msgLog=f"Dpkg-Unlocker-Cli. Action: restore. Mode of execution: Unnattended: {mode}"
		self._writeLog(msgLog)
		self.showServices(False)
		
		if len(self.unlockInfo["unlockCmd"])!=0:
			msgLog="Some processes seem locked. Unable to launch the services restore process"
			return self._sendFeedBack(msgLog,0)
	
		if self.unlockInfo["liveProcess"]!=0:
			msgLog="Some process are running. Wait a moment and try again"
			return self._sendFeedBack(msgLog,2)

		response="yes" if mode else input('  [Dpkg-Unlocker-Cli]: Do you want to execute the services restore process (yes/no)): ')

		if not response.startswith('y'):
			msgLog="Restoring process cancelled"
			return self._sendFeedBack(msgLog,0)

		result=self._restoreProcess()
		if result[0]:
			msgLog="Restore process finished successfully"
			return self._sendFeedBack(msgLog,0)

		msgLog=f"Restoring process. Error: {result[1]}"
		return self._sendFeedBack(msgLog,1)
		
	#def restore

	def _restoreProcess(self):

		command=self.dpkgUnlockerCore.getRestoreCommand()
		msgLog="Restoring services"
		self._sendFeedBack(msgLog,None)

		p=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)
		_,perror=p.communicate()
		error=self._readErrorOutput(perror)
		if error["result"]:
			return [False,error["content"]]

		return [True,""]

	#def _restoreProcess

	def _sendFeedBack(self,message,returnCode):

		if message:
			self._writeLog(message)
			print(f"  [Dpkg-Unlocker-Cli]: {message}")

		if returnCode is not None:
			self.dpkgUnlockerCore.cleanLockToken()
			return returnCode

	#def _sendFeedBack

	def _writeLog(self,msg):

		syslog.openlog("DpkgUnlocker")
		syslog.syslog(msg)
																
		return

	#def _writeLog	

#def DpkgUnlockerCli	