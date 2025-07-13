import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

current_order_customizations = []
product_dict = {}

# Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM orders')
        all_records = cur.fetchall()
        orders_treeview.delete(*orders_treeview.get_children())
        for record in all_records:
            orders_treeview.insert('', 'end', values=record)

# Function used to verify all data in fields is present and of the right type.
def validate_form_inputs(customer_name, customer_type, po_num, product_id, product_type, voltage, qty, notes):
    
    if not customer_name:
        messagebox.showerror('Empty Field', 'Customer Name cannot be empty.')
        return None

    if customer_type == "Select..":
        messagebox.showerror('Empty Field', 'Select a customer type.')
        return None

    if not product_id:
        messagebox.showerror('Empty Field', 'Select a Product.')
        return None

    if product_type == "Select..":
        messagebox.showerror('Empty Field', 'Select a Product.')
        return None

    if not voltage:
        messagebox.showerror('Empty Field', 'Voltage cannot be empty.')
        return None

    if not qty:
        messagebox.showerror('Empty Field', 'Qty cannot be empty.')
        return None

    try:
        qty = int(qty)
    except ValueError:
        messagebox.showerror("Validation Error", "Quantity must be a number.")
        return None

    if not po_num:
        po_num = "0"

    if not notes:
        notes = ""

    return (customer_name.strip(),
            customer_type.strip(),
            po_num.strip(),
            int(product_id),
            product_type.strip(),
            voltage.strip(),
            int(qty),
            notes.strip()
        )

# Check to make sure a row is selected to either update or delete.
def row_select_check(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, update=False, delete=False):
    
    selected = orders_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = orders_treeview.item(selected)
    id_num = data['values'][0]

    if update:
        add_update_item(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, True, id_num)
    elif delete:
        delete_item(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, id_num)

