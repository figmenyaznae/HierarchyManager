#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore, QtSql, uic
import Queries

class FolderProperties(QtGui.QDialog):
    def __init__(self, parent, parentFolder, user, folder = 0):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("FolderProperties.ui", self)
        self.FolderID = parentFolder
        self.UserID = user
        self.selfID = folder
        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.declineButton, QtCore.SIGNAL("clicked()"), self.close)
        
    def accept(self):
        query = QtSql.QSqlQuery(Queries.INSERT['Folder'])
        query.bindValue(0, self.ui.nameEdit.text())
        query.bindValue(1, self.UserID)
        query.bindValue(2, int(self.isShared.checkState()==QtCore.Qt.Checked))
        query.exec_()
        self.selfID = query.lastInsertId().toInt()[0]
        
        if self.FolderID>0:
            query = QtSql.QSqlQuery(Queries.INSERT['PasteFolder'])
            query.bindValue(0, self.selfID)
            query.bindValue(1, self.FolderID)
            query.bindValue(2, self.UserID)
            query.exec_()
        
        self.parent().model.setQuery(self.parent().execQuery())
        self.close()
