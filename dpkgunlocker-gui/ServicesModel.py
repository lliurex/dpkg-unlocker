#!/usr/bin/python3
import os
import sys
from PySide2 import QtCore, QtGui, QtQml

class ServicesModel(QtCore.QAbstractListModel):

	ServiceIdRole= QtCore.Qt.UserRole + 1000
	StatusCodeRole = QtCore.Qt.UserRole + 1001

	def __init__(self,parent=None):
		
		super(ServicesModel, self).__init__(parent)
		self._entries =[]
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == ServicesModel.ServiceIdRole:
				return item["serviceId"]
			elif role == ServicesModel.StatusCodeRole:
				return item["statusCode"]
	#def data

	def roleNames(self):
		
		roles = dict()
		roles[ServicesModel.ServiceIdRole] = b"serviceId"
		roles[ServicesModel.StatusCodeRole] = b"statusCode"

		return roles

	#def roleName

	def appendRow(self,si,sc):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(serviceId=si, statusCode=sc))
		self.endInsertRows()

	#def appendRow

	def setData(self, index, param, value, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			if param in ["statusCode"]:
				self._entries[row][param]=value
				self.dataChanged.emit(index,index)
				return True
			else:
				return False
	
	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class GroupModel