# When all fields are filled and the add button is pressed, this function adds the items to the database.
def add_update_item(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, user=None, update=False, cur_id=None):
    
    product_label = product
    product_id = product_dict.get(product_label)

    validated_data = validate_form_inputs(customer_name, customer_type, po_num, product_id, product_type, voltage, qty, notes)

    if not validated_data:
        return
    else:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                if update:
                    cur.execute('SELECT * FROM orders WHERE id = %s', (cur_id,))
                    current_db_data = cur.fetchone()
                    if not current_db_data:
                        messagebox.showerror("Error", 'The item does not exist.')
                        return

                    current_db_data = current_db_data[1:]
                    if current_db_data == validated_data:
                        messagebox.showinfo('No Changes','No Changes Detected.')
                        return
                    else:
                        cur.execute("""UPDATE orders SET part_name=%s, 
                                    customer_name=%s, 
                                    customer_type=%s, 
                                    po_number=%s, 
                                    product_id=%s,  
                                    product_type=%s,
                                    voltage=%s,
                                    quantity=%s,
                                    notes=%s WHERE id=%s""",
                                    
                                    (*validated_data,
                                    cur_id)
                                    )

                        messagebox.showinfo('Success','Update successful.')
                else:
                    
                    cur.execute(
                        """INSERT INTO orders (customer_name, customer_type, po_number, product_id, product_type,
                                               voltage, quantity, notes, status, builder_name,
                                               created_at, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)""",
                        (
                        *validated_data,
                        "Pending",
                        "",
                        user
                        )
                    )
                    order_id = cur.lastrowid

                    for custom in current_order_customizations:
                        cur.execute("""
                            INSERT INTO order_customizations (order_id, option_name, option_value, part_id, quantity)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            order_id,
                            custom["option_name"],
                            custom["option_value"],
                            custom["part_id"],
                            custom["quantity"]
                            ))
                    messagebox.showinfo('Success','Saved Successfully.')
            conn.commit()
            treeview()
        
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


def orders_frame(parent, user_info):
    global orders_treeview
    
    orders_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    orders_frame.place(x=201, y=100)

    heading_label = tk.Label(orders_frame, text='Order Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(orders_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:orders_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(orders_frame, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Cust name', 'PO'), 
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
    
    orders_treeview = ttk.Treeview(top_frame, columns=('id', 'customer_name', 'customer_type', 'po_number', 'product_id', 'product_type', 
                                                       'voltage', 'qty', 'notes', 'status', 'builder', 'created_at', 'created_by'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=orders_treeview.xview)
    vertical_scrollbar.config(command=orders_treeview.yview)
    orders_treeview.pack(pady= (10, 0))
    
    orders_treeview.heading('id', text='ID')
    orders_treeview.heading('customer_name', text='Customer name')
    orders_treeview.heading('customer_type', text='Customer type')
    orders_treeview.heading('po_number', text='P.O. #')
    orders_treeview.heading('product_id', text='Product')
    orders_treeview.heading('product_type', text='Product Type')
    orders_treeview.heading('voltage', text='Voltage')
    orders_treeview.heading('qty', text='Qty')
    orders_treeview.heading('notes', text='Notes')
    orders_treeview.heading('status', text='Status')
    orders_treeview.heading('builder', text='Builder')
    orders_treeview.heading('created_at', text='Order created')
    orders_treeview.heading('created_by', text='Created by')
    
    orders_treeview.column('id', width=70)
    orders_treeview.column('customer_name', width=200)
    orders_treeview.column('customer_type', width=175)
    orders_treeview.column('po_number', width=150)
    orders_treeview.column('product_id', width=120)
    orders_treeview.column('product_type', width=150)
    orders_treeview.column('voltage', width=90)
    orders_treeview.column('qty', width=90)
    orders_treeview.column('notes', width=300)
    orders_treeview.column('status', width=150)
    orders_treeview.column('builder', width=150)
    orders_treeview.column('created_at', width=175)
    orders_treeview.column('created_by', width=150)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(orders_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    cust_name_label = tk.Label(detail_frame, text='Customer Name', font=('times new roman', 10, 'bold'), bg='white')
    cust_name_label.grid(row=0, column=0,padx=10, pady=20)
    cust_name_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    cust_name_entry.grid(row=0, column=1, padx=10, pady=20 )

    cust_type_label = tk.Label(detail_frame, text='Customer Type', font=('times new roman', 10, 'bold'), bg='white')
    cust_type_label.grid(row=0, column=2, padx=10, pady=20)
    cust_type_combobox = ttk.Combobox(detail_frame, width=17, values=('Direct', 'Dealer', 'Distributor', 'Internal'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    cust_type_combobox.set('Select..')
    cust_type_combobox.grid(row=0, column=3, padx=10, pady=20)

    po_label = tk.Label(detail_frame, text='P.O. #', font=('times new roman', 10, 'bold'), bg='white')
    po_label.grid(row=0, column=4, padx=10, pady=20)
    po_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    po_entry.grid(row=0, column=5, padx=10, pady=20)

    # Create a dict for the product list and use the values for the drop down menu.

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id, product_name, product_code FROM products")
            rows = cur.fetchall()
            for row in rows:
                label = f"{row[1]}"  # e.g., "G120 Amp (AMP001)"
                product_dict[label] = row[0]
    except Exception as e:
        messagebox.showerror("DB Error", str(e))


    product_label = tk.Label(detail_frame, text='Product', font=('times new roman', 10, 'bold'), bg='white')
    product_label.grid(row=1, column=0, padx=10, pady=20)
    product_combobox = ttk.Combobox(detail_frame, width=17, values=list(product_dict.keys()), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    product_combobox.set('Select..')
    product_combobox.grid(row=1, column=1, padx=10, pady=20)

    product_label = product_combobox.get()
    product_id = product_dict.get(product_label)
    
    product_type_label = tk.Label(detail_frame, text='Product type', font=('times new roman', 10, 'bold'), bg='white')
    product_type_label.grid(row=1, column=2, padx=10, pady=20)
    product_type_combobox = ttk.Combobox(detail_frame, width=17, values=('Amplifier','Pedal', 'Cabinet', 'Woodshop'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    product_type_combobox.set('Select..')
    product_type_combobox.grid(row=1, column=3, padx=10, pady=20)

    qty_label = tk.Label(detail_frame, text='Quantity', font=('times new roman', 10, 'bold'), bg='white')
    qty_label.grid(row=1, column=4, padx=10, pady=20)
    qty_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    qty_entry.grid(row=1, column=5, padx=10, pady=20)

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white')
    notes_label.grid(row=2, column=0, padx=10, pady=20)
    notes_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    notes_entry.grid(row=2, column=1, padx=10, pady=20)

    voltage_label = tk.Label(detail_frame, text='Voltage (if appl)', font=('times new roman', 10, 'bold'), bg='white')
    voltage_label.grid(row=2, column=2, padx=10, pady=20)
    voltage_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    voltage_entry.grid(row=2, column=3, padx=10, pady=20)

    customize_btn = tk.Button(detail_frame, text='Configure Customizations', 
                                         font=('times new roman', 12), 
                                         bg='red', 
                                         fg='white', 
                                         width= 20, 
                                         cursor='hand2',
                                         command= lambda:open_customization_popup()
                                        )

    customize_btn.grid(row=2, column=5)

    def open_customization_popup():
        popup = tk.Toplevel()
        popup.title("Add Customizations")
        popup.geometry("825x400+500+300")
        popup.grab_set()

        customizations = []  # This will store customization entries locally

        # Dropdown for customization type
        tk.Label(popup, text="Customization Type").grid(row=0, column=0, padx=5, pady=5)
        customization_type_cb = ttk.Combobox(popup, values=["Tolex", "Knobs", "Tubes", "Corners", 
                                                            "Handle", "Chassis", "Faceplate", "Piping", 
                                                            "Speakers", "Grill_Cloth"], state="readonly")
        customization_type_cb.grid(row=0, column=1, padx=5)

        # Dropdown for parts from inventory
        tk.Label(popup, text="Part").grid(row=1, column=0, padx=5, pady=5)
        part_cb = ttk.Combobox(popup, state="readonly")
        part_cb.grid(row=1, column=1, padx=5)

        # Quantity Entry
        tk.Label(popup, text="Quantity").grid(row=2, column=0, padx=5, pady=5)
        quantity_entry = tk.Entry(popup)
        quantity_entry.insert(0, "1")
        quantity_entry.grid(row=2, column=1, padx=5)

        # Treeview to show added customizations
        tree = ttk.Treeview(popup, columns=("Type", "Part Name", "Part ID", "Qty"), show="headings")
        tree.heading("Type", text="Type")
        tree.heading("Part Name", text="Part Name")
        tree.heading("Part ID", text="Part ID")
        tree.heading("Qty", text="Qty")
        tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Fetch parts when type changes
        def update_part_dropdown(event):
            selected_type = customization_type_cb.get()
            try:
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, part_name FROM inventory_items
                        WHERE item_category = 'Customization' AND part_name LIKE %s
                    """, (f"%{selected_type}%",))
                    rows = cur.fetchall()
                    part_cb['values'] = [f"{r[0]} - {r[1]}" for r in rows]
            except Exception as e:
                messagebox.showerror("Error", str(e))

        customization_type_cb.bind("<<ComboboxSelected>>", update_part_dropdown)

        # Add customization
        def add_customization():
            option_name = customization_type_cb.get()
            part_value = part_cb.get()
            qty = quantity_entry.get()

            if not option_name or not part_value:
                messagebox.showwarning("Missing Info", "Select both a customization type and part.")
                return

            try:
                qty = int(qty)
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Quantity must be a number.")
                return

            part_id, part_name = part_value.split(" - ", 1)
            customizations.append({
                "option_name": option_name,
                "option_value": part_name,
                "part_id": int(part_id),
                "quantity": qty
            })
            tree.insert("", "end", values=(option_name, part_name, part_id, qty))

        # Remove customization
        def remove_customization():
            selected = tree.selection()
            if selected:
                index = tree.index(selected[0])
                tree.delete(selected[0])
                del customizations[index]

        # Finish and close
        def done():
            # Pass back to main frame
            global current_order_customizations
            current_order_customizations = customizations
            popup.destroy()

        # Buttons
        btn_frame = tk.Frame(popup)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)

        tk.Button(btn_frame, text="Add", command=add_customization).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove", command=remove_customization).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Done", command=done).pack(side=tk.RIGHT, padx=5)

    #Lower button Frame
    button_frame= tk.Frame(orders_frame, bg='white')
    button_frame.place(x=180, y=550, relwidth=1)

    add_button = tk.Button(button_frame, text='Add', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: add_update_item(cust_name_entry.get(),
                                                                         cust_type_combobox.get(),
                                                                         po_entry.get(),
                                                                         product_combobox.get(),
                                                                         product_type_combobox.get(),
                                                                         qty_entry.get(),
                                                                         notes_entry.get(),
                                                                         voltage_entry.get(),
                                                                         user_info['full_name']
                                                                         )
                                                                  )
    add_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(cust_name_entry.get(),
                                                                         cust_type_combobox.get(),
                                                                         po_entry.get(),
                                                                         product_id,
                                                                         product_type_combobox.get(),
                                                                         qty_entry.get(),
                                                                         notes_entry.get(),
                                                                         voltage_entry.get(),
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
                                                                low_entry,
                                                                restock_qty_entry,
                                                                item_type_combobox,
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
                                                                  low_entry,
                                                                  restock_qty_entry
                                                                  ), 
                                                                  combobox=item_type_combobox,
                                                                  tab=True)
                                                                  )
    clear_button.grid(row=0, column=3, padx=20)
    
    