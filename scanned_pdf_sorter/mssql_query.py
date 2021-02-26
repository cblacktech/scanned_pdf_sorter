import pyodbc
import configparser


class MsSqlQuery:

    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        if self.config.has_section('SQL_SERVER'):
            sql_config = self.config['SQL_SERVER']
            self.driver = sql_config.get('driver')
            self.ip = sql_config.get('server_ip')
            self.database_name = sql_config.get('database')
            self.table_name = sql_config.get('table')
            self.filter_column = sql_config.get('id_column')
            self.query_column = sql_config.get('email_column')
            self.sql_login = sql_config.getboolean('sql_login')
            self.username = sql_config.get('SA')
            self.password = sql_config.get('password')
            self.conn = None
            self.cursor = None

    def build_connection(self, trusted=True):
        try:
            if trusted:
                self.conn = pyodbc.connect(f"DRIVER={self.driver};SERVER={self.ip};"
                                           f"DATABASE={self.database_name};TRUSTED_CONNECTION=YES;")
            else:
                self.conn = pyodbc.connect(f"DRIVER={self.driver};SERVER={self.ip};"
                                           f"DATABASE={self.database_name};UID={self.username};PWD={self.password}")
            return True
        except Exception as e:
            self.conn = None
            print(e)
            return False

    def test_connection(self):
        pass

    def database_query(self, customer_num):
        with self.conn.cursor() as curs:
            curs.execute(f"""
                SELECT {self.query_column}
                FROM {self.table_name}
                where {self.filter_column} = {str(customer_num)};
            """)
            results = curs.fetchone()
        return results[0]


if __name__ == '__main__':
    database = MsSqlQuery(config_file='config.ini')
    database.build_connection(trusted=False)
    print(database.database_query(1175))
