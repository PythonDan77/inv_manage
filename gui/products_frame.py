import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

bom_data = []

# Used to populate the treeview form with products.
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM products')
        all_records = cur.fetchall()
        products_treeview.delete(*products_treeview.get_children())
        for record in all_records:
            products_treeview.insert('', 'end', values=record)

# Check to make sure a row is selected to either update or delete.
def row_select_check(product_name, product_number, product_type, inventory_item_entry=None, item_qty_entry=None, add_bom_button=None, update=False, delete=False):
    
    selected = products_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = products_treeview.item(selected)
    id_num = data['values'][0]
    if update:
        add_update_item(product_name, product_number, product_type, True, id_num)
    elif delete:
        delete_item(product_name, product_number, product_type, inventory_item_entry, item_qty_entry, add_bom_button, id_num)

 # Add and update products.
def add_update_item(product_name, product_number, product_type, update=False, cur_id=None):

    product_name = product_name.strip()
    product_number = product_number.strip()
    product_type = product_type.strip()
    
    if product_type == 'Select..':
        messagebox.showerror("Error", 'Product Type must be selected.')
        return

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            if update:
                cur.execute('SELECT * FROM products WHERE id = %s', (cur_id,))
                current_db_data = cur.fetchone()
                if not current_db_data:
                    messagebox.showerror("Error", 'The product does not exist.')
                    return
                current_db_data = current_db_data[1:]

                if current_db_data == (product_name, product_number, product_type):
                    messagebox.showinfo('No Changes','No Changes Detected.')
                    return
                else:
                    cur.execute("""UPDATE products SET product_name=%s, 
                                product_code=%s,
                                product_type=%s
                                WHERE id=%s""",
                                
                                (product_name,
                                product_number,
                                product_type,
                                cur_id)
                                )

                    messagebox.showinfo('Success','Update successful.')
            else:

                cur.execute(
                    """SELECT * FROM products
                    WHERE product_name = %s AND product_code = %s
                    """, (product_name, product_number))
                
                if cur.fetchone():
                    messagebox.showerror("Duplicate Error", 'The item already exists.')
                    return

                else:
                    cur.execute(
                        """INSERT INTO products (product_name, product_code, product_type) VALUES (%s, %s, %s)""",
                        (product_name, product_number, product_type)
                    )
                    messagebox.showinfo('Success','Saved Successfully.')
        conn.commit()
        treeview()
    
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Delete the selected row/item.
def delete_item(product_name, product_number, product_type, inventory_item_entry, item_qty_entry, add_bom_button, id_num):
    result = messagebox.askyesno('Confirm', 'Do you want to delete this product and the BOM?')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                # First, delete related BOM entries
                cur.execute('DELETE FROM bill_of_materials WHERE product_id=%s', (id_num,))
                # Then delete the product
                cur.execute('DELETE FROM products WHERE id=%s', (id_num,))
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
            product_name.delete(0, tk.END)
            product_number.delete(0, tk.END)
            inventory_item_entry.delete(0, tk.END)
            add_bom_button.config(state='disabled')
            item_qty_entry.delete(0, tk.END)
            product_type.set("Select..")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


