import psycopg2
import json
import sys
import psycopg2.extras

def connect_postgres(logger):
    try:
      key = ""
      with open('db/key.json', 'r') as f:
          key = json.load(f)
      conn = psycopg2.connect(
        host=key["host"],
        port= key["port"],
        user=key["user"],
        password=key["password"],
        sslmode="verify-full",
        sslrootcert="db/decoded_crt.txt",
        database="ibmclouddb")
      return conn
    except Exception as inst:
        logger.warning(f'Unable to connect to database \n {type(inst)}, {inst.args}, {inst}')


class Db():
    """
    This class contains code to talk to the the database
    """

    def __init__(self, logger):
        """
        Read key of your database from a file
        connect to db2 database
        """
        self.logger = logger


    def execute(self, sql, value, fetch):
        """
        Execute the sql statement and fetch the results with the results method
        Fetch is a BOOL, if true the statement needs a result
        If false no result is needed so directly execute the statement
        """
        conn = connect_postgres(self.logger)
        if conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute(sql, value)
                if fetch == 1:
                    result = cur.fetchall()
                    return result
                elif fetch == 2:
                    result = cur.fetchall()
                    conn.commit()
                    return result
                else:
                    conn.commit()
            except Exception as inst:
                print(inst)
                self.logger.warning(f'Unable to execute command:, {sql}, {type(inst)}, {inst.args}, {inst}')
            finally:
                cur.close()
                conn.close()


    def execute_from_file(self, filename, fetch):
        """
        Takes a .sql file with sql commands and executes them
        It takes fetch to pass to self.execute
        """
