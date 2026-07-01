#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
from . import ServicesModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	infoGathered=Signal()

	def __init__(self,manager):

		super().__init__()
		self.manager=manager
	
	#def __init__
		

	def run(self,*args):
		
		time.sleep(1)
		self.manager.loadInfo()
		self.infoGathered.emit()

	#def run

#class GatherInfo

class Bridge(QObject):

	LLXUP_UNLOCK_COMMAND_RUNNING=1
	DPKG_UNLOCK_COMMAND_RUNNING=2
	APT_UNLOCK_COMMAND_RUNNING=3
	FIXING_UNLOCK_COMMAND_RUNNING=4
	FIXING_UNLOCK_COMMAND_ERROR=-6
	APT_UNLOCK_COMMAND_ERROR=-7
	DPKG_UNLOCK_COMMAND_ERROR=-8
	LLXUP_UNLOCK_COMMAND_ERROR=-9

	WARNING_CODE=11
	SUCCESS_CODE=0
	ERROR_CODE=12

	isThereALockChanged=Signal()
	areLiveProcessChanged=Signal()
	showServiceStatusMesageChanged=Signal()

	PROCESSTOKENS=[
		("removeLlxupLock", "tokenLlxupProcess"),
		("removeDpkgLock", "tokenDpkgProcess"),
		("removeAptLock", "tokenAptProcess"),
		("fixingSystem","tokenFixingProcess")
	]	

		
	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.unlockerManager=self.core.unlockerManager
		self._servicesModel=ServicesModel.ServicesModel()
		self._showServiceStatusMesage={"show":False,"msgCode":"","type":""}
		self._isThereALock=False
		self._areLiveProcess=False
		self.runningUnlockCommand=False

	#def __init__

	@Property(bool,notify=isThereALockChanged)
	def isThereALock(self):

		return self._isThereALock

	#def isThereALock

	@isThereALock.setter
	def isThereALock(self,isThereALock):

		if self._isThereALock!=isThereALock:
			self._isThereALock=isThereALock
			self.isThereALockChanged.emit()

	#def isThereALock

	@Property(bool,notify=areLiveProcessChanged)
	def areLiveProcess(self):

		return self._areLiveProcess

	#def areLiveProcess

	@areLiveProcess.setter
	def areLiveProcess(self,areLiveProcess):

		if self._areLiveProcess!=areLiveProcess:
			self._areLiveProcess=areLiveProcess
			self.areLiveProcessChanged.emit()

	#def areLiveProcess
	
	@Property(dict,notify=showServiceStatusMesageChanged)
	def showServiceStatusMesage(self):

		return self._showServiceStatusMesage

	#def showServiceStatusMesage

	@showServiceStatusMesage.setter
	def showServiceStatusMesage(self,showServiceStatusMesage):

		if self._showServiceStatusMesage!=showServiceStatusMesage:
			self._showServiceStatusMesage=showServiceStatusMesage
			self.showServiceStatusMesageChanged.emit()

	#def _setShowServiceStatusMesage

	@Property(QObject,constant=True)
	def servicesModel(self):
		
		return self._servicesModel

	#def servicesModel

	def loadConfig(self):		

		self._checkLockInfo()
		self._updateServicesModel()

	#def loadConfig

	def initWatcher(self):

		self.statusServicesRunningTimer=QTimer(self)
		self.statusServicesRunningTimer.timeout.connect(self._updateServicesStatus)
		self.statusServicesRunningTimer.start(5000)

	#def initWatcher

	def _checkLockInfo(self):

		self.isThereALock=self.unlockerManager.isThereALock
		self.areLiveProcess=self.unlockerManager.areLiveProcess

		if self.isThereALock:
			if not self.areLiveProcess:
				code=Bridge.ERROR_CODE
				type=self.unlockerManager.KIRIGAMI_MSG_ERROR
			else:
				code=Bridge.WARNING_CODE
				type=self.unlockerManager.KIRIGAMI_MSG_WARNING
		else:
			code=Bridge.SUCCESS_CODE
			type=self.unlockerManager.KIRIGAMI_MSG_OK

		self.showServiceStatusMesage={"show":True,"msgCode":code,"type":type}


	#def _checkLockInfo

	def _updateServicesStatus(self):

		if not self.core.mainStack.isWorked:
			self.core.mainStack.isWorked=True
			self._gatherInfoThread()
	
	#def _updateServicesStatus

	def _gatherInfoThread(self):
		
		self.gatherInfoT=GatherInfo(self.unlockerManager)
		self.gatherInfoT.start()
		self.gatherInfoT.infoGathered.connect(self._updateServicesInfo)
		self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)
	
	#def _gatherInfoThread

	def _updateServicesInfo(self):

		if not self.runningUnlockCommand:
			self._checkLockInfo()

			self.core.protectionStack.updateProtectionInfo()

			updatedInfo=self.unlockerManager.servicesData
			for i,infoItem in enumerate(updatedInfo):
				index=self._servicesModel.index(i)
				self._servicesModel.setData(index,'statusCode',infoItem["statusCode"])

			if not self.core.mainStack.endProcess:
				if not self.core.restoreStack.runningRestoreCommand:
					self.core.mainStack.endProcess=True
					self.core.mainStack.endCurrentCommand=True
					self.unlockerManager.writeLogTerminal()
					self.unlockerManager.writeLog(f"Final Services Status: {updatedInfo}")

		self.core.mainStack.isWorked=False

	#def _updateServicesInfo

	def _updateServicesModel(self):

		ret=self._servicesModel.clear()
		servicesEntries=self.unlockerManager.servicesData
		for item in servicesEntries:
			self._servicesModel.appendRow(item["serviceId"],item["statusCode"])
		self.core.mainStack.isWorked=False

	#def _updateServicesModel

	@Slot()
	def launchUnlockProcess(self):

		self.core.mainStack.showDialog=False
		self.core.mainStack.processLaunched="Unlock"
		self.core.mainStack.enableKonsole=True
		self.runningUnlockCommand=True
		self.statusServicesRunningTimer.stop()
		self.core.mainStack.endProcess=False
		self.core.mainStack.isWorked=True
		self.showServiceStatusMesage={"show":False,"msgCode":"","type":""}
		self.unlockerManager.initUnlockerProcesses()
		self.unlockerManager.getUnlockerCommand()
		self.unlockerManager.writeLog(f"Services Status Error: {self.unlockerManager.servicesData}")
		self.unlockerProcessRunningTimer=QTimer(self)
		self.unlockerProcessRunningTimer.timeout.connect(self._updateUnlockerProcessStatus)
		self.unlockerProcessRunningTimer.start(100)

	#def launchUnlockProcess

	def _updateUnlockerProcessStatus(self):

		if not self.unlockerManager.removeLlxupLockLaunched:
			if "Lliurex-Up" in self.unlockerManager.unlockInfo["unlockCmd"]:
				self.core.mainStack.feedBackCode=Bridge.LLXUP_UNLOCK_COMMAND_RUNNING
				self.unlockerManager.removeLlxupLockLaunched=True
				self.core.mainStack.currentCommand=self.unlockerManager.execCommand("Lliurex-Up","remove")
				self.core.mainStack.endCurrentCommand=True
				self.llxupLockCheck=True
				self.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)

			else:
				self.unlockerManager.removeLlxupLockDone=True
				self.llxupLockCheck=False
				self.llxupLockResult=True

		if not self.unlockerManager.removeLlxupLockDone:
			return self._checkProcessToken()

		if self.llxupLockCheck:
			self.llxupLockResult=self.unlockerManager.checkProcess("Lliurex-Up")
			self.llxupLockCheck=False

		if not self.llxupLockResult:
			return self._endProcessWithErrors(Bridge.LLXUP_UNLOCK_COMMAND_ERROR)

		if not self.unlockerManager.removeDpkgLockLaunched:
			if "Dpkg" in self.unlockerManager.unlockInfo["unlockCmd"]:
				self.core.mainStack.feedBackCode=Bridge.DPKG_UNLOCK_COMMAND_RUNNING
				self.unlockerManager.removeDpkgLockLaunched=True
				self.core.mainStack.currentCommand=self.unlockerManager.execCommand("Dpkg","remove")
				self.core.mainStack.endCurrentCommand=True
				self.dpkgLockCheck=True
				self.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
			else:
				self.unlockerManager.removeDpkgLockDone=True
				self.dpkgLockCheck=False
				self.dpkgResult=True

		if not self.unlockerManager.removeDpkgLockDone:
			return self._checkProcessToken()

		if self.dpkgLockCheck:
			self.dpkgResult=self.unlockerManager.checkProcess("Dpkg")
			self.dpkgLockCheck=False

		if not self.dpkgResult:
			return self._endProcessWithErrors(Bridge.DPKG_UNLOCK_COMMAND_ERROR)

		if not self.unlockerManager.removeAptLockLaunched:
			if "Apt" in self.unlockerManager.unlockInfo["unlockCmd"]:
				self.core.mainStack.feedBackCode=Bridge.DPKG_UNLOCK_COMMAND_RUNNING
				self.unlockerManager.removeAptLockLaunched=True
				self.core.mainStack.currentCommand=self.unlockerManager.execCommand("Apt","remove")
				self.core.mainStack.endCurrentCommand=True
				self.aptLockCheck=True
				self.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
			else:
				self.unlockerManager.removeAptLockDone=True
				self.aptLockCheck=False
				self.aptResult=True	

		if not self.unlockerManager.removeAptLockDone:
			return self._checkProcessToken()

		if self.aptLockCheck:
			self.aptResult=self.unlockerManager.checkProcess("Apt")
			self.aptLockCheck=False

		if not self.aptResult:
			return self._endProcessWithErrors(Bridge.APT_UNLOCK_COMMAND_ERROR)

		if not self.unlockerManager.fixingSystemLaunched:
			if self.unlockerManager.unlockInfo["commonCmd"]!="":
				self.core.mainStack.feedBackCode=Bridge.FIXING_UNLOCK_COMMAND_RUNNING
				self.unlockerManager.fixingSystemLaunched=True
				self.core.mainStack.currentCommand=self.unlockerManager.execCommand("Fixing","fixing")
				self.core.mainStack.endCurrentCommand=True
				self.fixingLockCheck=True
				self.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
			else:
				self.unlockerManager.fixingSystemDone=True
				self.fixingLockCheck=False
				self.fixingResult=True

		if not self.unlockerManager.fixingSystemDone:
			return self._checkProcessToken()

		if self.fixingLockCheck:
			self.fixingResult=self.unlockerManager.checkProcess("Fixing")
			self.fixingLockCheck=False

		if not self.fixingResult:
			self._endProcessWithErrors(Bridge.FIXING_UNLOCK_COMMAND_ERROR)
		
		self.unlockerProcessRunningTimer.stop()
		self.runningUnlockCommand=False
		self._gatherInfoThread()

	#def _updateUnlockerProcessStatus

	def _endProcessWithErrors(self,code):

		self.runningUnlockCommand=False
		self.showServiceStatusMesage={"show":True,"msgCode":code,"type":self.unlockerManager.KIRIGAMI_MSG_ERROR}
		self.unlockerProcessRunningTimer.stop()
		self.unlockerManager.writeProcessLog(code)
		self._gatherInfoThread()

	#def _endProcessWithErrors

	def _checkProcessToken(self):

		for prefix, token in self.PROCESSTOKENS:
			if getattr(self.unlockerManager, f"{prefix}Launched") and not getattr(self.unlockerManager, f"{prefix}Done"):
				tmpToken=getattr(self.unlockerManager,token)
				if not os.path.exists(tmpToken):
					setattr(self.unlockerManager, f"{prefix}Done", True)

	#def _checkProcessToken

#class Bridge
from . import Core

