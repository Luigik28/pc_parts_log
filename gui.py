import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from database import Database
import Part as p
from Part import Part

class Gui:
    def __init__(self) -> None:
        self.allData: list[Part] = []
        self.db: Database = Database("parts.db")
        self.root: tk.Tk = tk.Tk()
        self.root.title("PC Parts Log")
        self.root.state("zoomed")
        self.initialize()

    def sort_column(self, tree: ttk.Treeview, col: str, reverse: bool):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))
    
    
    def get_first_empty_id(self):
        dataSorted = sorted(self.allData, key=lambda x: x.id)
        for i in range(len(dataSorted)):
            if dataSorted[i].id != i:
                return i
        return len(dataSorted)

    def show_popup(self, event, labels, tree: ttk.Treeview, data: Part=None):
        popup = tk.Toplevel()
        if event == "new_row":
            popup.title("Aggiungi Nuova Riga")
        else:
            popup.title("Modifica Riga")

                # Imposta le dimensioni della finestra popup
        popup_width = 800
        popup_height = 300

        # Calcola la posizione per centrare la finestra popup
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        position_x = (screen_width // 2) - (popup_width // 2)
        position_y = (screen_height // 2) - (popup_height // 2)

        # Imposta la geometria della finestra popup
        popup.geometry(f"{popup_width}x{popup_height}+{position_x}+{position_y}")

        # Rendi il popup modale
        popup.grab_set()

        entries = []        
        values = data.get_values_for_UI() if data is not None else None

        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=10, pady=5)
            entry = None
            if label == "ID":
                entry = ttk.Entry(popup)
                if data is None:
                    entry.insert(0, self.get_first_empty_id())
                else:
                    entry.insert(0, values[i])
                entry.config(state="readonly")
            elif label == "Componente":
                entry = ttk.Combobox(popup, values=Part.get_components_names())
                if data is not None:
                    entry.set(values[i])
                entry.bind("<Button-1>", lambda event: entry.event_generate("<Down>"))
                entry.config(state="readonly")
            elif label == "Scontato":
                var = tk.BooleanVar()
                if data is not None:
                    var.set(data.scontato)
                else:
                    var.set(False)
                entry = ttk.Checkbutton(popup, variable=var, onvalue=True, offvalue=False)
                entry.state(['!alternate'])
                entry.state(['!selected'])
                if data is not None and data.scontato:
                    entry.state(['selected']) 
                entry.var = var
            elif label == "Data Prezzo":
                entry = DateEntry(popup, date_pattern='dd-mm-yyyy')
                if data is not None:
                    entry.set_date(values[i])
            else:
                entry = ttk.Entry(popup)
                entry.insert(0, values[i] if data is not None else "")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries.append(entry)
        
        popup.grid_columnconfigure(1, weight=1)
        save_button = tk.Button(popup, text="Salva", command=lambda _entries=entries,_event=event, _popup=popup, _tree=tree:self.save_row(_entries, _event, _popup, _tree))
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def get_value(self, _entry:ttk.Entry):
        if isinstance(_entry, ttk.Combobox) or isinstance(_entry, ttk.Entry):
            return _entry.get()
        elif isinstance(_entry, ttk.Checkbutton):
            return 'Si' if _entry.var.get() else 'No'
        elif isinstance(_entry, DateEntry):
            return _entry.get_date().strftime('%Y-%m-%d') 
        return None

    def save_row(self, _entries: list[ttk.Entry], event: str, popup: tk.Toplevel, tree: ttk.Treeview):
        row = Part(list(self.get_value(entry) for entry in _entries), p.UI)
        if event == "new_row":
            row.insert_data(self.db.conn)
            self.allData.append(row)
            tree.insert("", tk.END, values=row.get_values_for_UI())
        else:
            row.update_data(self.db.conn)# Aggiorna i dati nel database
            for i in range(len(self.allData)):
                if self.allData[i].id == row.id:
                    self.allData[i] = row
                    break
            selected_item = tree.selection()[0]
            tree.item(selected_item, values=row.get_values_for_UI())
        popup.destroy()

    def create_table(self, tab: ttk.Frame, headers: list[str], data: list[Part]):
        tree = ttk.Treeview(tab, columns=headers, show="headings")

        for header in headers:
            tree.heading(header, text=header, anchor=tk.W, command=lambda _col=header: self.sort_column(tree, _col, False))
            if header == "ID":
                tree.column(header, width=50)
        
        for row in data:
            tree.insert("", tk.END, values=row.get_values_for_UI())

        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Creazione di un frame per contenere i bottoni
        button_frame = tk.Frame(tab)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        # Creazione del bottone per aggiungere una riga
        add_button = tk.Button(button_frame, text="Aggiungi Riga", command=lambda _headers=headers, _tree=tree: self.add_row(_headers, _tree))
        add_button.pack(side=tk.LEFT, padx=5)

        # Creazione del bottone per eliminare una riga
        delete_button = tk.Button(button_frame, text="Elimina Riga", command=lambda _tree=tree: self.delete_row(_tree))
        delete_button.pack(side=tk.LEFT, padx=5)

        # Creazione del bottone per modificare una riga
        modify_button = tk.Button(button_frame, text="Modifica Riga", command=lambda _headers=headers, _tree=tree: self.modify_row(_headers, _tree))
        modify_button.pack(side=tk.LEFT, padx=5)
    
    def add_row(self, headers: list[str], tree: ttk.Treeview):
        self.show_popup("new_row", headers, tree)

    def delete_row(self, tree: ttk.Treeview):
        selected_item = tree.selection()[0]
        data = tree.item(selected_item)["values"]
        for row in self.allData:
            if row.id == data[0]:
                self.allData.remove(row)
                row.delete_data(self.db.conn)
                break
        tree.delete(selected_item)

    def modify_row(self, headers: list[str], tree: ttk.Treeview):
        selected_item = tree.selection()[0]
        data = tree.item(selected_item)["values"]
        self.show_popup("modify_row", headers, tree, Part(data, p.UI))

    def initialize(self):
        #self.db.drop_table("parts")
        self.db.create_db()

        # Creazione del notebook (contenitore per le tab)
        notebook = ttk.Notebook(self.root)
        notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Creazione della prima tab
        tab_dashboard = ttk.Frame(notebook)
        notebook.add(tab_dashboard, text="Dashboard")

        # Creazione della seconda tab
        tab_storico = ttk.Frame(notebook)
        notebook.add(tab_storico, text="Storico")

        self.allData = Part.select_all_parts(self.db.conn)
        self.create_table(tab_storico,Part.get_headers(),self.allData)