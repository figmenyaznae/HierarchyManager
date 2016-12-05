#!/usr/bin/python2.7

from PyQt4 import QtGui, QtCore, QtSql, uic
from FolderModel import *
from FolderProperties import *
from FileProperties import *
import Queries
DBFolderIDRole = QtCore.Qt.UserRole

class FolderView(QtGui.QDialog):
    def __init__(self, parent, UserID, sharedOnly = False, otherUser = 0):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("FolderView.ui", self)
        
        self.Other = otherUser
        self.UserID = UserID
        self.sharedOnly = sharedOnly
        self.parent = parent
        self.folder = 0
        self.copy = None
        self.FileID = 0
        
        self.CommentsModel = QtSql.QSqlQueryModel()
        self.CommentsModel.setQuery(self.commentQuery())
        self.ui.comentsList.setModel(self.CommentsModel)
        self.ui.comentsList.setModelColumn(2)
        
        self.model = FolderModel()
        self.model.setQuery(self.execQuery())
        
        home = QtGui.QListWidgetItem('Home >')
        home.setData(DBFolderIDRole,0)
        self.ui.history.addItem(home)
        self.ui.history.setCurrentItem(self.ui.history.item(0))
        
        self.ui.mainView.setModel(self.model)
        self.ui.mainView.doubleClicked.connect(self.doubleClicked)
        self.ui.mainView.customContextMenuRequested.connect(self.AddFileContextMenu)
        self.ui.mainView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.ui.history.itemClicked.connect(self.selectFolder)
        
        self.connect(self.ui.submitComment, QtCore.SIGNAL("clicked()"), self.createComment)
        
        self.ui.frame.setVisible(False)
        
    def execQuery(self):
        if self.folder>0:
            if self.sharedOnly:
                query = QtSql.QSqlQuery(Queries.SELECT['SharedFolder'])
                query.bindValue(0, self.Other)
            else:
                query = QtSql.QSqlQuery(Queries.SELECT['nonSharedFolder'])
                query.bindValue(0, self.UserID)
            query.bindValue(1, self.folder)
            query.bindValue(2, self.folder)
        else:
            if self.sharedOnly:
                query = QtSql.QSqlQuery(Queries.SELECT['SharedRoot'])
                query.bindValue(0, self.Other)
            else:
                query = QtSql.QSqlQuery(Queries.SELECT['nonSharedRoot'])
                query.bindValue(0, self.UserID)
                query.bindValue(1, self.UserID)
        
        query.exec_()
        return query
    
    def createComment(self):
        query = QtSql.QSqlQuery(Queries.INSERT['Comment'])
        query.bindValue(0, self.UserID)
        query.bindValue(1, self.FileID)
        query.bindValue(2, self.ui.myComment.text())
        if query.exec_():
            self.ui.myComment.setText("")
            self.CommentsModel.setQuery(self.commentQuery())
    
    def commentQuery(self):
        query = QtSql.QSqlQuery(Queries.SELECT['Comments'])
                                
        query.bindValue(0, self.FileID)
        query.exec_()
        return query
    
    def ratingStr(self, rating):
        s = ""
        for i in xrange(rating):
            s += "*"
        for i in xrange(rating,5):
            s += "-"
        return s
    
    def doubleClicked(self, index):
        self.ui.frame.setVisible(False)
        i = index.row()
        if self.model.record(i).value(0).toInt()[0]==0:
            self.otherView = FolderView(self, self.UserID, True, self.model.record(i).value(1).toInt()[0])
            self.otherView.open()
            if self.otherView.copy is not None:
                self.copy = self.otherView.copy
        elif self.model.record(i).value(0).toInt()[0]==1:
            self.folder = self.model.record(i).value(1).toInt()[0]
            folder = QtGui.QListWidgetItem(self.model.record(i).value(2).toString()+" >")
            folder.setData(DBFolderIDRole,self.folder)
            self.ui.history.addItem(folder)
            self.ui.history.setCurrentItem(self.ui.history.item(self.ui.history.count()-1))
            self.model.setQuery(self.execQuery())
        else:
            self.FileID = self.model.record(i).value(1).toInt()[0]
            self.ui.fileName.setText("File: " + self.model.record(i).value(2).toString())
            self.ui.rating.setText("Rating: " + self.ratingStr(self.model.record(i).value(4).toInt()[0]))
            self.ui.shared.setText("Shared: " + str(self.model.record(i).value(5).toInt()[0]>0))
            self.CommentsModel.setQuery(self.commentQuery())
            self.ui.frame.setVisible(True)
        
    def selectFolder(self, item):
        self.ui.frame.setVisible(False)
        self.folder = item.data(DBFolderIDRole).toInt()[0]
        self.model.setQuery(self.execQuery())
        hist = [ (
                self.ui.history.item(i).text(),
                self.ui.history.item(i).data(DBFolderIDRole).toInt()[0]
            ) for i in xrange(self.ui.history.currentRow()+1)]
        self.ui.history.clear()
        for item in hist:
            folder = QtGui.QListWidgetItem(item[0])
            folder.setData(DBFolderIDRole,item[1])
            self.ui.history.addItem(folder)
        self.ui.history.setCurrentItem(self.ui.history.item(self.ui.history.count()-1))
    
    def AddFileContextMenu(self, point):
        self.fileAddMenu = QtGui.QMenu()
        if not self.sharedOnly:
            self.fileAddMenu.addAction("Add folder", self.folderAdd)
            if self.folder != 0:
                self.fileAddMenu.addAction("Add file", self.fileAdd)
        if len(self.ui.mainView.selectedIndexes())>0:
            self.fileAddMenu.addAction("Copy", self.objCopy)
        if self.copy!=None:
            self.fileAddMenu.addAction("Paste", self.objPaste)
        if len(self.ui.mainView.selectedIndexes())>0:
            self.fileAddMenu.addAction("Delete", self.objDelete)    
        self.fileAddMenu.popup(self.mapToGlobal(point))
    
    def folderAdd(self):
        self.FP = FolderProperties(self, self.folder, self.UserID)
        self.FP.open()
    
    def fileAdd(self):
        self.FP = FileProperties(self, self.folder)
        self.FP.open()
        
    def objCopy(self):
        indexes = self.ui.mainView.selectedIndexes()
        self.copy = []
        for i in indexes:
            type = self.model.record(i.row()).value(0).toInt()[0]
            if type!=0:
                rec = {'Type':type, 'ID':self.model.record(i.row()).value(1).toInt()[0]}
                self.copy.append(rec)
    
    def objPaste(self):
        if self.copy!=None:
            for index in self.copy:
                if index['Type'] == 1:
                    query = QtSql.QSqlQuery(Queries.INSERT['PasteFolder'])
                    query.bindValue(0, index['ID'])
                    query.bindValue(1, self.folder)
                    query.bindValue(2, self.UserID)
                    query.exec_()
                else:
                    query = QtSql.QSqlQuery(Queries.INSERT['PasteFile'])
                    query.bindValue(0, self.folder)
                    query.bindValue(1, index['ID'])
                    query.exec_()
        
        self.model.setQuery(self.execQuery())
        
    def objDelete(self):
        indexes = self.ui.mainView.selectedIndexes()
        for i in indexes:
            type = self.model.record(i.row()).value(0).toInt()[0]
            id = self.model.record(i.row()).value(1).toInt()[0]
            print type, id
            if type==2:
                query = QtSql.QSqlQuery(Queries.DELETE['FileFromFolder'])
                query.bindValue(0, id)
                query.bindValue(1, self.folder)
                query.exec_()
                
                query = QtSql.QSqlQuery(Queries.SELECT['FileBindings'])
                query.bindValue(0, id)
                query.exec_()
                if (query.numRowsAffected()==0):
                    query = QtSql.QSqlQuery(Queries.DELETE['FileCompletely'])
                    query.bindValue(0, id)
                    query.exec_()
                    
        self.model.setQuery(self.execQuery())
