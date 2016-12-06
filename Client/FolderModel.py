#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore

class FolderItem(object):
    def __init__(self, type, id, name, icon):
        self.type = type
        self.id = id
        self.name = name
        self.icon = icon

class FolderModel(QtCore.QAbstractListModel): 
    def __init__(self):
        QtCore.QAbstractListModel.__init__(self)
        self.record = []
        
    def setDataList(self, list):
        self.record = []
        for record in list:
            self.record.append(FolderItem(*record))
        self. modelReset.emit()
    
    def rowCount(self, parent):
        return len(self.record)
        
    def data(self, index, role):
        if index.isValid() and role==QtCore.Qt.DisplayRole:
            return self.record[index.row()].name
        elif index.isValid() and role==QtCore.Qt.DecorationRole:
            type = self.record[index.row()].type
            if type==0:
                icon = QtGui.QIcon("user.png")
            elif type==1:
                icon = QtGui.QIcon("folder.png")
            else:
                s = self.record[index.row()].icon
                if s=="":
                    s = "file.png"
                icon = QtGui.QIcon(s)
            return icon
        elif index.isValid() and role==QtCore.Qt.UserRole:
            return self.record[index.row()].id
        elif index.isValid() and role==QtCore.Qt.UserRole+1:
            return self.record[index.row()].type
        else:
            return None
