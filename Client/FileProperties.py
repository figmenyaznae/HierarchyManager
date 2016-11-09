#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore, QtSql, uic
import Queries

class FileProperties(QtGui.QDialog):
    def __init__(self, parent, folder):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("FileProperties.ui", self)
        self.FolderID = folder
        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.declineButton, QtCore.SIGNAL("clicked()"), self.close)
        self.connect(self.ui.openDialog, QtCore.SIGNAL("clicked()"), self.fileDialog)
        
        self.ui.fileExt.addItem("-",QtCore.QVariant(0))
        query = QtSql.QSqlQuery(Queries.SELECT['Extensions'])
        query.exec_()
        query.first()
        self.ui.fileExt.addItem(query.record().value(1).toString(),QtCore.QVariant(query.record().value(0).toInt()[0]))
        while query.next():
            self.ui.fileExt.addItem(query.record().value(1).toString(),QtCore.QVariant(query.record().value(0).toInt()[0]))
    
    def fileDialog(self):
        dialog = QtGui.QFileDialog.getOpenFileName()
        self.ui.filePath.setText(dialog)
    
    def accept(self):
        ExtId = self.ui.fileExt.itemData(self.ui.fileExt.currentIndex()).toInt()[0]
        query = QtSql.QSqlQuery(Queries.INSERT['File'])
        query.bindValue(0, self.ui.nameEdit.text())
        if ExtId > 0:
            query.bindValue(1, ExtId)
        query.bindValue(2, self.ui.filePath.text())
        query.bindValue(3, int(self.isShared.checkState()==QtCore.Qt.Checked))
        query.exec_()
        self.selfID = query.lastInsertId().toInt()[0]
        
        if self.FolderID>0:
            query = QtSql.QSqlQuery(Queries.INSERT['PasteFile'])
            query.bindValue(0, self.FolderID)
            query.bindValue(1, self.selfID)
            query.exec_()
        
        self.parent().model.setQuery(self.parent().execQuery())
        self.close()
