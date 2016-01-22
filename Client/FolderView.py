#!/usr/bin/python2.7

from PyQt4 import QtGui, QtCore, QtSql, uic
from FolderModel import *
from FolderProperties import *
from FileProperties import *
DBFolderIDRole = QtCore.Qt.UserRole

class obj(object):
    pass

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
                query = QtSql.QSqlQuery("select 1 as Type, NodeID as ID, NodeName as Name,\
                    NULL as Icon, NULL as Rating, IsShared\
                    from Nodes left join Edges on Nodes.NodeID=Edges.ChildID\
                    where Nodes.UserID=? and Edges.ParentID=? and IsShared=1\
                    \
                    union\
                    \
                    select 2 as Type, Files.FileID as ID, Files.Name as Name,\
                    FileExtensions.Icon as Icon, Ratings.Value as Rating, Files.IsShared\
                    from Files left join NodeFiles on NodeFiles.FileID=Files.FileID\
                    left join FileExtensions on Files.ExtensionID=FileExtensions.ExtensionID\
                    left join Ratings on Ratings.FileID=Files.FileID\
                    where NodeFiles.NodeID=? and IsShared=1;")
                query.bindValue(0, self.Other)
            else:
                query = QtSql.QSqlQuery("select 1 as Type, NodeID as ID, NodeName as Name,\
                    NULL as Icon, NULL as Rating, IsShared\
                    from Nodes left join Edges on Nodes.NodeID=Edges.ChildID\
                    where Nodes.UserID=? and Edges.ParentID=?\
                    \
                    union\
                    \
                    select 2 as Type, Files.FileID as ID, Files.Name as Name,\
                    FileExtensions.Icon as Icon, Ratings.Value as Rating, Files.IsShared\
                    from Files left join NodeFiles on NodeFiles.FileID=Files.FileID\
                    left join FileExtensions on Files.ExtensionID=FileExtensions.ExtensionID\
                    left join Ratings on Ratings.FileID=Files.FileID\
                    where NodeFiles.NodeID=?;")
                query.bindValue(0, self.UserID)
            query.bindValue(1, self.folder)
            query.bindValue(2, self.folder)
        else:
            if self.sharedOnly:
                query = QtSql.QSqlQuery("select 1 as Type, NodeID as ID, NodeName as Name\
                    from Nodes left join Edges on Nodes.NodeID=Edges.ChildID\
                    where Nodes.UserID=? and Edges.ParentID is NULL and IsShared=1;")
                query.bindValue(0, self.Other)
            else:
                query = QtSql.QSqlQuery("select 1 as Type, NodeID as ID, NodeName as Name\
                    from Nodes left join Edges on Nodes.NodeID=Edges.ChildID\
                    where Nodes.UserID=? and Edges.ParentID is NULL\
                    \
                    union\
                    \
                    select 0 as Type, UserID as ID, LoginWord as Name\
                    from Users\
                    where UserID in (select userID from nodes where IsShared=1 group by UserID having count(*)>0) and\
                    UserID<>?;")
                query.bindValue(0, self.UserID)
                query.bindValue(1, self.UserID)
        
        query.exec_()
        return query
    
    def createComment(self):
        query = QtSql.QSqlQuery("INSERT INTO Comments(UserID, FileID, CommentText)\
                                VALUES (?, ?, ?);")
        query.bindValue(0, self.UserID)
        query.bindValue(1, self.FileID)
        query.bindValue(2, self.myComment.text())
        if query.exec_():
            self.myComment.setText("")
            self.CommentsModel.setQuery(self.commentQuery())
    
    def commentQuery(self):
        query = QtSql.QSqlQuery("select Comments.commentID, Users.LoginWord, Comments.CommentText\
                                from Comments\
                                left join Users on Comments.UserID=Users.UserID\
                                where Comments.FileID=?;")
                                
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
        if self.model.record(index.row()).value(0).toInt()[0]==0:
            self.otherView = FolderView(self, self.UserID, True, self.model.record(index.row()).value(1).toInt()[0])
            self.otherView.open()
            if self.otherView.copy is not None:
                self.copy = self.otherView.copy
        elif self.model.record(index.row()).value(0).toInt()[0]==1:
            self.folder = self.model.record(index.row()).value(1).toInt()[0]
            folder = QtGui.QListWidgetItem(self.model.record(index.row()).value(2).toString()+" >")
            folder.setData(DBFolderIDRole,self.folder)
            self.history.addItem(folder)
            self.history.setCurrentItem(self.history.item(self.history.count()-1))
            self.model.setQuery(self.execQuery())
        else:
            self.FileID = self.model.record(index.row()).value(1).toInt()[0]
            self.FileName.setText("File: " + self.model.record(index.row()).value(2).toString())
            self.Rating.setText("Rating: " + self.ratingStr(self.model.record(index.row()).value(4).toInt()[0]))
            self.Shared.setText("Shared: " + str(self.model.record(index.row()).value(5).toInt()[0]>0))
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
        self.fileAddMenu.popup(self.pos() + point)
    
    def folderAdd(self):
        self.FP = FolderProperties(self, self.folder, self.UserID)
        self.FP.open()
    
    def fileAdd(self):
        self.FP = FileProperties(self, self.folder)
        self.FP.open()
        
    def objCopy(self):
        self.copy = obj
        self.copy.Type = self.model.record(self.View.selectedIndexes()[0].row()).value(0).toInt()[0]
        self.copy.ID = self.model.record(self.View.selectedIndexes()[0].row()).value(1).toInt()[0]
    
    def objPaste(self):
        if self.copy!=None:
            if self.copy.Type == 1:
                query = QtSql.QSqlQuery("INSERT INTO Edges(ChildID, ParentID, UserID)\
                                        VALUES (?, ?, ?);")
                query.bindValue(0, self.copy.ID)
                query.bindValue(1, self.folder)
                query.bindValue(2, self.UserID)
                query.exec_()
            else:
                query = QtSql.QSqlQuery("INSERT INTO NodeFiles(NodeID, FileID)\
                                        VALUES (?, ?);")
                query.bindValue(0, self.folder)
                query.bindValue(1, self.copy.ID)
                query.exec_()
        
        self.model.setQuery(self.execQuery())