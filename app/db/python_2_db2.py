## SOURCE: https://stackoverflow.com/questions/6044326/how-to-connect-python-to-db2
## Documentation:https://www.ibm.com/support/knowledgecenter/SSCJDQ/com.ibm.swg.im.dashdb.python.doc/doc/c0054699.html
from ibm_db import connect
from ibm_db import tables
from ibm_db import exec_immediate, execute
from ibm_db import fetch_assoc, prepare, bind_param

class Db():
    """
    This class contains code to talk to the the database
    """

    def __init__(self, connection_file):
        """
        Read key of your database from a file
        connect to db2 database
        """
        connection_string  = open(connection_file, "r")
        connection = connection_string.read()
        self.connection = connect(connection, '', '')

    def results(self, command):
        """
        Fetch the results, keep doing this untill there are no more results
        """
        ret = []
        result = fetch_assoc(command)
        while result:
            ret.append(result)
            result = fetch_assoc(command)
        return ret

    def execute(self, sql, fetch):
        """
        Execute the sql statement and fetch the results with the results method
        Fetch is a BOOL, if true the statement needs a result
        If false no result is needed so directly execute the statement
        """
        if fetch:
            return self.results(exec_immediate(self.connection, sql))
        else:
            return exec_immediate(self.connection, sql)

    def prepare(self, sql, param, fetch):
        """
        Prepare sql statement before execution.
        Use this whenever user can insert something in the database to avoid
        sql injections
        Fetch is a BOOL, if true the statement needs a result
        If false no result is needed so directly execute the statement
        """
        stmt = prepare(self.connection, sql)
        if fetch:
            execute(stmt, param)
            return self.results(stmt)
        else:
            return execute(stmt, param)

    def execute_from_file(self, filename, fetch):
        """
        Takes a .sql file with sql commands and executes them
        It takes fetch to pass to self.execute
        """
        file_object  = open(filename, "r")
        sql = file_object.read()
        return self.execute(sql, fetch)
