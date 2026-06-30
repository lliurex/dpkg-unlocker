#!/usr/bin/python3

import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import os
import subprocess
import shutil
import sys
import syslog
import json
import codecs
import tempfile
import pwd
import grp


class UnlockerManager:

	KIRIGAMI_MSG_OK=0
	KIRIGAMI_MSG_ERROR=1
	KIRIGAMI_MSG_WARNING=2
	KIRIGAMI_MSG_INFO=3

	def __init__(self):

		self.unlockerCore=DpkgUnlockerManager.DpkgUnlockerManager()
		self.unlockerCore.createLockToken()		
		self.debug=True
		self.servicesData=[]
		self.sessionLang=""
		self.isThereALock=False
		self.areLiveProcess=False
		self.KonsoleLog="/tmp/DpkgUnlocker_KonsoleLog.txt"
		self.getSessionLang()
		self.cleanEnvironment()
		self.metaProtectionEnabled=True
		self.runPkexec=True
		self._isRunPkexec()
		self.clearCache()

	#def __init__

	def _isRunPkexec(self):

		if 'PKEXEC_UID' not in os.environ:
			self.runPkexec=False

	#def _isRunPkexec

	def loadInfo(self):

		info=self.unlockerCore.checkingLocks()
		self.manageServiceInfo(info)
		self.getMetaProtectionStatus()
		
	#def loadInfo

	def getMetaProtectionStatus(self):

		self.metaProtectionEnabled=self.unlockerCore.checkMetaProtection()

	#def getMetaProtectionStatus

	def manageServiceInfo(self,info):

		okStatus={0,1,3,4}
		runningStatus={1,3,4}

		count=0
		liveProcess=0
		self.servicesData=[]
		
		for serviceId,statusCode in info.items():
			self.servicesData.append(
				{
				"serviceId":serviceId,
				"statusCode":statusCode
				}
			)
			
			if statusCode in okStatus:
				count+=1 
			if statusCode in runningStatus:
				liveProcess+=1 

		self.areLiveProcess=liveProcess > 0

		if count == len(info) or liveProcess == len(info):
			self.isThereALock=False
		else:
			self.isThereALock=True
		if liveProcess>0:
			self.areLiveProcess=True
		
	#def manageServiceInfo

	def getSessionLang(self):

		lang=os.environ["LANG"]
		
		if 'valencia' in lang:
			self.sessionLang="ca@valencia"
		else:
			self.sessionLang="es"

	#def getSessionLang

	def cleanEnvironment(self):

		if os.path.exists(self.KonsoleLog):
			os.remove(self.KonsoleLog)

	#def cleanEnvironment

	def initUnlockerProcesses(self):

		self.removeLlxupLockLaunched=False
		self.removeLlxupLockDone=False

		self.removeDpkgLockLaunched=False
		self.removeDpkgLockDone=False

		self.removeAptLockLaunched=False
		self.removeAptLockDone=False

		self.fixingSystemLaunched=False
		self.fixingSystemDone=False

	#def init_unlocker_processes	

	def createProcessToken(self,command,action):

		if action=="Lliurex-Up":
			self.tokenLlxupProcess=self._getTempFile('LlxUp')
			remove_tmp=f' rm -f {self.tokenLlxupProcess};\n'
			
		elif action=="Dpkg":
			self.tokenDpkgProcess=self._getTempFile('Dpkg')
			remove_tmp=f' rm -f {self.tokenDpkgProcess};\n'

		elif action=="Apt":
			self.tokenAptProcess=self._getTempFile('Apt')	
			remove_tmp=f' rm -f {self.tokenAptProcess};\n'
			
		elif action=="Fixing":
			self.tokenFixingProcess=self._getTempFile('Fixing')	
			remove_tmp=f' rm -f {self.tokenFixingProcess};\n'

		elif action=="Restore":
			self.tokenRestoreProcess=self._getTempFile('Restore')
			remove_tmp=f' rm -f {self.tokenRestoreProcess};\n'
					
		cmd=command+remove_tmp
		
		return cmd

	#def create_process_token

	def _getTempFile(self,action):

		suffixName=f"_{action}"
		tmpFile=tempfile.NamedTemporaryFile(suffix=suffixName,delete=False)
		tmpFile.close()

		return tmpFile.name

	#def _getTempFile	

	def createResultToken(self,command,action):

		if action=="Lliurex-Up":
			self.tokenLlxupResult=self._getTempFile('LlxUp')
			result_tmp=f' echo $? > {self.tokenLlxupResult})'
			
		elif action=="Dpkg":
			self.tokenDpkgResult=self._getTempFile('Dpkg')
			result_tmp=f' echo $? > {self.tokenDpkgResult})'

		elif action=="Apt":
			self.tokenAptResult=self._getTempFile('Apt')	
			result_tmp=f' echo $? > {self.tokenAptResult})'
			
		elif action=="Fixing":
			self.tokenFixingResult=self._getTempFile('Fixing')	
			result_tmp=f' echo $? > {self.tokenFixingResult})'

		elif action=="Restore":
			self.tokenRestoreResult=self._getTempFile('Restore')
			result_tmp=f' echo $? > {self.tokenRestoreResult})'	
		
		cmd=f"(('{command}');{result_tmp} '2>&1 | tee -a {self.KonsoleLog};"
		
		return cmd	

	#def createResultToken	

	def getUnlockerCommand(self):

		self.unlockInfo=self.unlockerCore.getUnlockerCommand()

	#def getUnlockerCommand

	def execCommand(self,action,typeCmd):

		command=""
		if typeCmd=="remove":
			command=self.unlockInfo.get("unlockCmd",{}).get(action,"")
		elif typeCmd=="restore":
			command=self.restoreCommand
		else:
			command=self.unlockInfo.get("commonCmd",{})

		length=len(command)
		
		if command:
			command=self.createResultToken(command,action)
			command=self.createProcessToken(command,action)
		else:
			statusFlag={
				"Lliurex-Up": "removeLlxupLockDone",
				"Dpkg": "removeDpkgLockDone",
				"Apt": "removeAptLockDone",
				"Fixing": "fixingSystemDone",
				"Restore": "restoreDone"
			}

			if action in statusFlag:
				setattr(self,statusFlag[action],True)
			
		return command
	
	#def exec_command			
	
	def checkProcess(self,action):

		result=True

		actionFlags={
			"Lliurex-Up": "tokenLlxupResult",
			"Dpkg": "tokenDpkgResult",
			"Apt": "tokenAptResult",
			"Fixing": "tokenFixingResult",
			"Restore": "tokenRestoreResult"
		}

		tmpToken=actionFlags.get(action)

		if not tmpToken:
			return result

		token=getattr(self,tmpToken)
					
		if not os.path.exists(token):
			return True

		try:
			with open(token,'r') as fd:
				content=fd.readline()
				if '0' not in content:
					result=False

			os.remove(token)
		
		except OSError:
			pass

		return result
		
	#def checkProcess

	def initRestoreProcesses(self):

		self.restoreLaunched=False
		self.restoreDone=False

	#def initRestoreProcesses

	def getRestoreCommand(self):

		self.restoreCommand=self.unlockerCore.getRestoreCommand()

	#def getStabilizeCommand

	def changeMetaProtectionStatus(self,change):

		if change:
			self.writeLog("Try to enable metapackage protection")
		else:
			self.writeLog("Try to disable metapackage protection")

		result=self.unlockerCore.changeMetaProtectionStatus(change)
		self.writeLog(f"Change metapackage protection result: {result}")
		return result[0]

	#def changeMetaProtectionStatus

	def writeProcessLog(self,code):

		msg=""
		if code==1:
			msg="Removing Lliurex-Up lock file"
		elif code==2:
			msg="Removing Dpkg lock file"
		elif code==3:
			msg="Removing Apt lock file"
		elif code==4:
			msg="Fixing the system"
		elif code==9:
			msg="Restoring the services"
		elif code==-6:
			msg="Error fixing the sytem"
		elif code==-7:
			msg="Error removing Apt lock file"
		elif code==-8:
			msg="Error removing Dpkg lock file"
		elif code==-9:
			msg="Error removing Lliurex-Up lock file"

		if msg:
			if msg==9:
				self.writeLog(f"Restoring process: {msg}")
			else:
				self.writeLog(f"Unlocked process: {msg}")

	#def writeProcessLog

	def writeLogTerminal(self):

		syslog.openlog("DpkgUnlocker")
		syslog.syslog("Unlocked process: Fixing the system details")

		if os.path.exists(self.KonsoleLog):
			with open(self.KonsoleLog,'r') as fd:
				content=fd.readlines()

		if len(content)>0:
			for line in content:
				self.writeLog(line)
		else:
			self.writeLog("KonsoleLog is empty")

		os.remove(self.KonsoleLog)
		
	#def writeLogTerminal

	def writeLog(self,msg):
	
		syslog.openlog("DpkgUnlocker")
		syslog.syslog(msg)	

	#def writeLog

	def cleanLockToken(self):

		self.unlockerCore.cleanLockToken()

	#def cleanLockToken
	
	def clearCache(self):

		clear=False
		versionFile="/root/.dpkg-unlocker-gui.conf"
		cachePath1="/root/.cache/dpkg-unlocker-gui"
		installedVersion=self.getPackageVersion()

		if not os.path.exists(versionFile):
			with open(versionFile,'w') as fd:
				fd.write(installedVersion)
			clear=True

		else:
			with open(versionFile,'r') as fd:
				fileVersion=fd.readline()
				fd.close()

			if fileVersion!=installedVersion:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)
				clear=True
		
		if clear:
			if os.path.exists(cachePath1):
				shutil.rmtree(cachePath1)

	#def clearCache

	def getPackageVersion(self):

		packageVersionFile="/var/lib/dpkgunlocker-gui/version"
		pkgVersion=""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline()
				fd.close()

		return pkgVersion

	#def getPackageVersion

	def showProtectionOption(self):

		userGroups=self._getUserGroups()
		
		if 'admin' not in userGroups:
			if 'teachers' in userGroups:
				return False

		return True

	#def showProtectionOption

	def _getUserGroups(self):

		userGroups=[]

		try:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			gid = pwd.getpwnam(user).pw_gid
			groups_gids = os.getgrouplist(user, gid)
			userGroups = [ grp.getgrgid(x).gr_name for x in groups_gids ]
		except:
			user=os.environ["USER"]
			gid = pwd.getpwnam(user).pw_gid
			groups_gids = os.getgrouplist(user, gid)
			userGroups = [ grp.getgrgid(x).gr_name for x in groups_gids ]

		return userGroups

	#def _getUserGroups

#class UnlockerManager
