import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

product_dict = {}
# Used to populate the treeview form with items. It is called after treeview is created.
def ped_treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                po.id,
                po.order_id,
                p.product_name,
                o.customer_name,
                o.po_number,
                o.quantity,
                o.status,
                o.notes,
                o.created_at
            FROM 
                pedal_orders po
            JOIN 
                products p ON po.product_id = p.id
            JOIN 
                orders o ON po.order_id = o.id
        """)
        all_records = cur.fetchall()
        pedal_treeview.delete(*pedal_treeview.get_children())
        for record in all_records:
            pedal_treeview.insert('', 'end', values=record)

def sto_treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""SELECT p.product_name, f.finished_quantity
                        FROM finished_pedals f
                        JOIN products p ON f.product_id = p.id""")
        all_records = cur.fetchall()
        stock_treeview.delete(*stock_treeview.get_children())
        for record in all_records:
            stock_treeview.insert('', 'end', values=record)

# Delete the selected row/item.
def delete_item(cur_id):

    result = messagebox.askyesno('Confirm', 'Do you want to delete this order?'
                                 ' The order will need to be re-entered to have it appear here again.')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM pedal_orders WHERE id = %s", (cur_id,))
                
            conn.commit()
            ped_treeview()
            messagebox.showinfo('Success','Deleted Successfully.')

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(user_info, delete=False):
    
    selected = pedal_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = pedal_treeview.item(selected)
    id_num = data['values'][0]
    
    if delete:
        delete_item(id_num)

def add_finished_quantity(status_combobox, qty_entry):
    selected_label = status_combobox.get()
    quantity_str = qty_entry.get()

    if not selected_label:
        messagebox.showerror("Input Error", "Please select a pedal.")
        return

    if not quantity_str.isdigit():
        messagebox.showerror("Input Error", "Please enter a valid quantity.")
        return

    quantity = int(quantity_str)
    product_id = product_dict.get(selected_label)

    if product_id is None:
        messagebox.showerror("Error", "Selected product not found.")
        return

    confirm = messagebox.askyesno("Confirm Quantity", f"Add {quantity} tested/etched and boxed {selected_label}?")
    if not confirm:
        return

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            # Update finished quantity by adding the new amount
            cur.execute("""
                UPDATE finished_pedals
                SET finished_quantity = finished_quantity + %s
                WHERE product_id = %s
            """, (quantity, product_id))
            conn.commit()

        messagebox.showinfo("Success", f"Added {quantity} to finished quantity for {selected_label}.")

        # Optionally reset fields
        qty_entry.delete(0, tk.END)
        status_combobox.set("Select..")
        sto_treeview()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))


def set_finished_quantity(status_combobox, qty_entry):
    selected_label = status_combobox.get()
    quantity_str = qty_entry.get()

    if not selected_label:
        messagebox.showerror("Input Error", "Please select a pedal.")
        return

    if not quantity_str.isdigit():
        messagebox.showerror("Input Error", "Please enter a valid quantity.")
        return

    quantity = int(quantity_str)
    product_id = product_dict.get(selected_label)

    if product_id is None:
        messagebox.showerror("Error", "Selected product not found.")
        return

    # Optional: Confirm before overwriting
    confirm = messagebox.askyesno("Confirm Overwrite", f"Set quantity for {selected_label} to {quantity}?")
    if not confirm:
        return

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            # Overwrite the finished quantity
            cur.execute("""
                UPDATE finished_pedals
                SET finished_quantity = %s
                WHERE product_id = %s
            """, (quantity, product_id))
            conn.commit()

        messagebox.showinfo("Success", f"{selected_label} finished quantity set to {quantity}.")

        # Optionally reset fields
        qty_entry.delete(0, tk.END)
        status_combobox.set("Select..")
        sto_treeview()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Function verifies data has been used to search the database and then retrieves the data.
def search_item(search_option, value):
    if search_option == 'Select..':
        messagebox.showerror('Error', 'Select an option.')
        return
    if not value:
        messagebox.showerror('Error', 'Enter a value to search.')
        return

    # Map user-friendly search options to actual SQL fields
    field_map = {
        'ID': 'po.id',
        'Customer Name': 'o.customer_name',
        'PO Number': 'o.po_number'
    }

    if search_option not in field_map:
        messagebox.showerror('Error', 'Invalid search option.')
        return

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            sql = f"""
                    SELECT 
                    po.id,
                    po.order_id,
                    p.product_name,
                    o.customer_name,
                    o.po_number,
                    o.quantity,
                    o.status,
                    o.notes,
                    o.created_at
                FROM 
                    pedal_orders po
                JOIN 
                    products p ON po.product_id = p.id
                JOIN 
                    orders o ON po.order_id = o.id
                WHERE 
                    {field_map[search_option]} LIKE %s
            """
            search_term = f"%{value}%" if search_option != "ID" else value
            cur.execute(sql, (search_term,))
            result = cur.fetchall()

            pedal_treeview.delete(*pedal_treeview.get_children())
            for record in result:
                pedal_treeview.insert('', 'end', values=record)

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Reloads all data and resets the search options.
def search_all(search_entry, search_combobox):
    ped_treeview()
    search_entry.delete(0,'end')
    search_combobox.set('Select..')

