#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore, uic
from DbConfig import *
from DbModel import *
from utils import *

class EditedFile(object):
    def __init__(self, name, ext_id, path, is_shared):
        self.name = name
        self.ext_id = ext_id
        self.path = path
        self.is_shared = is_shared

class FileProperties(QtGui.QDialog):
    def __init__(self, parent, user, folder):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("FileProperties.ui", self)
        self.userID = user
        self.folderID = folder
        self.multipleFiles = None
        self.fileNo = 0
        self.session = Session()
        self.navigationFrame.setVisible(False)
        
        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.declineButton, QtCore.SIGNAL("clicked()"), self.close)
        self.connect(self.ui.openDialog, QtCore.SIGNAL("clicked()"), self.fileDialog)
        self.connect(self.ui.prevButton, QtCore.SIGNAL("clicked()"), self.prevClicked)
        self.connect(self.ui.nextButton, QtCore.SIGNAL("clicked()"), self.nextClicked)
        
        
        self.ui.fileExt.addItem("-",QtCore.QVariant(0))
        for ext in self.session.query(FileExtension).all():
            self.ui.fileExt.addItem(ext.name, QtCore.QVariant(ext.id))
    
    def fileDialog(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        s = ['All (*)']
        for ext in self.session.query(FileExtension).all():
            s.append('{} ({})'.format(ext.name, ext.mask))
        dialog.setFilters(s)
        dialog.selectFilter(s[self.ui.fileExt.currentIndex()])
        if dialog.exec_():
            fileNames = dialog.selectedFiles();
            if len(fileNames)>1:
                self.ui.navigationFrame.setVisible(True)
                self.multipleFiles = []
                for file in fileNames:
                    self.multipleFiles.append(EditedFile(
                        name = getFileName(file),
                        path = file,
                        ext_id = self.ui.fileExt.currentIndex(),
                        is_shared = self.ui.isShared.checkState() == QtCore.Qt.Checked
                    ))
                    self.resetState(lambda x: 0)
            else:
                self.ui.nameEdit.setText(getFileName(fileNames[0]))
                self.ui.filePath.setText(fileNames[0])
    
    def saveState(self):        
        self.multipleFiles[self.fileNo] = EditedFile(
            name = self.ui.nameEdit.text(),
            ext_id = self.ui.fileExt.currentIndex(),
            path = self.ui.filePath.text(),
            is_shared = self.ui.isShared.checkState() == QtCore.Qt.Checked
        )
    
    def resetState(self, change):        
        self.fileNo = change(self.fileNo)
        self.ui.prevButton.setEnabled(True)
        self.ui.nextButton.setEnabled(True)
        if self.fileNo == 0:
            self.ui.prevButton.setEnabled(False)
        elif self.fileNo == len(self.multipleFiles) - 1:
            self.ui.nextButton.setEnabled(False)
        
        self.ui.progressLabel.setText(
            '{}/{}'.format(self.fileNo + 1, len(self.multipleFiles))
        )
        
        file = self.multipleFiles[self.fileNo]
        self.ui.nameEdit.setText(file.name)
        self.ui.fileExt.setCurrentIndex(file.ext_id)
        self.ui.filePath.setText(file.path)
        self.ui.isShared.setChecked(file.is_shared)
    
    def prevClicked(self):
        self.saveState()
        self.resetState(lambda x: x - 1)
    
    def nextClicked(self):
        self.saveState()
        self.resetState(lambda x: x + 1)
    
    def accept(self):
        parent = self.session.query(Node).filter(Node.id==self.folderID).one()
        
        if not self.multipleFiles:
            self.multipleFiles = []
            self.saveState()
            
        for file in self.multipleFiles:
            extensionId = self.ui.fileExt.itemData(file.ext_id).toInt()[0]
            if extensionId!=0:
                extension = self.session.query(FileExtension)\
                    .filter(FileExtension.id==extensionId).one()
            else:
                extension = None
            
            self.session.add(File(
                name = wrapNone(file.name),
                extension = extension,
                path = wrapNone(file.path),
                is_shared = file.is_shared,
                user_id = self.userID,
                folders=[parent]
            ))
            
        self.session.commit()
        self.parent().model.setDataList(self.parent().execQuery())
        self.close()
