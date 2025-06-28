import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

# When first run, verify the table exists in the MYSQL db
def ensure_table_exists():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS inventory_items (
                   id INT PRIMARY KEY AUTO_INCREMENT, 
                   part_name VARCHAR(40), 
                   part_number VARCHAR(40), 
                   quantity INT, 
                   location VARCHAR(30), 
                   supplier VARCHAR(30), 
                   supplier_contact VARCHAR(30), 
                   low_limit INT, 
                   last_receive_date VARCHAR(20),
                   last_receive_qty VARCHAR(15)   
                   )"""
        )

ensure_table_exists()

# Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM inventory_items')
        all_records = cur.fetchall()
        inv_treeview.delete(*inv_treeview.get_children())
        for record in all_records:
            inv_treeview.insert('', 'end', values=record)

# Function used to verify all data in fields is present and of the right type.
def validate_form_inputs(part_name, part_number, qty, location, supplier, sup_contact, low_limit):
    
    if not part_name:
        messagebox.showerror('Empty Field', 'Part Name cannot be empty.')
        return None
    
    if not part_number:
        messagebox.showerror('Empty Field', 'Part Number cannot be empty.')
        return None
    
    if not qty:
        messagebox.showerror('Empty Field', 'Quantity cannot be empty.')
        return None
    try:
        qty = int(qty)
    except ValueError:
        messagebox.showerror("Validation Error", "Quantity must be a number.")
        return None

    if not location:
        messagebox.showerror('Empty Field', 'Location cannot be empty.')
        return None

    if not supplier:
        messagebox.showerror('Empty Field', 'Supplier cannot be empty.')
        return None
    
    if not sup_contact:
        messagebox.showerror('Empty Field', 'Supplier Contact cannot be empty.')
        return None

    if not low_limit:
        messagebox.showerror('Empty Field', 'Low Limit cannot be empty.')
        return None
    try:
        low_limit = int(low_limit)
    except ValueError:
        messagebox.showerror("Validation Error", "Low Limit must be a number.")
        return None

    return (part_name.strip(),
            part_number.strip(),
            int(qty),
            location.strip(),
            supplier.strip(),
            sup_contact.strip(),
            int(low_limit)
        )

# Check to make sure a row is selected to either update or delete.
def row_select_check(part_name, part_number, qty, location, supplier, sup_contact, low_limit, update=False, delete=False):
    
    selected = inv_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = inv_treeview.item(selected)
    id_num = data['values'][0]

    if update:
        add_update_item(part_name, part_number, qty, location, supplier, sup_contact, low_limit, True, id_num)
    elif delete:
        delete_item(part_name, part_number, qty, location, supplier, sup_contact, low_limit, id_num)


# When all fields are filled and the add button is pressed, this function adds the items to the database.
def add_update_item(part_name, part_number, qty, location, supplier, sup_contact, low_limit, update=False, cur_id=None):

    validated_data = validate_form_inputs(part_name, part_number, qty, location, supplier, sup_contact, low_limit)

    if not validated_data:
        return
    else:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                if update:
                    cur.execute('SELECT * FROM inventory_items WHERE id = %s', (cur_id,))
                    current_db_data = cur.fetchone()
                    if not current_db_data:
                        messagebox.showerror("Error", 'The item does not exist.')
                        return
                    current_db_data = current_db_data[1:-2]
                    
                    if current_db_data == validated_data:
                        messagebox.showinfo('No Changes','No Changes Detected.')
                        return
                    else:
                        cur.execute("""UPDATE inventory_items SET part_name=%s, 
                                    part_number=%s, 
                                    quantity=%s, 
                                    location=%s, 
                                    supplier=%s, 
                                    supplier_contact=%s, 
                                    low_limit=%s WHERE id=%s""",
                                    
                                    (*validated_data,
                                    cur_id)
                                    )

                        messagebox.showinfo('Success','Update successful.')
                else:

                    cur.execute(
                        """SELECT * FROM inventory_items
                        WHERE part_number = %s AND supplier = %s
                        """, (validated_data[1], validated_data[4]))
                    
                    if cur.fetchone():
                        messagebox.showerror("Duplicate Error", 'The item already exists.')
                        return

                    else:
                        set_date = "New"
                        received_qty = 0

                        if validated_data[2] > 0:
                            set_date = datetime.today().strftime('%Y-%m-%d')
                            received_qty = validated_data[2]

                        cur.execute(
                            """INSERT INTO inventory_items (part_name, part_number, quantity, location,
                            supplier, supplier_contact, low_limit,
                            last_receive_date, last_receive_qty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                            *validated_data,
                            set_date,
                            received_qty)
                        )
                        messagebox.showinfo('Success','Saved Successfully.')
            conn.commit()
            treeview()
        
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Delete the selected row/item.
def delete_item(part_name, part_number, qty, location, supplier, sup_contact, low_limit, id_num):

    result = messagebox.askyesno('Confirm', 'Do you want to delete this record?')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute('DELETE FROM inventory_items WHERE id=%s',(id_num,))
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
            clear_fields((part_name, part_number, qty, location, supplier, sup_contact, low_limit))
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


