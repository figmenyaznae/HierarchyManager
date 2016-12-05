SELECT = {
    'SharedFolder' : '''
select 1 as Type, NodeID as ID, NodeName as Name,
    NULL as Icon, NULL as Rating, IsShared
from Nodes left join Edges on Nodes.NodeID=Edges.ChildID
where Nodes.UserID=? and Edges.ParentID=? and IsShared=1
        
union
        
select 2 as Type, Files.FileID as ID, Files.Name as Name,
    FileExtensions.Icon as Icon, Ratings.Value as Rating, Files.IsShared
from Files left join NodeFiles on NodeFiles.FileID=Files.FileID
    left join FileExtensions on Files.ExtensionID=FileExtensions.ExtensionID
    left join Ratings on Ratings.FileID=Files.FileID
where NodeFiles.NodeID=? and IsShared=1;
        ''',
    'nonSharedFolder' : '''
select 1 as Type, NodeID as ID, NodeName as Name,
    NULL as Icon, NULL as Rating, IsShared
from Nodes left join Edges on Nodes.NodeID=Edges.ChildID
where Nodes.UserID=? and Edges.ParentID=?

union

select 2 as Type, Files.FileID as ID, Files.Name as Name,
    FileExtensions.Icon as Icon, Ratings.Value as Rating, Files.IsShared
from Files left join NodeFiles on NodeFiles.FileID=Files.FileID
    left join FileExtensions on Files.ExtensionID=FileExtensions.ExtensionID
    left join Ratings on Ratings.FileID=Files.FileID
where NodeFiles.NodeID=?;
        ''',
    'SharedRoot' : '''
select 1 as Type, NodeID as ID, NodeName as Name
from Nodes left join Edges on Nodes.NodeID=Edges.ChildID
where Nodes.UserID=? and Edges.ParentID is NULL and IsShared=1;
        ''',
    'nonSharedRoot' : '''
select 1 as Type, NodeID as ID, NodeName as Name
from Nodes left join Edges on Nodes.NodeID=Edges.ChildID
where Nodes.UserID=? and Edges.ParentID is NULL

union

select 0 as Type, UserID as ID, LoginWord as Name
from Users
where UserID in
    (select userID
     from nodes
     where IsShared=1
     group by UserID
     having count(*)>0) and
    UserID<>?;
        ''',
    'Comments' : '''
select Comments.commentID, Users.LoginWord, Comments.CommentText
from Comments left join Users on Comments.UserID=Users.UserID
where Comments.FileID=?;
        ''',
    'Extensions' : 'select ExtensionID, Extension from FileExtensions;',
    'FileBindings' : 'select * from nodefiles where FileID=?',
    'Users' : 'SELECT UserId from users where LoginWord=? and PassPhrase=?',
}

INSERT = {
    'Comment' : 'INSERT INTO Comments(UserID, FileID, CommentText) VALUES (?, ?, ?);',
    'PasteFolder' : 'INSERT INTO Edges(ChildID, ParentID, UserID) VALUES (?, ?, ?);',
    'PasteFile' : 'INSERT INTO NodeFiles(NodeID, FileID) VALUES (?, ?);',
    'File' : 'INSERT INTO Files(Name, ExtensionID, FilePath, IsShared) VALUES (?, ?, ?, ?);',
    'Folder' : 'INSERT INTO Nodes(NodeName, UserID, IsShared) VALUES (?, ?, ?);',
    'User' : 'INSERT INTO Users(LoginWord, PassPhrase, FirstName, LastName, RootNodeID) VALUES (?, ?, ?, ?, NULL);',
}

DELETE = {
    'FileFromFolder' : 'delete from nodefiles where FileID=? and NodeID=?;',
    'FileCompletely' : 'delete from files where FileID=?;'
}