#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore, QtSql

class FolderModel(QtSql.QSqlQueryModel): 
    def __init__(self):
        QtSql.QSqlQueryModel.__init__(self)
        
    def data (self, index, role):
        if index.isValid() and role==QtCore.Qt.DisplayRole:
            return self.record(index.row()).value(2).toString()
        elif index.isValid() and role==QtCore.Qt.DecorationRole:
            type = self.record(index.row()).value(0).toInt()[0]
            if type==0:
                icon = QtGui.QIcon("user.png")
            elif type==1:
                icon = QtGui.QIcon("folder.png")
            else:
                s = self.record(index.row()).value(3).toString()
                if s=="":
                    s = "file.png"
                icon = QtGui.QIcon(s)
            return icon
        else:
            return QtSql.QSqlQueryModel.data(self, index, role)