# Clear the highlight from the combobox. Trigger in the main function at the bottom.
def on_select(event, combobox):
    combobox.selection_clear()

def pedal_frame(parent, user_info):
    global pedal_treeview
    global stock_treeview
    

    pedal_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    pedal_frame.place(x=201, y=100)

    heading_label = tk.Label(pedal_frame, text='Pedal Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(pedal_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:pedal_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(pedal_frame, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Customer Name', 'PO Number'), 
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
    
    pedal_treeview = ttk.Treeview(top_frame, columns=('id','order_id', 'product_name', 'customer_name', 'po_number','qty',
                                                        'status', 'notes', 'created_at'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=pedal_treeview.xview)
    vertical_scrollbar.config(command=pedal_treeview.yview)
    pedal_treeview.pack(pady= (10, 0))
    
    pedal_treeview.heading('id', text='ID')
    pedal_treeview.heading('order_id', text='Order ID')
    pedal_treeview.heading('product_name', text='Product Name')
    pedal_treeview.heading('customer_name', text='Customer Name')
    pedal_treeview.heading('po_number', text='P.O. #')
    pedal_treeview.heading('qty', text='QTY')
    pedal_treeview.heading('status', text='Status')
    pedal_treeview.heading('notes', text='Notes')
    pedal_treeview.heading('created_at', text='Order date')
    
    pedal_treeview.column('id', width=80)
    pedal_treeview.column('order_id', width=80)
    pedal_treeview.column('product_name', width=200)
    pedal_treeview.column('customer_name', width=200)
    pedal_treeview.column('po_number', width=150)
    pedal_treeview.column('qty', width=120)
    pedal_treeview.column('status', width=150)
    pedal_treeview.column('notes', width=300)
    pedal_treeview.column('created_at', width=150)

    #Lower Section of Page
    detail_frame = tk.Frame(pedal_frame, width=675, height=300, bg='white')
    detail_frame.place(x=0, y=375)

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id, product_name, product_code FROM products WHERE product_type =%s", ('Pedal'))
            rows = cur.fetchall()
            for row in rows:
                label = f"{row[1]}"  # e.g., "G120 Amp (AMP001)"
                product_dict[label] = row[0]
    except Exception as e:
        messagebox.showerror("DB Error", str(e))

    status_label = tk.Label(detail_frame, text='Product', font=('times new roman', 10, 'bold'), bg='white')
    status_label.grid(row=0, column=0, padx=20, pady=(20,0))
    status_combobox = ttk.Combobox(detail_frame, width=17, values=list(product_dict.keys()),
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    status_combobox.set('Select..')
    status_combobox.grid(row=0, column=1, padx=10, pady=(20,0))

    qty_label = tk.Label(detail_frame, text='Qty Completed', font=('times new roman', 10, 'bold'), bg='white')
    qty_label.grid(row=0, column=2, padx=10, pady=(20,0))
    qty_completed_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    qty_completed_entry.grid(row=0, column=3, padx=10, pady=(20,0))

    button_frame= tk.Frame(pedal_frame, bg='white')
    button_frame.place(x=180, y=550, relwidth=1)
    
        
    add_button = tk.Button(button_frame, text='Add Finished', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: add_finished_quantity(status_combobox, qty_completed_entry)
                                                                  )
    add_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update Qty', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: set_finished_quantity(status_combobox, qty_completed_entry)
                                                                  )

    delete_button = tk.Button(button_frame, text='Delete', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: row_select_check(user_info, delete=True)  
                                        )

    l_right_frame = tk.Frame(pedal_frame, width=300, height=300, bg='white')
    l_right_frame.place(x=700, y=370)

    s_vertical_scrollbar = tk.Scrollbar(l_right_frame, orient='vertical')
    stock_treeview = ttk.Treeview(l_right_frame, columns=('product_name','qty',
                                                        ), 
                                           show='headings',
                                           yscrollcommand=s_vertical_scrollbar.set
                                           )
    s_vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    s_vertical_scrollbar.config(command=stock_treeview.yview)
    stock_treeview.pack(pady= (10, 0))

    stock_treeview.heading('product_name', text='Pedal Name')
    stock_treeview.heading('qty', text='Finished Quantity')

    stock_treeview.column('product_name', width=200)
    stock_treeview.column('qty', width=150)

    #call treeview function to display the items.
    ped_treeview()
    sto_treeview()

    #Disable certain buttons if user permissions are not adequate
    if user_info['role'] in ['manager', 'admin']:
        update_button.grid(row=0, column=1, padx=20)
        delete_button.grid(row=0, column=2, padx=20)
    
    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))
    status_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, status_combobox))

    return pedal_frame