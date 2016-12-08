#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore

ItemNameRole = QtCore.Qt.DisplayRole
ItemIconRole = QtCore.Qt.DecorationRole
ItemIDRole = QtCore.Qt.UserRole
ItemTypeRole = QtCore.Qt.UserRole+1
#TODO
ItemRatingRole = QtCore.Qt.UserRole+2
ItemIsSharedRole = QtCore.Qt.UserRole+3

class FolderItem(object):
    def __init__(self, type, id, name, icon = '', rating = 0, is_shared = False):
        self.type = type
        self.id = id
        self.name = name
        self.icon = icon
        self.rating = rating
        self.is_shared = is_shared

class FolderModel(QtCore.QAbstractListModel): 
    def __init__(self):
        QtCore.QAbstractListModel.__init__(self)
        self.record = []
        
    def setDataList(self, list):
        self.record = []
        for record in list:
            self.record.append(record)
        self. modelReset.emit()
    
    def rowCount(self, parent):
        return len(self.record)
        
    def data(self, index, role):
        if index.isValid() and role==ItemNameRole:
            return self.record[index.row()].name
        elif index.isValid() and role==ItemIconRole:
            type = self.record[index.row()].type
            if type==0:
                icon = QtGui.QIcon("user.png")
            elif type==1:
                icon = QtGui.QIcon("folder.png")
            else:
                s = self.record[index.row()].icon
                if s is None or s=="":
                    s = "file.png"
                icon = QtGui.QIcon(s)
            return icon
        elif index.isValid() and role==ItemIDRole:
            return self.record[index.row()].id
        elif index.isValid() and role==ItemTypeRole:
            return self.record[index.row()].type
        elif index.isValid() and role==ItemRatingRole:
            return self.record[index.row()].rating
        elif index.isValid() and role==ItemIsSharedRole:
            return self.record[index.row()].is_shared
        else:
            return None
