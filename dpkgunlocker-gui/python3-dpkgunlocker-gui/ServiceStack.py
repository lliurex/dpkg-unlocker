#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
from . import ServicesModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
	
	#def __init__
		

	def run(self,*args):
		
		time.sleep(1)
		Bridge.unlockerManager.loadInfo()

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
		
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.unlockerManager=self.core.unlockerManager
		self._servicesModel=ServicesModel.ServicesModel()
		self._showServiceStatusMesage=[False,"","Success"]
		self._isThereALock=False
		self._areLiveProcess=False
		self.runningUnlockCommand=False

	#def __init__

	def loadConfig(self):		

		isThereALock=Bridge.unlockerManager.isThereALock
		self.areLiveProcess=Bridge.unlockerManager.areLiveProcess

		if isThereALock and not self.areLiveProcess:
			self.isThereALock=True
			self._updateServiceStatusMessage(12)
		elif isThereALock and self.areLiveProcess:
			self._updateServiceStatusMessage(11)
		else:
			self._updateServiceStatusMessage(0)
		
		self._updateServicesModel()

	#def loadConfig

	def initWatcher(self):

		self.statusServicesRunningTimer=QTimer(None)
		self.statusServicesRunningTimer.timeout.connect(self._updateServicesStatus)
		self.statusServicesRunningTimer.start(5000)

	#def initWatcher

	def _updateServicesStatus(self):

		if not self.core.mainStack.isWorked:
			self.core.mainStack.isWorked=True
			self._gatherInfoThread()
	
	#def _updateServicesStatus

	def _gatherInfoThread(self):
		
		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._updateServicesInfo)
	
	#def _gatherInfoThread

	def _updateServicesInfo(self):

		if not self.runningUnlockCommand:
			isThereALock=Bridge.unlockerManager.isThereALock
			self.areLiveProcess=Bridge.unlockerManager.areLiveProcess
			if isThereALock and not self.areLiveProcess:
				self.isThereALock=True
				self._updateServiceStatusMessage(12)
			elif isThereALock and self.areLiveProcess:
				self.isThereALock=False
				self._updateServiceStatusMessage(11)
			else:
				self.isThereALock=False
				self._updateServiceStatusMessage(0)
			
			self.core.protectionStack.updateProtectionInfo()

			updatedInfo=Bridge.unlockerManager.servicesData
			for i in range(len(updatedInfo)):
				index=self._servicesModel.index(i)
				self._servicesModel.setData(index,'statusCode',updatedInfo[i]["statusCode"])

			if not self.core.mainStack.endProcess:
				if not self.core.restoreStack.runningRestoreCommand:
					self.core.mainStack.endProcess=True
					self.core.mainStack.endCurrentCommand=True
					Bridge.unlockerManager.writeLogTerminal()
					Bridge.unlockerManager.writeLog("Final Services Status: %s"%(str(updatedInfo)))

		self.core.mainStack.isWorked=False

	#def _updateServicesInfo

	def _updateServiceStatusMessage(self,code):

		infoCode=[11]
		successCode=[0,5]
		errorCode=[12]

		if code in infoCode:
			self.showServiceStatusMesage=[True,code,"Warning"]
		elif code in successCode:
			self.showServiceStatusMesage=[True,code,"Success"]
		elif code in errorCode:
			self.showServiceStatusMesage=[True,code,"Error"]

	#def _updateServiceStatusMessage

	def _getIsThereALock(self):

		return self._isThereALock

	#def _getIsThereALock

	def _setIsThereALock(self,isThereALock):

		if self._isThereALock!=isThereALock:
			self._isThereALock=isThereALock
			self.on_isThereALock.emit()

	#def _setIsThereALock

	def _getAreLiveProcess(self):

		return self._areLiveProcess

	#def _getAreLiveProcess

	def _setAreLiveProcess(self,areLiveProcess):

		if self._areLiveProcess!=areLiveProcess:
			self._areLiveProcess=areLiveProcess
			self.on_areLiveProcess.emit()

	#def _setAreLiveProcess

	def _getShowServiceStatusMesage(self):

		return self._showServiceStatusMesage

	#def _getShowServiceStatusMesage

	def _setShowServiceStatusMesage(self,showServiceStatusMesage):

		if self._showServiceStatusMesage!=showServiceStatusMesage:
			self._showServiceStatusMesage=showServiceStatusMesage
			self.on_showServiceStatusMesage.emit()

	#def _setShowServiceStatusMesage

	def _getServicesModel(self):
		
		return self._servicesModel

	#def _getServicesModel

	def _updateServicesModel(self):

		ret=self._servicesModel.clear()
		servicesEntries=Bridge.unlockerManager.servicesData
		for item in servicesEntries:
			self._servicesModel.appendRow(item["serviceId"],item["statusCode"])
		self.core.mainStack.isWorked=False

	#def _updateServicesModel

	@Slot()
	def launchUnlockProcess(self):

		self.core.mainStack.showDialog=False
		self.core.mainStack.processLaunched="Unlock"
		self.runningUnlockCommand=True
		self.statusServicesRunningTimer.stop()
		self.core.mainStack.endProcess=False
		self.core.mainStack.isWorked=True
		self.showServiceStatusMesage=[False,"","Success"]
		Bridge.unlockerManager.initUnlockerProcesses()
		Bridge.unlockerManager.getUnlockerCommand()
		Bridge.unlockerManager.writeLog("Services Status Error: %s"%(str(Bridge.unlockerManager.servicesData)))
		self.unlockerProcessRunningTimer=QTimer(None)
		self.unlockerProcessRunningTimer.timeout.connect(self._updateUnlockerProcessStatus)
		self.unlockerProcessRunningTimer.start(100)

	#def launchUnlockProcess

	def _updateUnlockerProcessStatus(self):

		error=False

		if not Bridge.unlockerManager.removeLlxupLockLaunched:
			if "Lliurex-Up" in Bridge.unlockerManager.unlockInfo["unlockCmd"]:
				self.core.mainStack.feedBackCode=Bridge.LLXUP_UNLOCK_COMMAND_RUNNING
				Bridge.unlockerManager.removeLlxupLockLaunched=True
				self.core.mainStack.currentCommand=Bridge.unlockerManager.execCommand("Lliurex-Up","remove")
				self.core.mainStack.endCurrentCommand=True
				self.llxupLockCheck=True
				Bridge.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)

			else:
				Bridge.unlockerManager.removeLlxupLockDone=True
				self.llxupLockCheck=False
				self.llxupLockResult=True

		if Bridge.unlockerManager.removeLlxupLockDone:
			if self.llxupLockCheck:
				self.llxupLockResult=Bridge.unlockerManager.checkProcess("Lliurex-Up")

			if self.llxupLockResult:
				if not Bridge.unlockerManager.removeDpkgLockLaunched:
					if "Dpkg" in Bridge.unlockerManager.unlockInfo["unlockCmd"]:
						self.core.mainStack.feedBackCode=Bridge.DPKG_UNLOCK_COMMAND_RUNNING
						Bridge.unlockerManager.removeDpkgLockLaunched=True
						self.core.mainStack.currentCommand=Bridge.unlockerManager.execCommand("Dpkg","remove")
						self.core.mainStack.endCurrentCommand=True
						self.dpkgLockCheck=True
						Bridge.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
					else:
						Bridge.unlockerManager.removeDpkgLockDone=True
						self.dpkgLockCheck=False
						self.dpkgResult=True

				if Bridge.unlockerManager.removeDpkgLockDone:
					if self.dpkgLockCheck:
						self.dpkgResult=Bridge.unlockerManager.checkProcess("Dpkg")

					if self.dpkgResult:
						if not Bridge.unlockerManager.removeAptLockLaunched:
							if "Apt" in Bridge.unlockerManager.unlockInfo["unlockCmd"]:
								self.core.mainStack.feedBackCode=Bridge.DPKG_UNLOCK_COMMAND_RUNNING
								Bridge.unlockerManager.removeAptLockLaunched=True
								self.core.mainStack.currentCommand=Bridge.unlockerManager.execCommand("Apt","remove")
								self.core.mainStack.endCurrentCommand=True
								self.aptLockCheck=True
								Bridge.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
							else:
								Bridge.unlockerManager.removeAptLockDone=True
								self.aptLockCheck=False
								self.aptResult=True	

						if Bridge.unlockerManager.removeAptLockDone:
							if self.aptLockCheck:
								self.aptResult=Bridge.unlockerManager.checkProcess("Apt")

							if self.aptResult:
								if not Bridge.unlockerManager.fixingSystemLaunched:
									if Bridge.unlockerManager.unlockInfo["commonCmd"]!="":
										self.core.mainStack.feedBackCode=Bridge.FIXING_UNLOCK_COMMAND_RUNNING
										Bridge.unlockerManager.fixingSystemLaunched=True
										self.core.mainStack.currentCommand=Bridge.unlockerManager.execCommand("Fixing","fixing")
										self.core.mainStack.endCurrentCommand=True
										self.fixingLockCheck=True
										Bridge.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
									else:
										Bridge.unlockerManager.fixingSystemDone=True
										self.fixingLockCheck=False
										self.fixingResult=True

								if Bridge.unlockerManager.fixingSystemDone:
									if self.fixingLockCheck:
										self.fixingResult=Bridge.unlockerManager.checkProcess("Fixing")
									if self.fixingResult:
										self.unlockerProcessRunningTimer.stop()
										self.runningUnlockCommand=False
										self._gatherInfoThread()

									else:
										error=True
										code=Bridge.FIXING_UNLOCK_COMMAND_ERROR
							else:
								error=True
								code=Bridge.APT_UNLOCK_COMMAND_ERROR			
					else:
						error=True	
						code=Bridge.DPKG_UNLOCK_COMMAND_ERROR								
			else:
				error=True
				code=Bridge.LLXUP_UNLOCK_COMMAND_ERROR

			if error:
				self.runningUnlockCommand=False
				self.showServiceStatusMesage=[True,code,"Error"]
				self.unlockerProcessRunningTimer.stop()
				Bridge.unlockerManager.writeProcessLog(code)
				self._gatherInfoThread()

		if Bridge.unlockerManager.removeLlxupLockLaunched:
			if not Bridge.unlockerManager.removeLlxupLockDone:
				if not os.path.exists(Bridge.unlockerManager.tokenLlxupProcess[1]):
					Bridge.unlockerManager.removeLlxupLockDone=True

		if Bridge.unlockerManager.removeDpkgLockLaunched:
			if not Bridge.unlockerManager.removeDpkgLockDone:
				if not os.path.exists(Bridge.unlockerManager.tokenDpkgProcess[1]):
					Bridge.unlockerManager.removeDpkgLockDone=True

		if Bridge.unlockerManager.removeAptLockLaunched:
			if not Bridge.unlockerManager.removeAptLockDone:
				if not os.path.exists(Bridge.unlockerManager.tokenAptProcess[1]):
					Bridge.unlockerManager.removeAptLockDone=True

		if Bridge.unlockerManager.fixingSystemLaunched:
			if not Bridge.unlockerManager.fixingSystemDone:
				if not os.path.exists(Bridge.unlockerManager.tokenFixingProcess[1]):
					Bridge.unlockerManager.fixingSystemDone=True

	#def _updateUnlockerProcessStatus

	on_isThereALock=Signal()
	isThereALock=Property(bool,_getIsThereALock,_setIsThereALock,notify=on_isThereALock)

	on_areLiveProcess=Signal()
	areLiveProcess=Property(bool,_getAreLiveProcess,_setAreLiveProcess,notify=on_areLiveProcess)

	on_showServiceStatusMesage=Signal()
	showServiceStatusMesage=Property('QVariantList',_getShowServiceStatusMesage,_setShowServiceStatusMesage,notify=on_showServiceStatusMesage)

	servicesModel=Property(QObject,_getServicesModel,constant=True)


#class Bridge
from . import Core

