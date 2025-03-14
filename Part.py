import sqlite3

DB = 'db'
UI = 'UI'

class Part:

    def __init__(self):
        self.id: int = None
        self.component: str = None  
        self.nome: str = None
        self.prezzo: float = None
        self.scontato: bool = None
        self.data_prezzo: str = None
        self.link: str = None
        pass

    def __init__(self, t: tuple, fromWho: str = None):
        self.component = t[1]
        self.nome = t[2]
        self.data_prezzo = t[5]
        self.link = t[6]
        if fromWho == DB:
            self.id = t[0]
            self.prezzo = t[3]
            self.scontato = t[4] == 1
        if fromWho == UI:
            self.id = int(t[0])
            self.prezzo = 0 if t[3] == '' or t[3] is None else float(str(t[3]).replace(",", "."))
            self.scontato = t[4] == 'Si'
        pass
    
    def get_headers():
        return ("ID","Componente","Nome","Prezzo","Scontato","Data Prezzo","Link")
    
    def get_components_names():
        return ("Case","Processore","Scheda Madre","RAM","SSD","Alimentatore","Dissipatore")

    def __list__(self):
        return list([self.id, self.component, self.nome, self.prezzo, self.scontato, self.data_prezzo, self.link])
    
    def get_values_for_UI(self):
        return list([self.id, self.component, self.nome, str(self.prezzo).replace(".", ",").replace(",0", ""), 'Si' if self.scontato else 'No', self.data_prezzo, self.link])
    
    def insert_data(self, conn: sqlite3.Connection):
        sql = ''' INSERT INTO parts(id,component,nome,prezzo,scontato,data_prezzo,link)
            VALUES(?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, self.__list__())
        conn.commit()

    def update_data(self, conn: sqlite3.Connection):
        sql = ''' UPDATE parts
                SET component = ?,
                    nome = ?,
                    prezzo = ?,
                    scontato = ?,
                    data_prezzo = ?,
                    link = ?
                WHERE id = ? '''
        cur = conn.cursor()
        cur.execute(sql, self.__list__())
        conn.commit()

    def delete_data(self, conn: sqlite3.Connection):
        sql = 'DELETE FROM parts WHERE id = ?'
        cur = conn.cursor()
        cur.execute(sql, [self.id])
        conn.commit()

    def select_all_parts(conn: sqlite3.Connection):
        cur = conn.cursor()
        cur.execute("SELECT * FROM parts")
        rows = cur.fetchall()
        return list(map(lambda row: Part(row, DB), rows))