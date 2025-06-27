import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox
from pymysql.err import IntegrityError

#When first run, verify the table exists in the MYSQL db
def ensure_table_exists():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS inventory_items (
                   id INT PRIMARY KEY AUTO_INCREMENT, 
                   part_name VARCHAR(50), 
                   part_number VARCHAR(40), 
                   quantity INT, 
                   location VARCHAR(40), 
                   supplier VARCHAR(40), 
                   supplier_contact VARCHAR(40), 
                   low_limit INT, 
                   last_receive_date VARCHAR(30),
                   last_receive_qty VARCHAR(15),
                   UNIQUE KEY uniq_part_supplier (part_number, supplier)
                   )"""
        )

ensure_table_exists()

#Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_item()
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

    return {
        "part_name": part_name.strip(),
        "part_number": part_number.strip(),
        "quantity": int(qty),
        "location": location.strip(),
        "supplier": supplier.strip(),
        "supplier_contact": sup_contact.strip(),
        "low_limit": int(low_limit),
    }


def add_item(part_name, part_number, qty, location, supplier, sup_contact, low_limit):

    validated_data = validate_form_inputs(part_name, part_number, qty, location, supplier, sup_contact, low_limit)

    if not validated_data:
        return
    else:
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO inventory_items (part_name, part_number, quantity, location,
                    supplier, supplier_contact, low_limit,
                    last_receive_date, last_receive_qty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                    validated_data["part_name"],
                    validated_data["part_number"],
                    validated_data["quantity"],
                    validated_data["location"],
                    validated_data["supplier"],
                    validated_data["supplier_contact"],
                    validated_data["low_limit"],
                    today,
                    validated_data["quantity"])

                )
            conn.commit()
            messagebox.showinfo('Success','Saved Successfully.')
            treeview()
        except IntegrityError:
            messagebox.showerror(
                "Duplicate Item",
                "This item already exists with that part number and supplier."
        )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
       

# Clears data from all fields when the CLEAR button is pressed.
def clear_fields(all_fields):
    for field in all_fields:
        field.delete(0,tk.END)

def inventory_frame(parent):
    global inv_treeview

    inv_frame = tk.Frame(parent, width=1075, height=650, bg='white')
    inv_frame.place(x=226, y=100)

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
    search_combobox = ttk.Combobox(search_frame, values=('Part Name', 'Part Number', 'Location', 'Supplier'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    search_combobox.set('Select..')
    search_combobox.grid(row=0, column=0, padx=20)

    #Entry Field
    search_entry = tk.Entry(search_frame, font=('times new roman', 12), bg='lightyellow')
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text='Search', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    search_button.grid(row=0, column=2, padx=20)

    show_button = tk.Button(search_frame, text='Show All', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
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
    inv_treeview.heading('quantity', text='Quantity')
    inv_treeview.heading('location', text='Location')
    inv_treeview.heading('supplier', text='Supplier')
    inv_treeview.heading('supplier_contact', text='Supplier Contact')
    inv_treeview.heading('low_limit  ', text='Low Limit')
    inv_treeview.heading('last_receive_date', text='LRD')
    inv_treeview.heading('last_receive_qty', text='LRQ')
    
    inv_treeview.column('id', width=50)
    inv_treeview.column('part_name', width=175)
    inv_treeview.column('part_number', width=120)
    inv_treeview.column('quantity', width=100)
    inv_treeview.column('location', width=100)
    inv_treeview.column('supplier', width=120)
    inv_treeview.column('supplier_contact', width=175)
    inv_treeview.column('low_limit  ', width=100)
    inv_treeview.column('last_receive_date', width=120)
    inv_treeview.column('last_receive_qty', width=70)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(inv_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    part_name_label = tk.Label(detail_frame, text='Part Name', font=('times new roman', 10), bg='white')
    part_name_label.grid(row=0, column=0,padx=10, pady=20)
    part_name_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    part_name_entry.grid(row=0, column=1, padx=10, pady=20 )

    part_num_label = tk.Label(detail_frame, text='Part Number', font=('times new roman', 10), bg='white')
    part_num_label.grid(row=0, column=2, padx=10, pady=20)
    part_num_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    part_num_entry.grid(row=0, column=3, padx=10, pady=20)

    qty_label = tk.Label(detail_frame, text='Quantity', font=('times new roman', 10), bg='white')
    qty_label.grid(row=0, column=4, padx=10, pady=20)
    qty_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    qty_entry.grid(row=0, column=5, padx=10, pady=20)

    loc_label = tk.Label(detail_frame, text='Location', font=('times new roman', 10), bg='white')
    loc_label.grid(row=1, column=0, padx=10, pady=10)
    loc_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    loc_entry.grid(row=1, column=1, padx=10, pady=10)

    sup_label = tk.Label(detail_frame, text='Supplier', font=('times new roman', 10), bg='white')
    sup_label.grid(row=1, column=2, padx=10, pady=10)
    sup_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    sup_entry.grid(row=1, column=3, padx=10, pady=10)

    sup_contact_label = tk.Label(detail_frame, text='Supplier Contact', font=('times new roman', 10), bg='white')
    sup_contact_label.grid(row=1, column=4, padx=10, pady=10)
    sup_contact_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    sup_contact_entry.grid(row=1, column=5, padx=10, pady=10)

    low_label = tk.Label(detail_frame, text='Low Level', font=('times new roman', 10), bg='white')
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
                                         command=lambda: add_item(part_name_entry.get(), 
                                                                  part_num_entry.get(), 
                                                                  qty_entry.get(), 
                                                                  loc_entry.get(), 
                                                                  sup_entry.get(), 
                                                                  sup_contact_entry.get(), 
                                                                  low_entry.get())
                                                                  )
    add_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    update_button.grid(row=0, column=1, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    delete_button.grid(row=0, column=2, padx=20)

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
                                                                  low_entry)))
    clear_button.grid(row=0, column=3, padx=20)


    return inv_frame
