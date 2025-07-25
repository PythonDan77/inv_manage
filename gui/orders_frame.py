import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

current_order_customizations = []
product_dict = {}
selected_order_id = 0

# Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM orders')
        all_records = cur.fetchall()
        orders_treeview.delete(*orders_treeview.get_children())
        for record in all_records:
            orders_treeview.insert('', 'end', values=record)

# History tab that provides access to the table order_history.
def history_popup():

    popup = tk.Toplevel(bg='white')
    popup.title("Order History")
    popup.geometry("1150x650+400+250")
    popup.transient()  # Keeps it on top
    popup.grab_set()   # Modal behavior

    history_treeview = None

    heading_label = tk.Label(popup, text='Order History', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    top_frame = tk.Frame(popup, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()

    # Function verifies data has been used to search the database and then retrieves the data.
    def hist_search_item(search_option, value):
        if search_option == 'Select..':
            messagebox.showerror('Error','Select an option.')
        elif not value:
            messagebox.showerror('Error','Enter a value to search.')
        else:
            try:
                search_option = search_option.replace(' ', '_')
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute(f'SELECT * FROM order_history WHERE {search_option} LIKE %s', f'%{value}%')
                    result = cur.fetchall()
                    history_treeview.delete(*history_treeview.get_children())
                    for record in result:
                        history_treeview.insert('', 'end', values=record)

            except Exception as e:
                messagebox.showerror("Database Error", str(e))

    # Reloads all data and resets the search options.
    def hist_search_all(search_entry, search_combobox):
        hist_treeview()
        search_entry.delete(0,'end')
        search_combobox.set('Select..')

    # Clear the highlight from the combobox. Trigger in the main function at the bottom.
    def hist_on_select(event, combobox):
        combobox.selection_clear()

    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'customer name', 'customer po'), 
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
                                            command= lambda: hist_search_item(search_combobox.get(),search_entry.get())
                                            )
    search_button.grid(row=0, column=2, padx=20)

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 10, 
                                          cursor='hand2',
                                          command= lambda: hist_search_all(search_entry, search_combobox)
                                          )
    show_button.grid(row=0, column=3)

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    history_treeview = ttk.Treeview(top_frame, columns=('id','customer_name', 'customer_po', 'product_name',
                                                        'qty', 'notes', 'status', 'created_at', 
                                                        'created_by'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=history_treeview.xview)
    vertical_scrollbar.config(command=history_treeview.yview)
    history_treeview.pack(pady= (10, 0))
    
    history_treeview.heading('id', text='ID')
    history_treeview.heading('customer_name', text='Customer name')
    history_treeview.heading('customer_po', text='PO #')
    history_treeview.heading('product_name', text='Product name')
    history_treeview.heading('qty', text='Qty')
    history_treeview.heading('notes', text='Notes')
    history_treeview.heading('status', text='Status')
    history_treeview.heading('created_at', text='Order created')
    history_treeview.heading('created_by', text='Created by')
    
    history_treeview.column('id', width=120)
    history_treeview.column('customer_name', width=175)
    history_treeview.column('customer_po', width=175)
    history_treeview.column('product_name', width=200)
    history_treeview.column('qty', width=150)
    history_treeview.column('notes', width=300)
    history_treeview.column('status', width=175)
    history_treeview.column('created_at', width=175)
    history_treeview.column('created_by', width=200)

    
    def hist_treeview():
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM order_history"""
                )
                all_records = cur.fetchall()
                history_treeview.delete(*history_treeview.get_children())
                for record in all_records:
                    clean_record = ["" if field is None else field for field in record]
                    history_treeview.insert('', 'end', values=clean_record)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    #call treeview function to display the items.
    hist_treeview()

    button_frame= tk.Frame(popup, bg='white')
    button_frame.place(x=400, y=500, relwidth=1)

    def cancel():
        popup.destroy()

    close_button = tk.Button(button_frame, text='Close', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=cancel)
                                                                  
    close_button.grid(row=0, column=0, padx=20)

    def export_purchase_history_to_csv():
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM order_history")
                rows = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]

            if not rows:
                messagebox.showinfo("Export", "No data in order history.")
                return

            # Default filename
            default_filename = f"order_history_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

            # Path to user's Desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            # Ask where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                initialdir=desktop_path,
                title="Save Order History As"
            )

            if not file_path:
                return  # User cancelled

            # Write the CSV file
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(column_names)  # headers
                writer.writerows(rows)         # data

            messagebox.showinfo("Export Successful", f"CSV file saved:\n{file_path}")

            # Optionally open the file (Windows only)
            try:
                os.startfile(file_path)
            except:
                pass

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    excel_button = tk.Button(button_frame, text='Excel Sheet', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=export_purchase_history_to_csv
                                        )
                                                                  
    excel_button.grid(row=0, column=1, padx=20)

    search_combobox.bind("<<ComboboxSelected>>", lambda event: hist_on_select(event, search_combobox))

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
        messagebox.showerror('Empty Field', 'Select a Product Type.')
        return None

    if product_type == 'Amplifier':
        if not voltage:
            messagebox.showerror('Empty Field', 'Voltage cannot be empty.')
            return None
    
    if product_type in ['Cabinet']:
        voltage = 'N/A'

    if product_type == 'Pedal':
        voltage = '9V DC'
        if not qty:
            messagebox.showerror('Empty Field', 'Qty cannot be empty.')
            return None

    if product_type in ['Amplifier', 'Cabinet']:
        qty = 1

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
# Delete the selected row/item.
def delete_item(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, cur_id):

    result = messagebox.askyesno('Confirm', 'Do you want to delete this order?')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM order_customizations WHERE order_id = %s", (cur_id,))
                cur.execute('DELETE FROM orders WHERE id=%s',(cur_id,))
                
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
            clear_fields((
                        customer_name,
                        po_num,
                        qty,
                        notes,
                        voltage),
                        combobox1=customer_type,
                        combobox2=product,
                        combobox3=product_type)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Cancel an order. Add it to the order_history table. For amps and cabs, they can only be cancelled if they are pending.
def cancel_order(order_id, product):
    result = messagebox.askyesno('Confirm', 'Do you want to cancel this order?')
    if not result:
        return
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            # Fetch full order info
            cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cur.fetchone()
            if not order:
                messagebox.showerror("Error", "Order not found.")
                return
            product_type = order[5]
            product_name = product.get()
            product_id = order[4]
            po_number = order[3]
            customer_name = order[1]
            quantity = order[7]
            notes = order[8]
            created_at = order[10]
            created_by = order[11]

            # PEDAL logic
            if product_type == "Pedal":
                cur.execute("DELETE FROM pedal_orders WHERE order_id = %s", (order_id,))
                cur.execute("""
                    INSERT INTO order_history (
                        customer_name, po_number, product_name, quantity, 
                        notes, status, created_at, created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    customer_name, po_number, product_name, quantity,
                    notes, "Cancelled", created_at, created_by
                ))
                cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
                conn.commit()
                messagebox.showinfo("Order Cancelled", "Pedal order was cancelled.")
                return

            # AMP or CAB logic
            amp_ok = cab_ok = True

            # Check amplifier build status
            cur.execute("SELECT status FROM amplifier_builds WHERE order_id = %s", (order_id,))
            amp = cur.fetchone()
            
            if amp and amp[0].lower() != "pending":
                amp_ok = False

            # Check cabinet build status
            cur.execute("SELECT status FROM cabinet_builds WHERE order_id = %s", (order_id,))
            cab = cur.fetchone()
            if cab and cab[0].lower() != "pending":
                cab_ok = False

            if not amp_ok or not cab_ok:
                messagebox.showerror("Cannot Cancel", "Build already started. Cannot cancel this order. Re-assign or mark 'internal' for inventory.")
                return

            # Safe to remove everything
            cur.execute("DELETE FROM amplifier_builds WHERE order_id = %s", (order_id,))
            cur.execute("DELETE FROM cabinet_builds WHERE order_id = %s", (order_id,))
            cur.execute("DELETE FROM order_customizations WHERE order_id = %s", (order_id,))
            cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))

            cur.execute("""
                INSERT INTO order_history (
                    customer_name, po_number, product_name, quantity,
                    notes, status, created_at, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer_name, po_number, product_name, quantity,
                notes, "Cancelled", created_at, created_by
            ))

            conn.commit()
            messagebox.showinfo("Order Cancelled", "Order successfully cancelled and archived.")
            treeview()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, update=False, delete=False, cancel=False):
    
    selected = orders_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = orders_treeview.item(selected)
    id_num = data['values'][0]
    
    if update:
        add_update_item(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, update=True, cur_id=id_num)
    elif delete:
        delete_item(customer_name, customer_type, po_num, product, product_type, qty, notes, voltage, id_num)
    elif cancel:
        cancel_order(id_num, product)

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
                    
                    cur.execute("""UPDATE orders SET 
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

                    if current_order_customizations:
                        # Clear old customizations
                        cur.execute("DELETE FROM order_customizations WHERE order_id = %s", (cur_id,))

                        # Insert updated customizations
                        for custom in current_order_customizations:
                            cur.execute("""
                                INSERT INTO order_customizations (order_id, option_name, option_value, part_id, quantity)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                cur_id,
                                custom["option_name"],
                                custom["option_value"],
                                custom["part_id"],
                                custom["quantity"]
                            ))

                    messagebox.showinfo('Success','Update successful.')
                else:
                    set_date = datetime.today().strftime('%Y-%m-%d')
                    cur.execute(
                        """INSERT INTO orders (customer_name, customer_type, po_number, product_id, product_type,
                                               voltage, quantity, notes, status,
                                               created_at, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                        *validated_data,
                        "Pending",
                        set_date,
                        user
                        )
                    )
                    order_id = cur.lastrowid

                    if validated_data[4].lower() in ['amplifier', 'cabinet']:

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

                    # Check if this order is for an amplifier and add data to the amplifier_builds table
                    if validated_data[4].lower() == 'amplifier':

                        # Unpack the necessary fields from validated_data or DB   
                        product_id = validated_data[3]
                        notes = validated_data[7]

                        # Insert into amplifier_builds for the chassis and electronics
                        cur.execute("""
                            INSERT INTO amplifier_builds (
                                order_id, product_id, status,
                                builder_name, serial_number, notes, build_start, completed_at, playtester
                            ) VALUES (%s, %s, %s, '', '', %s, '', '', '')
                        """, (
                            order_id, product_id,
                            'Pending', notes
                        ))
                        # Insert into cabinet_builds for headshells.
                        cur.execute("""
                            INSERT INTO cabinet_builds (
                                order_id, product_id, status, notes, build_start, completed_at
                            ) VALUES (%s, %s, %s, %s, '', '')
                        """, (order_id, product_id,"Pending", notes))

                    # Check if this order is for a pedal and add data to the pedal_orders table
                    if validated_data[4].lower() == 'pedal':

                        product_id = validated_data[3]
                        # cur.execute("SELECT product_name FROM products WHERE id = %s", (product_id,))
                        quantity = validated_data[6]
                        # notes = validated_data[7]

                        cur.execute("""
                            INSERT INTO pedal_orders (
                                order_id, product_id
                            ) VALUES (%s, %s)
                        """, (
                            order_id, product_id
                        ))

                    # Check if this order is for a cabinet and add data to the cabinet_builds table
                    if validated_data[4].lower() == 'cabinet':

                        product_id = validated_data[3]
                        notes = validated_data[7]

                        # Insert into cabinet_builds for speaker cabs.
                        cur.execute("""
                            INSERT INTO cabinet_builds (
                                order_id, product_id, status, notes, build_start, completed_at
                            ) VALUES (%s, %s, %s, %s, '', '')
                        """, (order_id, product_id,"Pending", notes))
                    
                    messagebox.showinfo('Success','Saved Successfully.')
            conn.commit()
            treeview()
        
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
# Clears data from all fields. Highlighted row is also cleared when the CLEAR button is pressed, but not when called from select_data().
def clear_fields(all_fields, combobox1, combobox2, combobox3, tab=False):
    global selected_order_id

    for field in all_fields:
        field.delete(0,tk.END)

    combobox1.set("Select..")
    combobox2.set("Select..")
    combobox3.set("Select..")

    if tab:
        selected_order_id = 0
        orders_treeview.selection_remove(orders_treeview.selection())

def select_data(event, all_fields, combobox1, combobox2, combobox3):
    global selected_order_id

    index = orders_treeview.selection()
    if index:
        content_dict = orders_treeview.item(index)
        row_data = content_dict['values']
        
        clear_fields(all_fields, combobox1=combobox1, combobox2=combobox2, combobox3=combobox3)

        selected_order_id = row_data[0]
        
        all_fields[0].insert(0, row_data[1])
        all_fields[1].insert(0, row_data[3])
        all_fields[2].insert(0, row_data[7])
        all_fields[3].insert(0, row_data[8])
        all_fields[4].insert(0, row_data[6])

        combobox1.set(row_data[2])
        for key, value in product_dict.items():
            if value == row_data[4]:
                combobox2.set(key)
        combobox3.set(row_data[5])

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
                cur.execute(f'SELECT * FROM orders WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                orders_treeview.delete(*orders_treeview.get_children())
                for record in result:
                    orders_treeview.insert('', 'end', values=record)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Reloads all data and resets the search options.
def search_all(search_entry, search_combobox):
    treeview()
    search_entry.delete(0,'end')
    search_combobox.set('Select..')

# Clear the highlight from the combobox. Trigger in the main function at the bottom.
def on_select(event, combobox):
    combobox.selection_clear()

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
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Customer name', 'PO number'), 
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

    history_button = tk.Button(search_frame, text='History', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 10, 
                                          cursor='hand2',
                                          command= lambda: history_popup())
    history_button.grid(row=0, column=4,padx=20)

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    orders_treeview = ttk.Treeview(top_frame, columns=('id', 'customer_name', 'customer_type', 'po_number', 'product_id', 'product_type', 
                                                       'voltage', 'qty', 'notes', 'status', 'created_at', 'created_by'), 
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

    # product_label = product_combobox.get()
    # product_id = product_dict.get(product_label)
    
    product_type_label = tk.Label(detail_frame, text='Product type', font=('times new roman', 10, 'bold'), bg='white')
    product_type_label.grid(row=1, column=2, padx=10, pady=20)
    product_type_combobox = ttk.Combobox(detail_frame, width=17, values=('Amplifier','Pedal', 'Cabinet'), 
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

    voltage_label = tk.Label(detail_frame, text='Voltage', font=('times new roman', 10, 'bold'), bg='white')
    voltage_label.grid(row=2, column=2, padx=10, pady=20)
    voltage_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    voltage_entry.grid(row=2, column=3, padx=10, pady=20)

    customize_btn = tk.Button(detail_frame, text='Amp/Cab Customizations', 
                                         font=('times new roman', 12), 
                                         bg='red', 
                                         fg='white', 
                                         width= 20, 
                                         cursor='hand2',
                                         command= lambda:open_customization_popup(order_id=selected_order_id)
                                        )

    

    def open_customization_popup(order_id=None):
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
        
        def fetch_order_customizations(order_id):
            try:
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT option_name, option_value, part_id, quantity
                        FROM order_customizations
                        WHERE order_id = %s
                    """, (order_id,))
                    return cur.fetchall()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
                return []

        if order_id:
            existing = fetch_order_customizations(order_id)
            for opt_name, opt_value, part_id, qty in existing:
                customizations.append({
                    "option_name": opt_name,
                    "option_value": opt_value,
                    "part_id": part_id,
                    "quantity": qty
                })
                tree.insert("", "end", values=(opt_name, opt_value, part_id, qty))

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
    button_frame.place(x=140, y=550, relwidth=1)

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

    update_button = tk.Button(button_frame, text='Update', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(cust_name_entry.get(),
                                                                         cust_type_combobox.get(),
                                                                         po_entry.get(),
                                                                         product_combobox.get(),
                                                                         product_type_combobox.get(),
                                                                         qty_entry.get(),
                                                                         notes_entry.get(),
                                                                         voltage_entry.get(),
                                                                         update=True)
                                                                  )

    delete_button = tk.Button(button_frame, text='Delete', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(
                                                             cust_name_entry,
                                                             cust_type_combobox,
                                                             po_entry,
                                                             product_combobox,
                                                             product_type_combobox,
                                                             qty_entry,
                                                             notes_entry,
                                                             voltage_entry,
                                                             delete=True)
                                                                )
    
    # Clicking the clear button triggers the clear_fields() function and removes all data from the entry fields.
    clear_button = tk.Button(button_frame, text='Clear', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: clear_fields((
                                                             cust_name_entry,
                                                             po_entry,
                                                             qty_entry,
                                                             notes_entry,
                                                             voltage_entry),
                                                             combobox1=cust_type_combobox,
                                                             combobox2=product_combobox,
                                                             combobox3=product_type_combobox,
                                                             tab=True)
                                                                  )

    # Clicking the clear button triggers the clear_fields() function and removes all data from the entry fields.
    cancel_button = tk.Button(button_frame, text='Cancel Order', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: row_select_check(
                                                             cust_name_entry,
                                                             cust_type_combobox,
                                                             po_entry,
                                                             product_combobox,
                                                             product_type_combobox,
                                                             qty_entry,
                                                             notes_entry,
                                                             voltage_entry,
                                                             cancel=True)
                                                                  )
    
    # When a field in treeview is clicked, the select_data() function fills the entry fields.
    orders_treeview.bind('<ButtonRelease-1>', lambda event: select_data(
                                                            event,
                                                            (cust_name_entry,
                                                             po_entry,
                                                             qty_entry,
                                                             notes_entry,
                                                             voltage_entry),
                                                             cust_type_combobox,
                                                             product_combobox,
                                                             product_type_combobox)
                                                            )
    if user_info['role'] in ['manager', 'admin']:
        customize_btn.grid(row=2, column=5)
        add_button.grid(row=0, column=0, padx=20)
        update_button.grid(row=0, column=1, padx=20)
        clear_button.grid(row=0, column=3, padx=20)
        cancel_button.grid(row=0, column=4, padx=20)
        

    if user_info['role'] in ['manager', 'admin']:
        delete_button.grid(row=0, column=5, padx=20)

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))
    cust_type_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, cust_type_combobox))
    product_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, product_combobox))
    product_type_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, product_type_combobox))
    
    return orders_frame