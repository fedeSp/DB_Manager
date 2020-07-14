import sqlite3

from tkinter import ttk
from tkinter import *

class Product:

    db_name = 'database.db'
    tb_name = ''

    def __init__(self, window):
        self.wind = window
        self.wind.title("DB Manager")
        
        # Table Selector
        frame1 = LabelFrame(self.wind, text = 'Select Table')
        frame1.grid(row = 0, column = 0, columnspan = 3, pady = 20)

        Label(frame1, text = 'Table: ').grid(row = 1, column = 0)
        self.table_names = ttk.Combobox(frame1)
        self.table_names.grid(row = 1, column = 1, pady = 10)
        self.table_names["values"] = self.get_dbTableNames(self.db_name)

        # Button Set TbName
        ttk.Button(frame1, text = 'Choose Table', command = self.setDbTable).grid(row = 2, column = 2, sticky = W + E)

        # Create Products Frame
        frame2 = LabelFrame(self.wind, text = 'Register A new product')
        frame2.grid(row = 2, column = 0, columnspan = 3, pady = 20)

        # Name Input
        Label(frame2, text = 'Name: ').grid(row = 1, column = 0)
        self.name = Entry(frame2)
        self.name.focus()
        self.name.grid(row = 1, column = 1)

        # Price Input
        Label(frame2, text = 'Price: ').grid(row = 2, column = 0)
        self.price = Entry(frame2)
        self.price.grid(row = 2, column = 1)

        # Button Add Product
        ttk.Button(frame2, text = "Save Product", command = self.add_product).grid(row = 3, column = 2, sticky = W + E)

        # Output Messages
        self.message = Label(text = '', fg = 'red')
        self.message.grid(row = 4, column = 0, columnspan = 2, sticky = W + E)


    def get_dbTableNames(self, dbName):
        tbNames = []
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        res = self.run_query(query)
        for name in res:
            tbNames.append(name)
        return tbNames
    
    def setDbTable(self):
        self.tb_name = self.table_names.get()
        self.build_table()

    def get_columnNames(self):
        colList = []
        cont = 1
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            query = 'SELECT * FROM {}'.format(self.tb_name)
            cursor = conn.execute(query)
            row = cursor.fetchone()
            self.colNames = row.keys()
            for col in self.colNames:
                if col == "id":
                    continue
                colList.append("#"+str(cont))
                cont = cont + 1
        self.columnTuple = tuple(colList)

    def build_table(self):
        # Traer los nombres de las columnas
        self.get_columnNames()

        cont = 0
        # Table 
        self.tree = ttk.Treeview(height = 10, columns = self.columnTuple)
        self.tree.grid(row = 5, column = 0, columnspan = 2)
        for name in self.colNames:
            self.tree.heading('#'+str(cont), text = name, anchor = CENTER)
            cont = cont + 1
        # Buttons
        ttk.Button(text = 'Delete', command = self.delete_product).grid(row = 6, column = 0, sticky = W + E)
        ttk.Button(text = 'Update', command = self.update_product).grid(row = 6, column = 1, sticky = W + E)
        
        self.get_products()
    def run_query(self, query, params = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            res = cursor.fetchall()
            conn.commit()
        return res

    def get_products(self):
        # Cleaning Table
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        # Quering data
        query = 'SELECT * FROM {} ORDER BY name DESC'.format(self.tb_name)

        db_rows = self.run_query(query)
        for row in db_rows:
           self.tree.insert('', 0, text = row[0], values = row[1:])

    def add_product(self):
        if self.validation():
            query = 'INSERT INTO product VALUES(NULL, ?, ?)'
            params = (self.name.get(), self.price.get())
            self.run_query(query,params)
            self.message['text'] = 'Product {} added Succesfully'.format(self.name.get())
            self.name.delete(0,END)
            self.price.delete(0,END)
        else:
            self.message['text'] = 'Name and Price are '
        
        self.get_products()

    def validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0

    def delete_product(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text']
        except IndexError as e:
            self.message['text'] = 'Please Select a Record'
            return
        self.message['text'] = ''
        name = self.tree.item(self.tree.selection())['values'][0]
        query = "DELETE FROM product WHERE name = ?"
        self.run_query(query, (name, ))
        self.message['text'] = 'Record {} Deleted Succesfully'.format(name)

        self.get_products()

    def update_product(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text']
        except IndexError as e:
            self.message['text'] = 'Please Select a Record'
            return
        name = self.tree.item(self.tree.selection())['values'][0]
        old_price = self.tree.item(self.tree.selection())['values'][1]
        self.editWind = Toplevel()
        self.editWind.title('Edit Product')
        
        # Old Name
        Label(self.editWind, text = 'Old Name : ').grid(row = 0, column = 1)
        Entry(self.editWind, textvariable = StringVar(self.editWind, value = name), state = 'readonly').grid(row = 0, column = 2)

        # New Name
        Label(self.editWind, text = 'New Name : ').grid(row = 1, column = 1)
        new_name = Entry(self.editWind)
        new_name.grid(row = 1, column = 2)

        # Old Price
        Label(self.editWind, text = 'Old Price : ').grid(row = 3, column = 1)
        Entry(self.editWind, textvariable = StringVar(self.editWind, value = old_price), state = 'readonly').grid(row = 3, column = 2)

        # New Price
        Label(self.editWind, text = 'New Price : ').grid(row = 4, column = 1)
        new_price = Entry(self.editWind)
        new_price.grid(row = 4, column = 2)

        Button(self.editWind, text = "Update", command = lambda: self.edit_records(new_name.get(), name, new_price.get(), old_price)).grid(row = 5, column = 0, sticky = W)

    def edit_records(self, new_name, name, new_price, old_price):
        if not new_name:
            new_name = name
        if not new_price:
            new_price = old_price
        
        query = 'UPDATE product SET name = ?, price = ? WHERE name = ? AND price = ?'
        params = (new_name, new_price, name, old_price)
        self.run_query(query,params)
        self.editWind.destroy()
        self.message['text'] = 'Record {} Updated Succesfully'.format(name)
        self.get_products()

if __name__ == '__main__':
   window = Tk()
   application = Product(window)
   window.mainloop()
