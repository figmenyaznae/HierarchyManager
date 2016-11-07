from MySQLdb import Connect
import sys

def Deletion(cursor, id):
    if cursor.execute('select * from files where FileID = {}'.format(id))<1:
        print 'File deleted permanently'
    print 'File occurs in {} folders'.format(cursor.execute('select * from nodefiles where FileID = {}'.format(id)))
    
if __name__ == "__main__":
    db =  Connect(user='root', passwd='pass', db='hierarchymanager')
    cursor = db.cursor()
    if len(sys.argv)==3 and sys.argv[1] == 'd':
        Deletion(cursor, int(sys.argv[2]))