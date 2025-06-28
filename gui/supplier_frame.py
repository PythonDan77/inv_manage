import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from tkinter import messagebox

# When first run, verify the table exists in the MYSQL db
def ensure_table_exists():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS supplier_list (
                   id INT PRIMARY KEY AUTO_INCREMENT, 
                   name VARCHAR(40), 
                   contact VARCHAR(20),
                   phone_number VARCHAR(20), 
                   email VARCHAR(30),
                   country VARCHAR(20),
                   address VARCHAR(50)   
                   )"""
        )

ensure_table_exists()

# Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM supplier_list')
        all_records = cur.fetchall()
        sup_treeview.delete(*sup_treeview.get_children())
        for record in all_records:
            sup_treeview.insert('', 'end', values=record)

# Function used to verify all data in fields is present and of the right type.
def validate_form_inputs(name, contact, phone, email, country, address):
    
    if not name:
        messagebox.showerror('Empty Field', 'Company cannot be empty.')
        return None
    
    if not country:
        messagebox.showerror('Empty Field', 'Country cannot be empty.')
        return None
    address = address.replace("\n", " ")
    return (name.strip(),
            contact.strip(),
            phone.strip(),
            email.strip(),
            country.strip(),
            address.strip()  
        )

# Check to make sure a row is selected to either update or delete.
def row_select_check(name, contact, phone, email, country, address, update=False, delete=False):
    
    selected = sup_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return
    # Get the currently selected ID of the row.
    data = sup_treeview.item(selected)
    id_num = data['values'][0]

    if update:
        add_update_item(name, contact, phone, email, country, address, True, id_num)
    elif delete:
        delete_item(name, contact, phone, email, country, address, id_num)


# When all fields are filled and the add button is pressed, this function adds the items to the database.
def add_update_item(name, contact, phone, email, country, address, update=False, cur_id=None):

    validated_data = validate_form_inputs(name, contact, phone, email, country, address)

    if not validated_data:
        return
    else:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                if update:
                    cur.execute('SELECT * FROM supplier_list WHERE id = %s', (cur_id,))
                    current_db_data = cur.fetchone()
                    if not current_db_data:
                        messagebox.showerror("Error", 'The item does not exist.')
                        return
                    current_db_data = current_db_data[1:]
                    
                    if current_db_data == validated_data:
                        messagebox.showinfo('No Changes','No Changes Detected.')
                        return
                    else:
                        cur.execute("""UPDATE supplier_list SET name=%s, 
                                    contact=%s, 
                                    phone_number=%s, 
                                    email=%s, 
                                    country=%s, 
                                    address=%s 
                                    WHERE id=%s""",
                                    
                                    (*validated_data,
                                    cur_id)
                                    )

                        messagebox.showinfo('Success','Update successful.')
                else:

                    cur.execute(
                        """SELECT * FROM supplier_list
                        WHERE name = %s AND country = %s
                        """, (validated_data[0], validated_data[4]))
                    
                    if cur.fetchone():
                        messagebox.showerror("Duplicate Error", 'The item already exists.')
                        return

                    else:
                        cur.execute(
                            """INSERT INTO supplier_list (name, contact, phone_number, email, country, address) VALUES (%s, %s, %s, %s, %s, %s)""",
                            (validated_data[0],
                             validated_data[1],
                             validated_data[2],
                             validated_data[3],
                             validated_data[4],
                             validated_data[5])
                        )
                        messagebox.showinfo('Success','Saved Successfully.')
            conn.commit()
            treeview()
        
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Delete the selected row/item.
def delete_item(name, contact, phone, email, country, address, id_num):

    result = messagebox.askyesno('Confirm', 'Do you want to delete this record?')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute('DELETE FROM supplier_list WHERE id=%s',(id_num,))
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
            clear_fields((name, contact, phone, email, country, address))
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Clears data from all fields. Highlighted row is also cleared when the CLEAR button is pressed, but not when called from select_data().
def clear_fields(all_fields, tab=False):

    for field in all_fields:
        field.delete(0,tk.END)

    if tab:
        sup_treeview.selection_remove(sup_treeview.selection())

def select_data(event, all_fields):

    index = sup_treeview.selection()
    content_dict = sup_treeview.item(index)
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
            if search_option == 'Company':
                search_option = 'name'
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(f'SELECT * FROM supplier_list WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                sup_treeview.delete(*sup_treeview.get_children())
                for record in result:
                    sup_treeview.insert('', 'end', values=record)

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

def supplier_frame(parent):
    global sup_treeview

    # Main Frame Code
    supplier_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    supplier_frame.place(x=201, y=100)

    heading_label = tk.Label(supplier_frame, text='Supplier Detail', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_img_supplier = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(supplier_frame, image=back_img_supplier, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:supplier_frame.place_forget())
    back_button.image = back_img_supplier
    back_button.place(x=5, y=33)

    #Left Frame Code
    left_frame = tk.Frame(supplier_frame, width=525, height=600, bg='white')
    left_frame.place(x=0, y=75)
    left_frame.grid_propagate(False)

    name_label = tk.Label(left_frame, text="Company Name",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    name_label.grid(row=0, column=0, padx=(20,0), pady=(60,0))
    name_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    name_entry.grid(row=0, column=1, padx=(15,0), pady=(60,0))

    contact_label = tk.Label(left_frame, text="Contact Name",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    contact_label.grid(row=1, column=0, padx=(20,0), pady=(20,0))
    contact_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    contact_entry.grid(row=1, column=1, padx=(15,0), pady=(20,0))

    phone_label = tk.Label(left_frame, text="Phone",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    phone_label.grid(row=2, column=0, padx=(20,0), pady=(20,0))
    phone_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    phone_entry.grid(row=2, column=1, padx=(15,0), pady=(20,0))

    email_label = tk.Label(left_frame, text="Email",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    email_label.grid(row=3, column=0, padx=(20,0), pady=(20,0))
    email_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    email_entry.grid(row=3, column=1, padx=(15,0), pady=(20,0))

    country_label = tk.Label(left_frame, text="Country",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    country_label.grid(row=4, column=0, padx=(20,0), pady=(20,0))
    country_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    country_entry.grid(row=4, column=1, padx=(15,0), pady=(20,0))
    
    address_label = tk.Label(left_frame, text="Address",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    address_label.grid(row=5, column=0, padx=(20,0), pady=(20,0), sticky='nw')
    # address_text = tk.Text(left_frame, width=31, height=6, bg='lightyellow', bd=2)
    address_text = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    address_text.grid(row=5, column=1, padx=(15,0), pady=(20,0))

    button_frame = tk.Frame(left_frame, width=537, height= 200, bg='white')
    button_frame.place(x=0, y=450, relwidth=1)

    add_button = tk.Button(button_frame, text='Add', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: add_update_item(name_entry.get(), 
                                                                  contact_entry.get(), 
                                                                  phone_entry.get(), 
                                                                  email_entry.get(), 
                                                                  country_entry.get(), 
                                                                  address_text.get()
                                                                  )
                                                                  )
    add_button.grid(row=0, column=0, padx=(20,0), pady=20)

    update_button = tk.Button(button_frame, text='Update', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: row_select_check(name_entry.get(), 
                                                                  contact_entry.get(), 
                                                                  phone_entry.get(), 
                                                                  email_entry.get(), 
                                                                  country_entry.get(), 
                                                                  address_text.get(),
                                                                  update=True)
                                        )
    update_button.grid(row=0, column=1, padx=(20,0), pady=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: row_select_check(
                                                                name_entry, 
                                                                contact_entry, 
                                                                phone_entry, 
                                                                email_entry, 
                                                                country_entry, 
                                                                address_text,
                                                                delete=True)
                                        )
    delete_button.grid(row=0, column=2, padx=(20,0), pady=20)

    clear_button = tk.Button(button_frame, text='Clear', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: clear_fields((
                                                                name_entry, 
                                                                contact_entry, 
                                                                phone_entry, 
                                                                email_entry, 
                                                                country_entry, 
                                                                address_text),
                                                                True)
                                        )
    clear_button.grid(row=0, column=3, padx=(20,0), pady=20)


    #Right frame code
    right_frame = tk.Frame(supplier_frame, width=525, height= 600, bg='white')
    right_frame.place(x=537, y=75, width=560)
    right_frame.grid_propagate(False)

    #Search Frame
    search_frame = tk.Frame(right_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, width=8, values=('ID', 'Company', 'Contact', 'Country'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    search_combobox.set('Select..')
    search_combobox.grid(row=0, column=0, padx=(0,10))

    #Entry Field
    search_entry = tk.Entry(search_frame, font=('times new roman', 12), bg='lightyellow', width=18)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text='Search', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width=7, 
                                            cursor='hand2',
                                            command= lambda: search_item(search_combobox.get(),search_entry.get())
                                            )
    search_button.grid(row=0, column=2, padx=(12,12))

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width=7, 
                                          cursor='hand2',
                                          command= lambda: search_all(search_entry, search_combobox)
                                            )
                                          
    show_button.grid(row=0, column=3)
    
    horizontal_scrollbar = tk.Scrollbar(right_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(right_frame, orient='vertical')

    sup_treeview = ttk.Treeview(right_frame,columns=('id', 'name', 'contact', 'phone_number', 'email', 'country', 'address'), 
                                            show='headings', 
                                            yscrollcommand=vertical_scrollbar.set,
                                            xscrollcommand=horizontal_scrollbar.set, height=20)

    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(50, 0))
    horizontal_scrollbar.config(command=sup_treeview.xview)
    vertical_scrollbar.config(command=sup_treeview.yview)
    sup_treeview.pack(pady= (30, 0))

    sup_treeview.heading('id', text='ID')
    sup_treeview.heading('name', text='Company')
    sup_treeview.heading('contact', text='Contact')
    sup_treeview.heading('phone_number', text='Phone')
    sup_treeview.heading('email', text='Email')
    sup_treeview.heading('country', text='Country')
    sup_treeview.heading('address', text='Address')
    
    
    sup_treeview.column('id', width=70)
    sup_treeview.column('name', width=175)
    sup_treeview.column('contact', width=150)
    sup_treeview.column('phone_number', width=120)
    sup_treeview.column('email', width=170)
    sup_treeview.column('country', width=140)
    sup_treeview.column('address', width=400)
    

    #call treeview function to display the items.
    treeview()

   # When a field in treeview is clicked, the select_data() function fills the entry fields.
    sup_treeview.bind('<ButtonRelease-1>', lambda event: select_data(
                                                            event,
                                                            (name_entry, 
                                                                contact_entry, 
                                                                phone_entry, 
                                                                email_entry, 
                                                                country_entry, 
                                                                address_text))
                                                            )

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))

    return supplier_frame
                   