# Clears data from all fields. Highlighted row is also cleared when the CLEAR button is pressed, but not when called from select_data().
def clear_fields(all_fields, tab=False):

    for field in all_fields:
        field.delete(0,tk.END)

    if tab:
        inv_treeview.selection_remove(inv_treeview.selection())

# When a field in treeview is selected, this function collects the data and applies it to all entry fields (all_fields).
def select_data(event, all_fields):

    index = inv_treeview.selection()
    content_dict = inv_treeview.item(index)
    row_data = content_dict['values']

    clear_fields(all_fields)
    
    for i, field in enumerate(all_fields, start=1):
        field.insert(0, row_data[i])

# Function verifies data has been used to search the database and then retrieves the data.
def search_item(search_option, value):
    if search_option == 'Select..':
        messagebox.showerror('Error','Select an option.')
    elif not value:
        messagebox.showerror('Error','Enter a value to search.')
    else:
        try:
            search_option = search_option.replace(' ', '_')
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(f'SELECT * FROM inventory_items WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                inv_treeview.delete(*inv_treeview.get_children())
                for record in result:
                    inv_treeview.insert('', 'end', values=record)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Reloads all data and resets the search options.
def search_all(search_entry, search_combobox):
    treeview()
    search_entry.delete(0,'end')
    search_combobox.set('Select...')

# Clear the highlight from the combobox. Trigger in the main function at the bottom.
def on_select(event, combobox):
    combobox.selection_clear()

def inventory_frame(parent):
    global inv_treeview

    inv_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    inv_frame.place(x=201, y=100)

    heading_label = tk.Label(inv_frame, text='Inventory Detail', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(inv_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:inv_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)
    
    #Top Section of Page
    top_frame = tk.Frame(inv_frame, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Part name', 'Part number', 'Location', 'Supplier'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    search_combobox.set('Select..')
    search_combobox.grid(row=0, column=0, padx=20)

    #Entry Field
    search_entry = tk.Entry(search_frame, font=('times new roman', 12), bg='lightyellow')
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text='Search', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command= lambda: search_item(search_combobox.get(),search_entry.get()))
    search_button.grid(row=0, column=2, padx=20)

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 10, 
                                          cursor='hand2',
                                          command= lambda: search_all(search_entry, search_combobox))
    show_button.grid(row=0, column=3)

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    inv_treeview = ttk.Treeview(top_frame, columns=('id', 'part_name', 'part_number', 'quantity', 'location','supplier', 'supplier_contact', 'low_limit  ', 'last_receive_date', 'last_receive_qty'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=inv_treeview.xview)
    vertical_scrollbar.config(command=inv_treeview.yview)
    inv_treeview.pack(pady= (10, 0))
    
    inv_treeview.heading('id', text='ID')
    inv_treeview.heading('part_name', text='Part Name')
    inv_treeview.heading('part_number', text='Part Number')
    inv_treeview.heading('quantity', text='QTY')
    inv_treeview.heading('location', text='Location')
    inv_treeview.heading('supplier', text='Supplier')
    inv_treeview.heading('supplier_contact', text='Supplier Contact')
    inv_treeview.heading('low_limit  ', text='Low')
    inv_treeview.heading('last_receive_date', text='LRD')
    inv_treeview.heading('last_receive_qty', text='LRQ')
    
    inv_treeview.column('id', width=70)
    inv_treeview.column('part_name', width=175)
    inv_treeview.column('part_number', width=150)
    inv_treeview.column('quantity', width=70)
    inv_treeview.column('location', width=100)
    inv_treeview.column('supplier', width=150)
    inv_treeview.column('supplier_contact', width=200)
    inv_treeview.column('low_limit  ', width=70)
    inv_treeview.column('last_receive_date', width=100)
    inv_treeview.column('last_receive_qty', width=70)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(inv_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    part_name_label = tk.Label(detail_frame, text='Part Name', font=('times new roman', 10, 'bold'), bg='white')
    part_name_label.grid(row=0, column=0,padx=10, pady=20)
    part_name_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    part_name_entry.grid(row=0, column=1, padx=10, pady=20 )

    part_num_label = tk.Label(detail_frame, text='Part Number', font=('times new roman', 10, 'bold'), bg='white')
    part_num_label.grid(row=0, column=2, padx=10, pady=20)
    part_num_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    part_num_entry.grid(row=0, column=3, padx=10, pady=20)

    qty_label = tk.Label(detail_frame, text='Quantity', font=('times new roman', 10, 'bold'), bg='white')
    qty_label.grid(row=0, column=4, padx=10, pady=20)
    qty_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    qty_entry.grid(row=0, column=5, padx=10, pady=20)

    loc_label = tk.Label(detail_frame, text='Location', font=('times new roman', 10, 'bold'), bg='white')
    loc_label.grid(row=1, column=0, padx=10, pady=10)
    loc_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    loc_entry.grid(row=1, column=1, padx=10, pady=10)

    sup_label = tk.Label(detail_frame, text='Supplier', font=('times new roman', 10, 'bold'), bg='white')
    sup_label.grid(row=1, column=2, padx=10, pady=10)
    sup_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    sup_entry.grid(row=1, column=3, padx=10, pady=10)

    sup_contact_label = tk.Label(detail_frame, text='Supplier Contact', font=('times new roman', 10, 'bold'), bg='white')
    sup_contact_label.grid(row=1, column=4, padx=10, pady=10)
    sup_contact_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    sup_contact_entry.grid(row=1, column=5, padx=10, pady=10)

    low_label = tk.Label(detail_frame, text='Low Level', font=('times new roman', 10, 'bold'), bg='white')
    low_label.grid(row=2, column=0, padx=10, pady=20)
    low_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    low_entry.grid(row=2, column=1, padx=10, pady=20)

    #Lower button Frame
    button_frame= tk.Frame(inv_frame, bg='white')
    button_frame.place(x=180, y=550, relwidth=1)

    add_button = tk.Button(button_frame, text='Add', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: add_update_item(part_name_entry.get(), 
                                                                  part_num_entry.get(), 
                                                                  qty_entry.get(), 
                                                                  loc_entry.get(), 
                                                                  sup_entry.get(), 
                                                                  sup_contact_entry.get(), 
                                                                  low_entry.get())
                                                                  )
    add_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(part_name_entry.get(), 
                                                                  part_num_entry.get(), 
                                                                  qty_entry.get(), 
                                                                  loc_entry.get(), 
                                                                  sup_entry.get(), 
                                                                  sup_contact_entry.get(), 
                                                                  low_entry.get(),
                                                                  update=True)
                                                                  )
    update_button.grid(row=0, column=1, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(
                                                                part_name_entry, 
                                                                part_num_entry, 
                                                                qty_entry, 
                                                                loc_entry, 
                                                                sup_entry, 
                                                                sup_contact_entry, 
                                                                low_entry,
                                                                delete=True)
                                                                )
    delete_button.grid(row=0, column=2, padx=20)
    
    # Clicking the clear button triggers the clear_fields() function and removes all data from the entry fields.
    clear_button = tk.Button(button_frame, text='Clear', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: clear_fields((
                                                                  part_name_entry, 
                                                                  part_num_entry, 
                                                                  qty_entry, 
                                                                  loc_entry, 
                                                                  sup_entry, 
                                                                  sup_contact_entry, 
                                                                  low_entry,
                                                                  ), True)
                                                                  )
    clear_button.grid(row=0, column=3, padx=20)

    # When a field in treeview is clicked, the select_data() function fills the entry fields.
    inv_treeview.bind('<ButtonRelease-1>', lambda event: select_data(
                                                            event,
                                                            (part_name_entry, 
                                                            part_num_entry, 
                                                            qty_entry, 
                                                            loc_entry, 
                                                            sup_entry, 
                                                            sup_contact_entry, 
                                                            low_entry))
                                                            )

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))

    return inv_frame
