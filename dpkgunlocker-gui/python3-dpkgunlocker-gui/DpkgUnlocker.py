#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import UnlockerManager
import ServicesModel
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
		self.tmpNewUser=""
		self.moveToStack=""
		self.statusServicesRunningTimer=QTimer(None)
		self.statusServicesRunningTimer.timeout.connect(self._updateServicesStatus)
		self.statusServicesRunningTimer.start(5000)
		self.isWorked=True
		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._loadConfig)

	#def initBridge

	def _loadConfig(self):		

		self.isThereALock=DpkgUnlocker.unlockerManager.isThereALock
		if self._isThereALock:
			self._updateServiceStatusMessage(12)
		else:
			self._updateServiceStatusMessage(0)
		self._updateServicesModel()
		self.currentStack=1

	#def _loadConfig

	def _updateServicesStatus(self):

		if not self.isWorked:
			self.isWorked=True
			self.gatherInfo=GatherInfo()
			self.gatherInfo.start()
			self.gatherInfo.finished.connect(self._updateServicesInfo)
	
	#def _updateServicesModel

	def _updateServicesInfo(self):

		self.isThereALock=DpkgUnlocker.unlockerManager.isThereALock
		if self._isThereALock:
			self._updateServiceStatusMessage(12)
		else:
			self._updateServiceStatusMessage(0)
		
		updatedInfo=DpkgUnlocker.unlockerManager.servicesData
		for i in range(len(updatedInfo)):
			index=self._servicesModel.index(i)
			self._servicesModel.setData(index,'statusCode',updatedInfo[i]["statusCode"])

		self.isWorked=False

	#def _updateServicesInfo

	def _updateServiceStatusMessage(self,code):

		infoCode=[0,12]

		if code in infoCode:
			self.showServiceStatusMesage=[True,code,"Info"]

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

	def _getShowServiceStatusMesage(self):

		return self._showServiceStatusMesage

	#def _getShowServiceStatusMesage

	def _setShowServiceStatusMesage(self,showServiceStatusMesage):

		if self._showServiceStatusMesage!=showServiceStatusMesage:
			self._showServiceStatusMesage=showServiceStatusMesage
			self.on_showServiceStatusMesage.emit()

	#def _setShowServiceStatusMesage	

	def _getClosePopUp(self):

		return self._closePopUp

	#def _getClosePopUp	

	def _setClosePopUp(self,closePopUp):
		
		if self._closePopUp!=closePopUp:
			self._closePopUp=closePopUp		
			self.on_closePopUp.emit()

	#def _setClosePopUp	

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

	@Slot()
	def launchUnlockProcess(self):

		print("Aplicando")

	#def launchUnlockProcess

	@Slot()
	def openHelp(self):
		
		if 'valencia' in self.unlockerManager.sessionLang:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker.'
		else:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker'
		
		self.open_help_t=threading.Thread(target=self._openHelp)
		self.open_help_t.daemon=True
		self.open_help_t.start()

	#def openHelp

	def _openHelp(self):

		os.system(self.help_cmd)

	#def _openHelp

	@Slot()
	def closeApplication(self):

		self.closeGui=True

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_isThereALock=Signal()
	isThereALock=Property(bool,_getIsThereALock,_setIsThereALock,notify=on_isThereALock)
	
	on_showServiceStatusMesage=Signal()
	showServiceStatusMesage=Property('QVariantList',_getShowServiceStatusMesage,_setShowServiceStatusMesage,notify=on_showServiceStatusMesage)
	on_closePopUp=Signal()
	closePopUp=Property(bool,_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	servicesModel=Property(QObject,_getServicesModel,constant=True)


#class DpkgUnlocker