def products_frame(parent, user_info):
    global products_treeview
    selected_part = {"id": None}
    
    products_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    products_frame.place(x=201, y=100)

    heading_label = tk.Label(products_frame, text='Product Detail', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(products_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:products_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Left Frame Code
    left_frame = tk.Frame(products_frame, width=450, height=600, bg='white')
    left_frame.place(x=0, y=75)
    left_frame.grid_propagate(False)
    
    #Top Section of left frame
    top_frame = tk.Frame(left_frame, width=450, height=240, bg='white')
    top_frame.place(x=0, y=10, relwidth=1)
    
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')

    products_treeview = ttk.Treeview(top_frame,columns=('id', 'product_name', 'product_code'), 
                                            show='headings', 
                                            yscrollcommand=vertical_scrollbar.set, height=11)
  
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    vertical_scrollbar.config(command=products_treeview.yview)
    products_treeview.pack(pady= (10, 0))

    products_treeview.heading('id', text='ID')
    products_treeview.heading('product_name', text='Product name')
    products_treeview.heading('product_code', text='Product code')
  
    products_treeview.column('id', width=50)
    products_treeview.column('product_name', width=195)
    products_treeview.column('product_code', width=175)

    #call treeview function to display the items.
    treeview()
    
    #Detail frame for the entry and lebel fields
    detail_frame = tk.Frame(left_frame, width=450, height=150, bg='white')
    detail_frame.place(x=0, y=275, relwidth=1)

    product_name_label = tk.Label(detail_frame, text='Product Name', font=('times new roman', 10, 'bold'), bg='white')
    product_name_label.grid(row=0, column=0,padx=10, pady=(20,0))
    product_name_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', width=30)
    product_name_entry.grid(row=0, column=1, padx=10, pady=(20,0) )

    product_id_label = tk.Label(detail_frame, text='Product ID', font=('times new roman', 10, 'bold'), bg='white')
    product_id_label.grid(row=1, column=0, padx=10, pady=(20,0))
    product_id_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', width=30)
    product_id_entry.grid(row=1, column=1, padx=10, pady=(20,0))

    item_category_label = tk.Label(detail_frame, text='Product Type', font=('times new roman', 10, 'bold'), bg='white')
    item_category_label.grid(row=2, column=0, padx=10, pady=(20,0))
    item_category_combobox = ttk.Combobox(detail_frame, width=17, values=('Amplifier','Pedal','Cabinet','Sub-Assembly'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    item_category_combobox.set('Select..')
    item_category_combobox.grid(row=2, column=1, padx=10, pady=(20,0))
    
    #Bottom frame for the buttons.
    bottom_frame = tk.Frame(left_frame, width=450, height=150, bg='white')
    bottom_frame.place(x=0, y=430, relwidth=1)

    button_frame = tk.Frame(bottom_frame, width=450, height=150, bg='white')
    button_frame.pack(pady= (30, 0))

    add_button = tk.Button(button_frame, text='Add', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: add_update_item(product_name_entry.get(), 
                                                                  product_id_entry.get(),item_category_combobox.get())
                                                                  )
    add_button.grid(row=0, column=0, padx=(20,0), pady=20)

    update_button = tk.Button(button_frame, text='Update', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: row_select_check(product_name_entry.get(), 
                                                                  product_id_entry.get(),item_category_combobox.get(),
                                                                  update=True)
                                        )
    update_button.grid(row=0, column=1, padx=(20,0), pady=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command=lambda: row_select_check(product_name_entry, 
                                                                  product_id_entry, 
                                                                  item_category_combobox,
                                                                  inventory_item_entry, 
                                                                  item_qty_entry,
                                                                  add_bom_button,
                                                                  delete=True)
                                         )
                                        
    delete_button.grid(row=0, column=2, padx=(20,0), pady=20)

    #Right frame code
    right_frame = tk.Frame(products_frame, width=560, height=800, bg='white')
    right_frame.place(x=450, y=75, width=650)
    right_frame.grid_propagate(False)

    #Detail frame for the entry and label fields in right frame.
    right_detail_frame = tk.Frame(right_frame, width=450, height=150, bg='white')
    right_detail_frame.place(x=60, y=0, relwidth=1)

    inventory_item_label = tk.Label(right_detail_frame, text='Inventory Item', font=('times new roman', 10, 'bold'), bg='white')
    inventory_item_label.grid(row=0, column=0,padx=10, pady=(10,0))
    inventory_item_entry = tk.Entry(right_detail_frame, font=('times new roman', 11), bg='lightyellow', width=25, state="disabled")
    inventory_item_entry.grid(row=0, column=1, padx=10, pady=(10,0) )

    item_search_button = tk.Button(right_detail_frame, text='Item Search', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         state="disabled",
                                         command=lambda: open_part_search_popup()
                                         )
                                        
    item_search_button.grid(row=0, column=2, padx=10, pady=(10,0))

    item_qty_label = tk.Label(right_detail_frame, text='Qty Used', font=('times new roman', 10, 'bold'), bg='white')
    item_qty_label.grid(row=1, column=0, padx=10, pady=20)
    item_qty_entry = tk.Entry(right_detail_frame, font=('times new roman', 11), bg='lightyellow', width=25, state="disabled")
    item_qty_entry.grid(row=1, column=1, padx=10, pady=20)

    add_bom_button = tk.Button(right_detail_frame, text='Add to BOM', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         state="disabled",
                                         command=lambda: add_bom_item()
                                         )
                                        
    add_bom_button.grid(row=1, column=2, padx=10, pady=20)

    #Search Frame
    search_frame = tk.Frame(right_frame, bg='white')
    search_frame.place(x=60, y=140, relwidth=1)

    # Search function called when search button is pressed.
    def filter_bom_tree():
        search_term = bom_search_entry.get().strip().lower()
        bom_treeview.delete(*bom_treeview.get_children())
        for row in bom_data:
            f_bom_id, part_name, part_number, qty = row
            if search_term in part_name.lower():
                bom_treeview.insert("", "end", values=(f_bom_id, part_name, part_number, qty))

    # Function used to repopulate the bom treeview when all button is pressed.
    def reset_bom_tree():
        bom_search_entry.delete(0, tk.END)  # Clear the search box
        bom_treeview.delete(*bom_treeview.get_children())

        for row in bom_data:
            f_bom_id, part_name, part_number, qty = row
            bom_treeview.insert("", "end", values=(f_bom_id, part_name, part_number, qty))
        
    part_name_label = tk.Label(search_frame, text='Part Name', font=('times new roman', 10, 'bold'), bg='white')
    part_name_label.grid(row=0, column=1, padx=(0,10))

    bom_search_entry = tk.Entry(search_frame, font=('times new roman', 12), bg='lightyellow')
    bom_search_entry.grid(row=0, column=2)

    search_button = tk.Button(search_frame, text='Search', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 6, 
                                            cursor='hand2',
                                            command=lambda: filter_bom_tree()
                                            )
    search_button.grid(row=0, column=3, padx=20)

    show_button = tk.Button(search_frame, text='All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 6, 
                                          cursor='hand2',
                                          command= lambda: reset_bom_tree()
                                        )
    show_button.grid(row=0, column=4)

    # Frame for the bom treeview
    right_mid_frame = tk.Frame(right_frame, width=450, height=240, bg='white')
    right_mid_frame.place(x=0, y=170, relwidth=1)
    
    r_vertical_scrollbar = tk.Scrollbar(right_mid_frame, orient='vertical')

    bom_treeview = ttk.Treeview(right_mid_frame,columns=('bom_id', 'part_name', 'part_number', 'qty_used'), 
                                            show='headings', 
                                            yscrollcommand=r_vertical_scrollbar.set, height=11)
  
    r_vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    r_vertical_scrollbar.config(command=bom_treeview.yview)
    bom_treeview.pack(pady= (10, 0))
    
    bom_treeview.heading("bom_id", text="BOM ID")
    bom_treeview.heading('part_name', text='Part name')
    bom_treeview.heading('part_number', text='Part number')
    bom_treeview.heading('qty_used', text='Qty used')
    
    bom_treeview.column('bom_id', width=100)
    bom_treeview.column('part_name', width=200)
    bom_treeview.column('part_number', width=200)
    bom_treeview.column('qty_used', width=90)

    r_bottom_frame = tk.Frame(right_frame, width=450, height=150, bg='white')
    r_bottom_frame.place(x=0, y=430, relwidth=1)

    button_frame = tk.Frame(r_bottom_frame, width=450, height=150, bg='white')
    button_frame.pack(pady= (30, 0))

    # Function used to update the selected BOM quantity. A pop up window is created when pressed.
    def update_bom_quantity():
        selected = bom_treeview.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to update.")
            return

        values = bom_treeview.item(selected[0], "values")
        bom_id = int(values[0])
        part_name = values[1]
        current_qty = values[3]

        selected_prod_id = products_treeview.selection()
        id_content = products_treeview.item(selected_prod_id)
        new_row_data = id_content["values"]
        prod_id = int(new_row_data[0])
    
        # Pop-up
        popup = tk.Toplevel()
        popup.title("Update Quantity")
        popup.geometry("300x150+800+450")
        popup.grab_set()

        tk.Label(popup, text=f"Update quantity for '{part_name}'").pack(pady=10)

        qty_var = tk.StringVar(value=current_qty)
        tk.Entry(popup, textvariable=qty_var).pack(pady=5)

        def save_qty():
            try:
                new_qty = int(qty_var.get())
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute("UPDATE bill_of_materials SET quantity_needed = %s WHERE id = %s", (new_qty, bom_id))
                conn.commit()
                popup.destroy()
                refresh_bom_treeview(prod_id)
            except ValueError:
                messagebox.showerror("Invalid Input", "Quantity must be a number.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Save", command=save_qty).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(side=tk.RIGHT, padx=10, pady=10)

    update_button = tk.Button(button_frame, text='Update', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command= lambda: update_bom_quantity()
                                        )
    update_button.grid(row=0, column=1, padx=(10,0), pady=20)
    
    #Function used to remove an item from the bom table.
    def delete_bom_item():
        selected = bom_treeview.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a BOM item to delete.")
            return

        values = bom_treeview.item(selected[0], "values")
        bom_id = values[0]  # assuming bom_id is the first column

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this BOM item?")
        if not confirm:
            return

        selected_prod_id = products_treeview.selection()
        id_content = products_treeview.item(selected_prod_id)
        new_row_data = id_content["values"]
        prod_id = int(new_row_data[0])

        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM bill_of_materials WHERE id = %s", (bom_id,))
            conn.commit()

            # Refresh the tree
            refresh_bom_treeview(prod_id)
            messagebox.showinfo("Deleted", "BOM item deleted successfully.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    delete_button = tk.Button(button_frame, text='Delete', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2',
                                         command= lambda: delete_bom_item()
                                         )
                                        
    delete_button.grid(row=0, column=2, padx=(20,0), pady=20)

    def refresh_bom_treeview(product_id):
        global bom_data
        bom_data = []  # reset list

        bom_treeview.delete(*bom_treeview.get_children())

        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.id, i.part_name, i.part_number, b.quantity_needed
                    FROM bill_of_materials b
                    JOIN inventory_items i ON b.part_id = i.id
                    WHERE b.product_id = %s
                """, (product_id,))
                bom_data = cur.fetchall()

            for row in bom_data:
                bom_id, part_name, part_number, qty = row
                bom_treeview.insert("", "end", values=(bom_id, part_name, part_number, qty))

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # pop up window to search through inventory items.
    def open_part_search_popup():
        popup = tk.Toplevel()
        popup.title("Select Inventory Item")
        popup.geometry("800x400+650+400")
        popup.grab_set()

        # --- Search Bar ---
        search_frame = tk.Frame(popup)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search Part Name:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)

        # --- Treeview with Scrollbar ---
        tree_frame = tk.Frame(popup)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "part_name", "part_number")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def load_inventory(filter_text=""):
            tree.delete(*tree.get_children())
            try:
                conn = get_conn()
                with conn.cursor() as cur:
                    if filter_text:
                        query = """
                            SELECT id, part_name, part_number
                            FROM inventory_items
                            WHERE part_name LIKE %s
                        """
                        cur.execute(query, (f"%{filter_text}%",))
                    else:
                        cur.execute("SELECT id, part_name, part_number FROM inventory_items")
                    rows = cur.fetchall()
                    for row in rows:
                        tree.insert("", "end", values=row)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                popup.destroy()

        def search_inventory():
            search_term = search_var.get().strip()
            load_inventory(search_term)

        tk.Button(search_frame, text="Search", command=search_inventory).pack(side=tk.LEFT, padx=5)

        # --- Button Frame ---
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def on_select():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select an Item", "Please select an inventory item.")
                return
            values = tree.item(selected[0], "values")
            part_id, part_name, part_number = values

            selected_part["id"] = int(part_id)

            inventory_item_entry.config(state="normal")
            inventory_item_entry.delete(0, tk.END)
            inventory_item_entry.insert(0, part_name)
            inventory_item_entry.config(state="readonly")

            popup.destroy()

        def on_cancel():
            popup.destroy()

        tk.Button(btn_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

        # Initial load of full inventory
        load_inventory()

    # Add the BOM items to the table
    def add_bom_item():
        selected = products_treeview.selection()
        content_dict = products_treeview.item(selected)
        row_data = content_dict['values']

        if selected_part["id"] is None:
            messagebox.showwarning("No Part Selected", "Please select a part using the Search button.")
            return

        try:
            qty = int(item_qty_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be an integer.")
            return

        product_id = row_data[0]
        
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO bill_of_materials (product_id, part_id, quantity_needed)
                    VALUES (%s, %s, %s)
                """, (product_id, selected_part["id"], qty))
                conn.commit()
            refresh_bom_treeview(product_id)  # Call the same logic from `on_tree_select`
            item_qty_entry.delete(0, tk.END)
            inventory_item_entry.config(state="normal")
            inventory_item_entry.delete(0, tk.END)
            inventory_item_entry.config(state="readonly")
            selected_part["id"] = None
        except Exception as e:
            print(e)
            messagebox.showerror("Error", str(e))

    # When a treeview item is selected (Product)
    def on_tree_select(event):
        selected = products_treeview.selection()
        if not selected:
            product_name_entry.delete(0, tk.END)
            product_id_entry.delete(0, tk.END)
            inventory_item_entry.config(state='normal')
            inventory_item_entry.delete(0, tk.END)
            inventory_item_entry.config(state='readonly')
            item_qty_entry.delete(0, tk.END)
            for item in bom_treeview.get_children():
                bom_treeview.delete(item)
            return

        content_dict = products_treeview.item(selected)
        row_data = content_dict['values']

        if len(row_data) < 3:
            return  # Not enough data in row to safely unpack (avoid out-of-range error)

        # Enable form fields
        inventory_item_entry.config(state="readonly")
        item_qty_entry.config(state='normal')
        item_search_button.config(state='normal')
        add_bom_button.config(state='normal')

        # Fill entry fields with product data
        product_name_entry.delete(0, tk.END)
        product_id_entry.delete(0, tk.END)
        product_name_entry.insert(0, row_data[1])
        product_id_entry.insert(0, row_data[2])
        item_category_combobox.set(row_data[3])


        # Refresh BOM Treeview
        try:
            product_id = int(row_data[0])
            refresh_bom_treeview(product_id)
        except ValueError:
            messagebox.showerror("Invalid Data", "Product ID is not an integer.")

    products_treeview.bind("<<TreeviewSelect>>", on_tree_select)

    return products_frame