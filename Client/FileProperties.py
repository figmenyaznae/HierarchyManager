#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore, uic
from DbConfig import *
from DbModel import *
from utils import *

class FileProperties(QtGui.QDialog):
    def __init__(self, parent, folder):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("FileProperties.ui", self)
        self.folderID = folder
        self.session = Session()
        self.navigationFrame.setVisible(False)
        
        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.declineButton, QtCore.SIGNAL("clicked()"), self.close)
        self.connect(self.ui.openDialog, QtCore.SIGNAL("clicked()"), self.fileDialog)
        
        
        self.ui.fileExt.addItem("-",QtCore.QVariant(0))
        for ext in self.session.query(FileExtension).all():
            self.ui.fileExt.addItem(ext.name, QtCore.QVariant(ext.id))
    
    def fileDialog(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        #TODO filtering
        if dialog.exec_():
            fileNames = dialog.selectedFiles();
        print [s for s in fileNames]
        self.ui.filePath.setText(dialog)
    
    def accept(self):
        parent = self.session.query(Node).filter(Node.id==self.folderID).one()
        
        extensionId = self.ui.fileExt.itemData(self.ui.fileExt.currentIndex()).toInt()[0]
        if extensionId!=0:
            extension = self.session.query(FileExtension)\
                .filter(FileExtension.id==extensionId).one()
        else:
            extension = None
        
        self.session.add(File(
            name = wrapNone(self.ui.nameEdit.text()),
            extension = extension,
            path = wrapNone(self.ui.filePath.text()),
            is_shared = self.isShared.checkState()==QtCore.Qt.Checked,
            folders=[parent]
        ))
        self.session.commit()
        self.parent().model.setDataList(self.parent().execQuery())
        self.close()
