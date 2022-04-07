#!/usr/bin/python3

import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import os
import sys
import syslog
import json
import codecs
import tempfile


class UnlockerManager:

	def __init__(self):

		self.unlockerCore=DpkgUnlockerManager.DpkgUnlockerManager()
		self.unlockerCore.createLockToken()		
		self.debug=True
		self.servicesData=[]
		self.sessionLang=""
		self.isThereALock=False
		self.KonsoleLog="/tmp/DpkgUnlocker_KonsoleLog.txt"
		self.getSessionLang()
		self.cleanEnvironment()
		self.metaProtectionEnabled=True

	#def __init__

	def loadInfo(self):

		info=self.unlockerCore.checkingLocks()
		self.manageServiceInfo(info)
		self.getMetaProtectionStatus()

	#def loadInfo

	def getMetaProtectionStatus(self):

		self.metaProtectionEnabled=self.unlockerCore.checkMetaProtection()

	#def getMetaProtectionStatus

	def manageServiceInfo(self,info):

		count=0
		okStatus=[0,1,3,4]
		runningStatus=[1,3,4]
		liveProcess=0
		self.isThereALock=False
		self.servicesData=[]

		for item in info:
			tmp={}
			tmp["serviceId"]=item
			tmp["statusCode"]=info[item]
			
			if info[item] in okStatus:
				count+=1 
			if info[item] in runningStatus:
				liveProcess+=1 

			self.servicesData.append(tmp)

		if count==len(info):
			self.isThereAlock=False
		else:
			if count==0:
				self.isThereAreLock=True
			else:
				if liveProcess==0:
					self.isThereALock=True 
				else:
					self.isThereALock=False

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
			self.tokenLlxupProcess=tempfile.mkstemp('_LlxUp')
			remove_tmp=' rm -f ' + self.tokenLlxupProcess[1] + ';'+'\n'
			
		elif action=="Dpkg":
			self.tokenDpkgProcess=tempfile.mkstemp('_Dpkg')
			remove_tmp=' rm -f ' + self.tokenDpkgProcess[1] + ';'+'\n'

		elif action=="Apt":
			self.tokenAptProcess=tempfile.mkstemp('_Apt')	
			remove_tmp=' rm -f ' + self.tokenAptProcess[1] + ';'+'\n'
			
		elif action=="Fixing":
			self.tokenFixingProcess=tempfile.mkstemp('_Fixing')	
			remove_tmp=' rm -f ' + self.tokenFixingProcess[1] + ';'+'\n'

		cmd=command+remove_tmp
		
		return cmd

	#def create_process_token	

	def createResultToken(self,command,action):

		if action=="Lliurex-Up":
			self.tokenLlxupResult=tempfile.mkstemp('_LlxUp')
			result_tmp=' echo $? >' + self.tokenLlxupResult[1]+ ')'
			
		elif action=="Dpkg":
			self.tokenDpkgResult=tempfile.mkstemp('_Dpkg')
			result_tmp=' echo $? > ' + self.tokenDpkgResult[1] + ')'

		elif action=="Apt":
			self.tokenAptResult=tempfile.mkstemp('_Apt')	
			result_tmp=' echo $? > ' + self.tokenAptResult[1] + ')'
			
		elif action=="Fixing":
			self.tokenFixingResult=tempfile.mkstemp('_Fixing')	
			result_tmp=' echo $? > ' + self.tokenFixingResult[1] + ')'

		cmd='(('+command+');'+result_tmp+'2>&1 | tee -a %s;'%self.KonsoleLog
		
		return cmd	

	#def createResultToken	

	def getUnlockerCommand(self):

		self.unlockInfo=self.unlockerCore.getUnlockerCommand()

	#def getUnlockerCommand

	def execCommand(self,action,type_cmd):

		command=""
		if type_cmd=="remove":
			command=self.unlockInfo["unlockCmd"][action]
		else:
			command=self.unlockInfo["commonCmd"]

		length=len(command)
		
		if length>0:
			command=self.createResultToken(command,action)
			command=self.createProcessToken(command,action)
		else:
			if action=="Lliurex-Up":
				self.removeLlxupLockDone=True
			elif action=="Dpkg":
				self.removeDpkgLockDone=True
			elif action=="Apt":
				self.remove_ap_lock_done=True
			elif action=="Fixing":
				self.fixingSystemDone=True
		return command
	
	#def exec_command			
	
	def checkProcess(self,action):

		result=True

		if action=="Lliurex-Up":
			token=self.tokenLlxupResult[1]
		elif action=="Dpkg":
			token=self.tokenDpkgResult[1]
		elif action=="Apt":
			token=self.tokenAptResult[1]
		elif action=="Fixing":
			token=self.tokenFixingResult[1]
					
		if os.path.exists(token):
			file=open(token)
			content=file.readline()
			if '0' not in content:
				result=False
			file.close()
			os.remove(token)

		return result
		
	#def check_process

	def changeMetaProtectionStatus(self,change):

		if change:
			self.writeLog("Try to enable metapackage protection")
		else:
			self.writeLog("Try to disable metapackage protection")

		result=self.unlockerCore.changeMetaProtectionStatus(change)
		self.writeLog("Change metapackage protection result: %s"%(str(result)))
		return result[0]

	#def changeMetaProtectionStatus

	def writeProcessLog(self,code):

		if code==1:
			msg="Removing Lliurex-Up lock file"
		elif code==2:
			msg="Removing Dpkg lock file"
		elif code==3:
			msg="Removing Apt lock file"
		elif code==4:
			msg="Fixing the system"
		elif code==-6:
			msg="Error fixing the sytem"
		elif code==-7:
			msg="Error removing Apt lock file"
		elif code==-8:
			msg="Error removing Dpkg lock file"
		elif code==-9:
			msg="Error removing Lliurex-Up lock file"

		if msg!="":
			self.writeLog("Unlocked process: %s"%msg)

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


#class UnlockerManager
