import pyodbc


class MsSqlQuery:

    def __init__(self, driver='', server_ip='172.17.0.2,1433', database_name='',
                 table_name='', id_column='', email_column='', filter_column='',
                 query_column='', sql_login=False, username='', password=''):
        # self.driver = "ODBC Driver 17 for SQL Server"
        self.driver = driver
        self.ip = server_ip
        self.database_name = database_name
        self.table_name = table_name
        self.filter_column = filter_column
        self.query_column = query_column
        self.sql_login = sql_login
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None

    def build_connection(self, trusted=True):
        if trusted:
            self.conn = pyodbc.connect(f"DRIVER={self.driver};SERVER={self.ip};"
                                       f"DATABASE={self.database_name};TRUSTED_CONNECTION=YES;")
        else:
            self.conn = pyodbc.connect(f"DRIVER={self.driver};SERVER={self.ip};"
                                       f"DATABASE={self.database_name};UID={self.username};PWD={self.password}")

    def database_query(self, customer_num):
        curs = self.conn.cursor()
        # query = f"SELECT email FROM Customers WHERE id = {str(customer_num)}"
        query = f"{self.sql_query} {str(customer_num)}"
        curs.execute(query)
        results = curs.fetchone()
        return results[0]


if __name__ == '__main__':
    database = MsSqlQuery(server_ip='172.17.0.2,1433', database_name='TestDB',
                          username='SA', password='ToorPass39')
    database.build_connection(trusted=False)
    print(database.database_query(1175))
