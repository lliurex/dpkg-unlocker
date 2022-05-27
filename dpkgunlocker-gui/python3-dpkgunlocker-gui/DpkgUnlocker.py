#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
from . import UnlockerManager
from . import ServicesModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
	
	#def __init__
		

	def run(self,*args):
		
		time.sleep(1)
		DpkgUnlocker.unlockerManager.loadInfo()

	#def run

#class GatherInfo

class DpkgUnlocker(QObject):

	unlockerManager=UnlockerManager.UnlockerManager()
	LLXUP_UNLOCK_COMMAND_RUNNING=1
	DPKG_UNLOCK_COMMAND_RUNNING=2
	APT_UNLOCK_COMMAND_RUNNING=3
	FIXING_UNLOCK_COMMAND_RUNNING=4
	META_PROTECTION_ENABLED=6
	META_PROTECTION_DISABLED=7
	META_PROTECTION_CHANGE_SUCCESS=8
	FIXING_UNLOCK_COMMAND_ERROR=-6
	APT_UNLOCK_COMMAND_ERROR=-7
	DPKG_UNLOCK_COMMAND_ERROR=-8
	LLXUP_UNLOCK_COMMAND_ERROR=-9
	META_PROTECTION_ENABLED_ERROR=-10
	META_PROTECTION_DISABLED_ERROR=-11
	
	def __init__(self):

		QObject.__init__(self)
		self.initBridge()

	#def __init__

	def initBridge(self):

		self._servicesModel=ServicesModel.ServicesModel()
		self._closeGui=False
		self._closePopUp=True
		self._showServiceStatusMesage=[False,"","Success"]
		self._currentStack=0
		self._currentOptionsStack=0
		self._isThereALock=False
		self._feedBackCode=0
		self._metaProtectionEnabled=True
		self._showProtectionStatusMessage=[False,"","Success"]
		self._isProtectionChange=False
		self._showDialog=False
		self._showPendingChangesDialog=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self.statusServicesRunningTimer=QTimer(None)
		self.statusServicesRunningTimer.timeout.connect(self._updateServicesStatus)
		self.statusServicesRunningTimer.start(5000)
		self.isWorked=True
		self.runningUnlockCommand=False
		self.moveToStack=""
		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._loadConfig)

	#def initBridge

	def _loadConfig(self):		

		self.metaProtectionEnabled=DpkgUnlocker.unlockerManager.metaProtectionEnabled
	
		self.isThereALock=DpkgUnlocker.unlockerManager.isThereALock
		if self._isThereALock:
			self._updateServiceStatusMessage(12)
		else:
			self._updateServiceStatusMessage(0)
		
		if self.metaProtectionEnabled:
			self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_ENABLED,"Success"]
		else:
			self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_DISABLED,"Warning"]

		self._copyCurrentProtectionStatus()
		self._updateServicesModel()
		DpkgUnlocker.unlockerManager.writeLog("Dpkg-Unlocker-Gui")
		DpkgUnlocker.unlockerManager.writeLog("Initial System Metapackage Protecion. Enabled: %s"%(str(self.metaProtectionEnabled)))
		DpkgUnlocker.unlockerManager.writeLog("Initial Services Status: %s"%(str(DpkgUnlocker.unlockerManager.servicesData)))
		self.currentStack=1

	#def _loadConfig

	def _updateServicesStatus(self):

		if not self.isWorked:
			self.isWorked=True
			self._gatherInfoThread()
	
	#def _updateServicesModel

	def _gatherInfoThread(self):
		
		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._updateServicesInfo)
	
	#def _gatherInfoThread

	def _updateServicesInfo(self):

		if not self.runningUnlockCommand:
			self.isThereALock=DpkgUnlocker.unlockerManager.isThereALock
			
			if self.isThereALock:
				self._updateServiceStatusMessage(12)
			else:
				self._updateServiceStatusMessage(0)
			
			if not self.isProtectionChange:
				self.metaProtectionEnabled=DpkgUnlocker.unlockerManager.metaProtectionEnabled
				if self.metaProtectionEnabled:
					self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_ENABLED,"Success"]
				else:
					self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_DISABLED,"Warning"]

				self._copyCurrentProtectionStatus()

			updatedInfo=DpkgUnlocker.unlockerManager.servicesData
			for i in range(len(updatedInfo)):
				index=self._servicesModel.index(i)
				self._servicesModel.setData(index,'statusCode',updatedInfo[i]["statusCode"])

			if not self.endProcess:
				self.endProcess=True
				self.endCurrentCommand=True
				DpkgUnlocker.unlockerManager.writeLogTerminal()
				DpkgUnlocker.unlockerManager.writeLog("Final Services Status: %s"%(str(updatedInfo)))

		self.isWorked=False

	#def _updateServicesInfo

	def _updateServiceStatusMessage(self,code):

		infoCode=[11]
		successCode=[0,5]
		errorCode=[12]

		if code in infoCode:
			self.showServiceStatusMesage=[True,code,"Info"]
		elif code in successCode:
			self.showServiceStatusMesage=[True,code,"Success"]
		elif code in errorCode:
			self.showServiceStatusMesage=[True,code,"Error"]

	#def _updateServiceStatusMessage

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getCurrentOptionsStack(self):

		return self._currentOptionsStack

	#def _getCurrentOptionsStack

	def _setCurrentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.on_currentOptionsStack.emit()

	#def _setCurrentOptionsStack

	def _getIsThereALock(self):

		return self._isThereALock

	#def _getIsThereALock

	def _setIsThereALock(self,isThereALock):

		if self._isThereALock!=isThereALock:
			self._isThereALock=isThereALock
			self.on_isThereALock.emit()

	#def _setIsThereALock

	def _getFeedBackCode(self):

		return self._feedBackCode

	#def _getFeedBackCode

	def _setFeedBackCode(self,feedBackCode):

		if self._feedBackCode!=feedBackCode:
			self._feedBackCode=feedBackCode
			self.on_feedBackCode.emit()

	#def _setFeedBackCode

	def _getShowServiceStatusMesage(self):

		return self._showServiceStatusMesage

	#def _getShowServiceStatusMesage

	def _setShowServiceStatusMesage(self,showServiceStatusMesage):

		if self._showServiceStatusMesage!=showServiceStatusMesage:
			self._showServiceStatusMesage=showServiceStatusMesage
			self.on_showServiceStatusMesage.emit()

	#def _setShowServiceStatusMesage

	def _getMetaProtectionEnabled(self):

		return self._metaProtectionEnabled

	#def _getFeedBackCode

	def _setMetaProtectionEnabled(self,metaProtectionEnabled):

		if self._metaProtectionEnabled!=metaProtectionEnabled:
			self._metaProtectionEnabled=metaProtectionEnabled
			self.on_metaProtectionEnabled.emit()

	#def _setMetaProtectionEnabled

	def _getShowProtectionStatusMessage(self):

		return self._showProtectionStatusMessage

	#def _getShowServiceStatusMesage

	def _setShowProtectionStatusMessage(self,showProtectionStatusMessage):

		if self._showProtectionStatusMessage!=showProtectionStatusMessage:
			self._showProtectionStatusMessage=showProtectionStatusMessage
			self.on_showProtectionStatusMessage.emit()

	#def _setShowProtectionStatusMessage

	def _getIsProtectionChange(self):

		return self._isProtectionChange

	#def _getIsProtectionChange

	def _setIsProtectionChange(self,isProtectionChange):

		if self._isProtectionChange!=isProtectionChange:
			self._isProtectionChange=isProtectionChange
			self.on_isProtectionChange.emit()
	
	#def _setIsProtectionChange

	def _getShowDialog(self):

		return self._showDialog

	#def _getShowDialog

	def _setShowDialog(self,showDialog):

		if self._showDialog!=showDialog:
			self._showDialog=showDialog
			self.on_showDialog.emit()
	
	#def _setShowDialog

	def _getShowPendingChangesDialog(self):

		return self._showPendingChangesDialog

	#def _getShowPendingChangesDialog

	def _setShowPendingChangesDialog(self,showPendingChangesDialog):

		if self._showPendingChangesDialog!=showPendingChangesDialog:
			self._showPendingChangesDialog=showPendingChangesDialog
			self.on_showPendingChangesDialog.emit()
	
	#def _setShowPendingChangesDialog

	def _getEndProcess(self):

		return self._endProcess

	#def _getEndProcess	

	def _setEndProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.on_endProcess.emit()

	#def _setEndProcess

	def _getEndCurrentCommand(self):

		return self._endCurrentCommand

	#def _getEndCurrentCommand

	def _setEndCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.on_endCurrentCommand.emit()

	#def _setEndCurrentCommand

	def _getCurrentCommand(self):

		return self._currentCommand

	#def _getCurrentCommand

	def _setCurrentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.on_currentCommand.emit()

	#def _setCurrentCommand

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui	

	def _getServicesModel(self):
		
		return self._servicesModel

	#def _getServicesModel

	def _updateServicesModel(self):

		ret=self._servicesModel.clear()
		servicesEntries=DpkgUnlocker.unlockerManager.servicesData
		for item in servicesEntries:
			self._servicesModel.appendRow(item["serviceId"],item["statusCode"])
		self.isWorked=False

	#def _updateServicesModel

	def _copyCurrentProtectionStatus(self):

		self.currentMetaProtectionStatus=copy.deepcopy(self.metaProtectionEnabled)
		self.currentMessage=copy.deepcopy(self.showProtectionStatusMessage)

	#def _copyCurrentProtectionStatus

	@Slot()
	def openDialog(self):
		
		self.showDialog=True

	#def openDialog

	@Slot()
	def launchUnlockProcess(self):

		self.showDialog=False
		self.runningUnlockCommand=True
		self.statusServicesRunningTimer.stop()
		self.endProcess=False
		self.isWorked=True
		self.isThereALock=False
		self.showServiceStatusMesage=[False,"","Success"]
		DpkgUnlocker.unlockerManager.initUnlockerProcesses()
		DpkgUnlocker.unlockerManager.getUnlockerCommand()
		DpkgUnlocker.unlockerManager.writeLog("Services Status Error: %s"%(str(DpkgUnlocker.unlockerManager.servicesData)))
		self.unlockerProcessRunningTimer=QTimer(None)
		self.unlockerProcessRunningTimer.timeout.connect(self._updateUnlockerProcessStatus)
		self.unlockerProcessRunningTimer.start(100)

	#def launchUnlockProcess

	def _updateUnlockerProcessStatus(self):

		error=False

		if not DpkgUnlocker.unlockerManager.removeLlxupLockLaunched:
			if "Lliurex-Up" in DpkgUnlocker.unlockerManager.unlockInfo["unlockCmd"]:
				self.feedBackCode=DpkgUnlocker.LLXUP_UNLOCK_COMMAND_RUNNING
				DpkgUnlocker.unlockerManager.removeLlxupLockLaunched=True
				self.currentCommand=DpkgUnlocker.unlockerManager.execCommand("Lliurex-Up","remove")
				self.endCurrentCommand=True
				self.llxupLockCheck=True
				DpkgUnlocker.unlockerManager.writeProcessLog(self.feedBackCode)

			else:
				DpkgUnlocker.unlockerManager.removeLlxupLockDone=True
				self.llxupLockCheck=False
				self.llxupLockResult=True

		if DpkgUnlocker.unlockerManager.removeLlxupLockDone:
			if self.llxupLockCheck:
				self.llxupLockResult=DpkgUnlocker.unlockerManager.checkProcess("Lliurex-Up")

			if self.llxupLockResult:
				if not DpkgUnlocker.unlockerManager.removeDpkgLockLaunched:
					if "Dpkg" in DpkgUnlocker.unlockerManager.unlockInfo["unlockCmd"]:
						self.feedBackCode=DpkgUnlocker.DPKG_UNLOCK_COMMAND_RUNNING
						DpkgUnlocker.unlockerManager.removeDpkgLockLaunched=True
						self.currentCommand=DpkgUnlocker.unlockerManager.execCommand("Dpkg","remove")
						self.endCurrentCommand=True
						self.dpkgLockCheck=True
						DpkgUnlocker.unlockerManager.writeProcessLog(self.feedBackCode)
					else:
						DpkgUnlocker.unlockerManager.removeDpkgLockDone=True
						self.dpkgLockCheck=False
						self.dpkgResult=True

				if DpkgUnlocker.unlockerManager.removeDpkgLockDone:
					if self.dpkgLockCheck:
						self.dpkgResult=DpkgUnlocker.unlockerManager.checkProcess("Dpkg")

					if self.dpkgResult:
						if not DpkgUnlocker.unlockerManager.removeAptLockLaunched:
							if "Apt" in DpkgUnlocker.unlockerManager.unlockInfo["unlockCmd"]:
								self.feedBackCode=DpkgUnlocker.DPKG_UNLOCK_COMMAND_RUNNING
								DpkgUnlocker.unlockerManager.removeAptLockLaunched=True
								self.currentCommand=DpkgUnlocker.unlockerManager.execCommand("Apt","remove")
								self.endCurrentCommand=True
								self.aptLockCheck=True
								DpkgUnlocker.unlockerManager.writeProcessLog(self.feedBackCode)
							else:
								DpkgUnlocker.unlockerManager.removeAptLockDone=True
								self.aptLockCheck=False
								self.aptResult=True	

						if DpkgUnlocker.unlockerManager.removeAptLockDone:
							if self.aptLockCheck:
								self.aptResult=DpkgUnlocker.unlockerManager.checkProcess("Apt")

							if self.aptResult:
								if not DpkgUnlocker.unlockerManager.fixingSystemLaunched:
									if DpkgUnlocker.unlockerManager.unlockInfo["commonCmd"]!="":
										self.feedBackCode=DpkgUnlocker.FIXING_UNLOCK_COMMAND_RUNNING
										DpkgUnlocker.unlockerManager.fixingSystemLaunched=True
										self.currentCommand=DpkgUnlocker.unlockerManager.execCommand("Fixing","fixing")
										self.endCurrentCommand=True
										self.fixingLockCheck=True
										DpkgUnlocker.unlockerManager.writeProcessLog(self.feedBackCode)
									else:
										DpkgUnlocker.unlockerManager.fixingSystemDone=True
										self.fixingLockCheck=False
										self.fixingResult=True

								if DpkgUnlocker.unlockerManager.fixingSystemDone:
									if self.fixingLockCheck:
										self.fixingResult=DpkgUnlocker.unlockerManager.checkProcess("Fixing")
									if self.fixingResult:
										self.unlockerProcessRunningTimer.stop()
										self.runningUnlockCommand=False
										self._gatherInfoThread()

									else:
										error=True
										code=DpkgUnlocker.FIXING_UNLOCK_COMMAND_ERROR
							else:
								error=True
								code=DpkgUnlocker.APT_UNLOCK_COMMAND_ERROR			
					else:
						error=True	
						code=DpkgUnlocker.DPKG_UNLOCK_COMMAND_ERROR								
			else:
				error=True
				code=DpkgUnlocker.LLXUP_UNLOCK_COMMAND_ERROR

			if error:
				self.runningUnlockCommand=False
				self.showServiceStatusMesage=[True,code,"Error"]
				self.unlockerProcessRunningTimer.stop()
				DpkgUnlocker.unlockerManager.writeProcessLog(code)
				self._gatherInfoThread()

		if DpkgUnlocker.unlockerManager.removeLlxupLockLaunched:
			if not DpkgUnlocker.unlockerManager.removeLlxupLockDone:
				if not os.path.exists(DpkgUnlocker.unlockerManager.tokenLlxupProcess[1]):
					DpkgUnlocker.unlockerManager.removeLlxupLockDone=True

		if DpkgUnlocker.unlockerManager.removeDpkgLockLaunched:
			if not DpkgUnlocker.unlockerManager.removeDpkgLockDone:
				if not os.path.exists(DpkgUnlocker.unlockerManager.tokenDpkgProcess[1]):
					DpkgUnlocker.unlockerManager.removeDpkgLockDone=True

		if DpkgUnlocker.unlockerManager.removeAptLockLaunched:
			if not DpkgUnlocker.unlockerManager.removeAptLockDone:
				if not os.path.exists(DpkgUnlocker.unlockerManager.tokenAptProcess[1]):
					DpkgUnlocker.unlockerManager.removeAptLockDone=True

		if DpkgUnlocker.unlockerManager.fixingSystemLaunched:
			if not DpkgUnlocker.unlockerManager.fixingSystemDone:
				if not os.path.exists(DpkgUnlocker.unlockerManager.tokenFixingProcess[1]):
					DpkgUnlocker.unlockerManager.fixingSystemDone=True

	@Slot()
	def getNewCommand(self):

		self.endCurrentCommand=False
		
	#def getNewCommand

	@Slot(bool)
	def getProtectionChange(self,change):
		
		if self.currentMetaProtectionStatus!=change:
			self.metaProtectionEnabled=change
			self.showProtectionStatusMessage=[False,"","Success"]
			self.isProtectionChange=True
		else:
			self.metaProtectionEnabled=self.currentMetaProtectionStatus
			self.showProtectionStatusMessage=self.currentMessage
			self.isProtectionChange=False

	#def getProtectionChange

	@Slot()
	def changeProteccionStatus(self):

		self.showDialog=False
		self.isWorked=True
		self.runningUnlockCommand=True
		self.isProtectionChange=False
		result=DpkgUnlocker.unlockerManager.changeMetaProtectionStatus(self.metaProtectionEnabled)
		if result:
			self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_CHANGE_SUCCESS,"Success"]
			self.currentMessage=copy.deepcopy(self.showProtectionStatusMessage)
			self.closeGui=True
		else:
			if self.metaProtectionEnabled:
				self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_DISABLED_ERROR,"Error"]
			else:
				self.showProtectionStatusMessage=[True,DpkgUnlocker.META_PROTECTION_ENABLED_ERROR,"Error"]
			self.closeGui=False
			self.moveToStack=""

		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
			self.moveToStack=""
		
		DpkgUnlocker.unlockerManager.getMetaProtectionStatus()	
		self._copyCurrentProtectionStatus()
		DpkgUnlocker.unlockerManager.writeLog("Final System Metapackage Protecion. Enabled: %s"%(str(self.metaProtectionEnabled)))
		
		self.isWorked=False	
		self.runningUnlockCommand=False

	#def changeProteccionStatus

	@Slot()
	def discardChangeProtectionStatus(self):

		self.showDialog=False
		self.showPendingChangesDialog=False
		self.isProtectionChange=False
		self.metaProtectionEnabled=self.currentMetaProtectionStatus
		self.showProtectionStatusMessage=self.currentMessage
		self.closeGui=True
		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
			self.moveToStack=""

	#def cancelChangeProtectionStatus

	@Slot() 
	def cancelAction(self):

		self.showDialog=False
		if self.showPendingChangesDialog:
			self.showPendingChangesDialog=False
			self.moveToStack=""

	#def cancelAction

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.moveToStack=stack
			if self.isProtectionChange:
				self.showDialog=True
				self.showPendingChangesDialog=True
			else:
				self.currentOptionsStack=stack
				self.moveToStack=""
	
	#def manageTransitions

	@Slot()
	def openHelp(self):
		
		runPkexec=False
		
		if "PKEXEC_UID" in os.environ:
			runPkexec=True

		if 'valencia' in DpkgUnlocker.unlockerManager.sessionLang:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker.'
		else:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker'
		
		if not runPkexec:
			self.helpCmd="su -c '%s' $USER"%self.helpCmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd="su -c '%s' %s"%(self.helpCmd,user)
		
		self.openHelpT=threading.Thread(target=self._openHelp)
		self.openHelpT.daemon=True
		self.openHelpT.start()

	#def openHelp

	def _openHelp(self):

		os.system(self.helpCmd)

	#def _openHelp

	@Slot()
	def closeApplication(self):

		if self.runningUnlockCommand:
			self.closeGui=False
		else:
			if not self.isProtectionChange:
				if self.isWorked:
					self.statusServicesRunningTimer.stop()
				self.closeGui=True
				DpkgUnlocker.unlockerManager.cleanLockToken()
				DpkgUnlocker.unlockerManager.writeLog("Quit")
			else:
				self.showDialog=True
				self.showPendingChangesDialog=True
				self.closeGui=False

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_isThereALock=Signal()
	isThereALock=Property(bool,_getIsThereALock,_setIsThereALock,notify=on_isThereALock)

	on_feedBackCode=Signal()
	feedBackCode=Property(int,_getFeedBackCode,_setFeedBackCode,notify=on_feedBackCode)
	
	on_showServiceStatusMesage=Signal()
	showServiceStatusMesage=Property('QVariantList',_getShowServiceStatusMesage,_setShowServiceStatusMesage,notify=on_showServiceStatusMesage)

	on_metaProtectionEnabled=Signal()
	metaProtectionEnabled=Property(int,_getMetaProtectionEnabled,_setMetaProtectionEnabled,notify=on_metaProtectionEnabled)
	
	on_showProtectionStatusMessage=Signal()
	showProtectionStatusMessage=Property('QVariantList',_getShowProtectionStatusMessage,_setShowProtectionStatusMessage,notify=on_showProtectionStatusMessage)

	on_isProtectionChange=Signal()
	isProtectionChange=Property(bool,_getIsProtectionChange,_setIsProtectionChange,notify=on_isProtectionChange)

	on_showDialog=Signal()
	showDialog=Property(bool,_getShowDialog,_setShowDialog,notify=on_showDialog)
	
	on_showPendingChangesDialog=Signal()
	showPendingChangesDialog=Property(bool,_getShowPendingChangesDialog,_setShowPendingChangesDialog,notify=on_showPendingChangesDialog)
	
	on_endProcess=Signal()
	endProcess=Property(bool,_getEndProcess,_setEndProcess, notify=on_endProcess)

	on_endCurrentCommand=Signal()
	endCurrentCommand=Property(bool,_getEndCurrentCommand,_setEndCurrentCommand, notify=on_endCurrentCommand)

	on_currentCommand=Signal()
	currentCommand=Property('QString',_getCurrentCommand,_setCurrentCommand, notify=on_currentCommand)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	servicesModel=Property(QObject,_getServicesModel,constant=True)


#class DpkgUnlocker

