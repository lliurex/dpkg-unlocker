#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	META_PROTECTION_ENABLED=6
	META_PROTECTION_DISABLED=7
	META_PROTECTION_CHANGE_SUCCESS=8
	META_PROTECTION_ENABLED_ERROR=-10
	META_PROTECTION_DISABLED_ERROR=-11

	metaProtectionEnabledChanged=Signal()
	showProtectionStatusMessageChanged=Signal()
	isProtectionChangeChanged=Signal()
	showPendingChangesDialogChanged=Signal()
	showProtectionOptionChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.unlockerManager=self.core.unlockerManager
		self._metaProtectionEnabled=True
		self._showProtectionStatusMessage={"show":False,"msgCode":"","type":""}
		self._isProtectionChange=False
		self._showPendingChangesDialog=False
		self._showProtectionOption=False

	#def __init__

	@Property(int,notify=metaProtectionEnabledChanged)
	def metaProtectionEnabled(self):

		return self._metaProtectionEnabled

	#def metaProtectionEnabled

	@metaProtectionEnabled.setter
	def metaProtectionEnabled(self,metaProtectionEnabled):

		if self._metaProtectionEnabled!=metaProtectionEnabled:
			self._metaProtectionEnabled=metaProtectionEnabled
			self.metaProtectionEnabledChanged.emit()

	#def metaProtectionEnabled

	@Property('QVariant',notify=showProtectionStatusMessageChanged)
	def showProtectionStatusMessage(self):

		return self._showProtectionStatusMessage

	#def showServiceStatusMesage

	@showProtectionStatusMessage.setter
	def showProtectionStatusMessage(self,showProtectionStatusMessage):

		if self._showProtectionStatusMessage!=showProtectionStatusMessage:
			self._showProtectionStatusMessage=showProtectionStatusMessage
			self.showProtectionStatusMessageChanged.emit()

	#def showProtectionStatusMessage

	@Property(bool,notify=isProtectionChangeChanged)
	def isProtectionChange(self):

		return self._isProtectionChange

	#def isProtectionChange

	@isProtectionChange.setter
	def isProtectionChange(self,isProtectionChange):

		if self._isProtectionChange!=isProtectionChange:
			self._isProtectionChange=isProtectionChange
			self.isProtectionChangeChanged.emit()
	
	#def isProtectionChange

	@Property(bool,notify=showPendingChangesDialogChanged)
	def showPendingChangesDialog(self):

		return self._showPendingChangesDialog

	#def showPendingChangesDialog

	@showPendingChangesDialog.setter
	def showPendingChangesDialog(self,showPendingChangesDialog):

		if self._showPendingChangesDialog!=showPendingChangesDialog:
			self._showPendingChangesDialog=showPendingChangesDialog
			self.showPendingChangesDialogChanged.emit()
	
	#def showPendingChangesDialog

	@Property(bool,notify=showProtectionOptionChanged)
	def showProtectionOption(self):

		return self._showProtectionOption

	#def showProtectionOption

	@showProtectionOption.setter
	def showProtectionOption(self,showProtectionOption):

		if self._showProtectionOption!=showProtectionOption:
			self._showProtectionOption=showProtectionOption
			self.showProtectionOptionChanged.emit()

	#def showProtectionOption

	def loadConfig(self):		

		self.metaProtectionEnabled=self.unlockerManager.metaProtectionEnabled
		self.showProtectionOption=self.unlockerManager.showProtectionOption()

		if self.metaProtectionEnabled:
			self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_ENABLED,"type":self.unlockerManager.KIRIGAMI_MSG_OK}
		else:
			self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_DISABLED,"type":self.unlockerManager.KIRIGAMI_MSG_WARNING}

		self._copyCurrentProtectionStatus()
	
	#def loadConfig

	def updateProtectionInfo(self):

		if not self.isProtectionChange:
			self.metaProtectionEnabled=self.unlockerManager.metaProtectionEnabled
			if self.metaProtectionEnabled:
				self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_ENABLED,"type":self.unlockerManager.KIRIGAMI_MSG_OK}
			else:
				self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_DISABLED,"type":self.unlockerManager.KIRIGAMI_MSG_WARNING}

			self._copyCurrentProtectionStatus()

	#def updateProtection Info

	def _copyCurrentProtectionStatus(self):

		self.currentMetaProtectionStatus=copy.deepcopy(self.metaProtectionEnabled)
		self.currentMessage=copy.deepcopy(self.showProtectionStatusMessage)

	#def _copyCurrentProtectionStatus

	@Slot(bool)
	def getProtectionChange(self,change):
		
		self.metaProtectionEnabled=change
		
		if self.currentMetaProtectionStatus!=change:
			self.showProtectionStatusMessage={"show":False,"msgCode":"","type":""}
			self.isProtectionChange=True
		else:
			self.showProtectionStatusMessage=self.currentMessage
			self.isProtectionChange=False

	#def getProtectionChange

	@Slot()
	def changeProteccionStatus(self):

		self.core.mainStack.showDialog=False
		self.core.mainStack.isWorked=True
		self.core.mainStack.runningUnlockCommand=True
		self.isProtectionChange=False
		self.showPendingChangesDialog=False

		result=self.unlockerManager.changeMetaProtectionStatus(self.metaProtectionEnabled)
		if result:
			self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_CHANGE_SUCCESS,"type":self.unlockerManager.KIRIGAMI_MSG_OK}
			self.currentMessage=copy.deepcopy(self.showProtectionStatusMessage)
			self.core.mainStack.closeGui=True
		else:
			if self.metaProtectionEnabled:
				self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_DISABLED_ERROR,"type":self.unlockerManager.KIRIGAMI_MSG_ERROR}
			else:
				self.showProtectionStatusMessage={"show":True,"msgCode":Bridge.META_PROTECTION_ENABLED_ERROR,"type":self.unlockerManager.KIRIGAMI_MSG_ERROR}
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.core.mainStack.moveToStack=""
		
		self.unlockerManager.getMetaProtectionStatus()	
		self._copyCurrentProtectionStatus()
		self.unlockerManager.writeLog(f"Final System Metapackage Protecion. Enabled: {self.metaProtectionEnabled}")
		
		self.core.mainStack.isWorked=False	
		self.core.mainStack.runningUnlockCommand=False

	#def changeProteccionStatus

	@Slot()
	def discardChangeProtectionStatus(self):

		self.core.mainStack.showDialog=False
		self.showPendingChangesDialog=False
		self.isProtectionChange=False
		self.metaProtectionEnabled=self.currentMetaProtectionStatus
		self.showProtectionStatusMessage=self.currentMessage
		self.core.mainStack.closeGui=True
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.core.mainStack.moveToStack=""

	#def discardChangeProtectionStatus

	
#class Bridge

from . import Core

