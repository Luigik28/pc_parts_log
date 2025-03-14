import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.create_connection()

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(e)
    
    def create_db(self):
        create_table_sql = """
        --DROP TABLE IF EXISTS parts;
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY,
            component TEXT NOT NULL,
            nome TEXT NOT NULL,
            prezzo FLOAT NOT NULL,
            scontato INTEGER NOT NULL,
            data_prezzo TEXT NOT NULL,
            link TEXT NOT NULL
        );
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except sqlite3.Error as e:
            print(e)