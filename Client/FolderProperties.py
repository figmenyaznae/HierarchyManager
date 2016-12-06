#!/usr/bin/python2.7
from PyQt4 import QtGui, QtCore, QtSql, uic
from DbConfig import *
from DbModel import *
from utils import *

class FolderProperties(QtGui.QDialog):
    def __init__(self, parent, parentFolder, user, folder = 0):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("FolderProperties.ui", self)
        self.parentID = parentFolder
        self.userID = user
        #self.selfID = folder #TODO
        self.session = Session()
        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.declineButton, QtCore.SIGNAL("clicked()"), self.close)
        
    def accept(self):
        node = Node(
            name=wrapNone(self.ui.nameEdit.text()),
            user_id=self.userID,
            is_shared=self.isShared.checkState()==QtCore.Qt.Checked
        )
        
        if self.parentID!=0:
            parent = self.session.query(Node).filter(Node.id==self.parentID).one()
            node.parent = [parent]
        
        self.session.add(node)
        self.session.commit()
        self.parent().model.setDataList(self.parent().execQuery())
        self.close()
