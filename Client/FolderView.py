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
        self.setWindowTitle("Hierarchy Manager")
        self.Other = otherUser
        self.UserID = UserID
        self.sharedOnly = sharedOnly
        self.parent = parent
        self.folder = 0
        self.copy = None
        
        self.model = FolderModel()
        self.model.setQuery(self.execQuery())
        
        self.View = QtGui.QListView(self)
        self.View.setModel(self.model)
        self.View.setSpacing(10)
        self.View.setViewMode(QtGui.QListView.IconMode)
        self.View.doubleClicked.connect(self.doubleClicked)
        self.View.customContextMenuRequested.connect(self.AddFileContextMenu)
        self.View.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.history = QtGui.QListWidget()
        self.history.setFlow(QtGui.QListView.LeftToRight)
        self.history.setMaximumHeight(25)
        self.history.itemClicked.connect(self.selectFolder)
        
        home = QtGui.QListWidgetItem('Home >')
        home.setData(DBFolderIDRole,0)
        self.history.addItem(home)
        self.history.setCurrentItem(self.history.item(0))
        
        self.FileName = QtGui.QLabel("File: ")
        self.Rating = QtGui.QLabel("Rating:")
        self.Shared = QtGui.QLabel("Rating:")
        CommentLabel = QtGui.QLabel("Comments")
        
        self.FileID = 0
        self.CommentsModel = QtSql.QSqlQueryModel()
        self.CommentsModel.setQuery(self.commentQuery())
        self.Comments = QtGui.QListView()
        self.Comments.setModel(self.CommentsModel)
        self.Comments.setModelColumn(2)
        self.Comments.setMaximumWidth(300)
        self.Comments.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.Comments.setWordWrap(True)
        
        main = QtGui.QHBoxLayout()
        
        box = QtGui.QVBoxLayout()
        box.addWidget(self.history)
        box.addWidget(self.View)
        main.addLayout(box)
        
        self.myComment = QtGui.QLineEdit(self)
        SubmitComment = QtGui.QPushButton("Submit")
        self.connect(SubmitComment, QtCore.SIGNAL("clicked()"), self.createComment)
        
        input = QtGui.QHBoxLayout()
        input.addWidget(self.myComment)
        input.addWidget(SubmitComment)
        
        box = QtGui.QVBoxLayout()
        box.addWidget(self.FileName)
        box.addWidget(self.Rating)
        box.addWidget(self.Shared)
        box.addWidget(CommentLabel)
        box.addWidget(self.Comments)
        box.addLayout(input)
        self.frame = QtGui.QFrame()
        self.frame.setLayout(box)
        self.frame.setVisible(False)
        main.addWidget(self.frame)
        self.setLayout(main)
        self.resize(700, 500)
        
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
        query = QtSql.QSqlQuery(Queries.CREATE['Comment'])
        query.bindValue(0, self.UserID)
        query.bindValue(1, self.FileID)
        query.bindValue(2, self.myComment.text())
        if query.exec_():
            self.myComment.setText("")
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
        self.frame.setVisible(False)
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
            self.history.addItem(folder)
            self.history.setCurrentItem(self.history.item(self.history.count()-1))
            self.model.setQuery(self.execQuery())
        else:
            self.FileID = self.model.record(i).value(1).toInt()[0]
            self.FileName.setText("File: " + self.model.record(i).value(2).toString())
            self.Rating.setText("Rating: " + self.ratingStr(self.model.record(i).value(4).toInt()[0]))
            self.Shared.setText("Shared: " + str(self.model.record(i).value(5).toInt()[0]>0))
            self.CommentsModel.setQuery(self.commentQuery())
            self.frame.setVisible(True)
        
    def selectFolder(self, item):
        self.frame.setVisible(False)
        self.folder = item.data(DBFolderIDRole).toInt()[0]
        self.model.setQuery(self.execQuery())
        hist = [(self.history.item(i).text(),self.history.item(i).data(DBFolderIDRole).toInt()[0]) for i in xrange(self.history.currentRow()+1)]
        self.history.clear()
        for item in hist:
            folder = QtGui.QListWidgetItem(item[0])
            folder.setData(DBFolderIDRole,item[1])
            self.history.addItem(folder)
        self.history.setCurrentItem(self.history.item(self.history.count()-1))
    
    def AddFileContextMenu(self, point):
        self.fileAddMenu = QtGui.QMenu()
        if not self.sharedOnly:
            self.fileAddMenu.addAction("Add folder", self.folderAdd)
            if self.folder != 0:
                self.fileAddMenu.addAction("Add file", self.fileAdd)
        if len(self.View.selectedIndexes())>0:
            self.fileAddMenu.addAction("Copy", self.objCopy)
        if self.copy!=None:
            self.fileAddMenu.addAction("Paste", self.objPaste)
        if len(self.View.selectedIndexes())>0:
            self.fileAddMenu.addAction("Delete", self.objDelete)
        self.fileAddMenu.popup(self.pos() + point)
    
    def folderAdd(self):
        self.FP = FolderProperties(self, self.folder, self.UserID)
        self.FP.open()
    
    def fileAdd(self):
        self.FP = FileProperties(self, self.folder)
        self.FP.open()
        
    def objCopy(self):
        indexes = self.View.selectedIndexes()
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
        indexes = self.View.selectedIndexes()
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
