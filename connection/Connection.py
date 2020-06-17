import MySQLdb

class Connection:

    def __init__(self, conf, dbname=None):
        try:
            if dbname is None:
                self.connection = MySQLdb.connect(host=conf['host'], user=conf['user'], passwd=conf['password'], db=conf['dbName'], connect_timeout=10)
            else:
                self.connection = MySQLdb.connect(host=conf['host'], user=conf['user'], passwd=conf['password'], db=dbname, connect_timeout=10)
            self.cursor = self.connection.cursor()
        except:
            self.connection = False

    def getAllTables(self):
        self.cursor.execute("SHOW TABLES")
        return self.cursor.fetchall()

    def getColumnsByTable(self, table):
        self.cursor.execute("SHOW columns FROM " + table)
        return self.cursor.fetchall()

    def getCreateTableSyntax(self, table):
        self.cursor.execute("SHOW CREATE TABLE " + table)
        syntax = self.cursor.fetchall()
        return syntax[0][1]