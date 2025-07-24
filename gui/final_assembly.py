import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

# Used to populate the treeview form with items. It is called after treeview is created.
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                fa.id,
                fa.order_id,
                p.product_name,
                o.customer_name,
                o.po_number,
                o.status,
                fa.notes,
                o.created_at,
                fa.assembly_complete,
                fa.assembler_name,
                fa.packed_at
            FROM final_assembly fa
            JOIN products p ON fa.product_id = p.id
            JOIN orders o ON fa.order_id = o.id
        """)
        all_records = cur.fetchall()
        assy_treeview.delete(*assy_treeview.get_children())
        for record in all_records:
            cleaned_record = [value if value is not None else '' for value in record]
            assy_treeview.insert('', 'end', values=cleaned_record)

def item_assembled(cur_id, user_info):
    result = messagebox.askyesno('Confirm', 'The item is assembled?')
    if result:
        try:
            set_date = datetime.today().strftime('%Y-%m-%d')
            conn = get_conn()
            with conn.cursor() as cur:
                # First update the orders table (status)
                cur.execute("""
                    UPDATE orders SET status = %s WHERE id = (
                        SELECT order_id FROM final_assembly WHERE id = %s
                    )
                """, ("Assembled", cur_id))

                # Then update assembler name and assembly_start in final_assembly
                cur.execute("""
                    UPDATE final_assembly SET assembler_name = %s, assembly_complete = %s WHERE id = %s
                """, (user_info['full_name'], set_date, cur_id))
            conn.commit()
            treeview()
            
            messagebox.showinfo('Success','Marked Assembled Successfully.')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


# Delete the selected row/item.
def delete_item(cur_id):
    result = messagebox.askyesno('Confirm', 'Do you want to delete this build?'
                                 ' The order will need to be re-entered to have it appear here again.')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM final_assembly WHERE id = %s", (cur_id,))
                
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

def update_item(cur_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""UPDATE final_assembly SET notes=%s WHERE id=%s""",
                                (notes_entry.get(),
                                cur_id)
                                )
        conn.commit()
        treeview()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def complete_item(cur_id, user_info):
    result = messagebox.askyesno('Confirm', 'Mark the item packed and ready for shipping? This cannot be undone')
    if result:
        try:
            set_date = datetime.today().strftime('%Y-%m-%d')
            conn = get_conn()
            with conn.cursor() as cur:
                # First update the orders table (status)
                cur.execute("""
                    UPDATE orders SET status = %s WHERE id = (
                        SELECT order_id FROM final_assembly WHERE id = %s
                    )
                """, ("Packed", cur_id))

                # Then update assembler name and assembly_start in final_assembly
                cur.execute("""
                    UPDATE final_assembly SET packed_at = %s WHERE id = %s
                """, (set_date, cur_id))
            conn.commit()
            treeview()

            messagebox.showinfo('Success','Build Completed.')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(user_info, assembled=False, update=False, complete=False, delete=False):
    
    selected = assy_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = assy_treeview.item(selected)
    id_num = data['values'][0]
    status = data['values'][5]
    
    if assembled:
        if status != "Assembled":
            item_assembled(id_num, user_info)
        else:
            messagebox.showerror('Error','This item is already assembled.')
    elif update:
        update_item(id_num)

    elif complete:    
        if status == "Assembled":
            complete_item(id_num, user_info)
        else:
            messagebox.showerror('Error','This build needs to be marked Assembled before it can be Packed.')
    elif delete:
        delete_item(id_num)

# Function verifies data has been used to search the database and then retrieves the data.
def search_item(search_option, value):
    if search_option == 'Select..':
        messagebox.showerror('Error', 'Select an option.')
        return
    if not value:
        messagebox.showerror('Error', 'Enter a value to search.')
        return

    # Map dropdown to actual database fields
    field_map = {
        'ID': 'fa.id',
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
                    fa.id,
                    fa.order_id,
                    p.product_name,
                    o.customer_name,
                    o.po_number,
                    o.status,
                    fa.notes,
                    o.created_at,
                    fa.assembly_complete,
                    fa.assembler_name,
                    fa.packed_at
                FROM 
                    final_assembly fa
                JOIN 
                    products p ON fa.product_id = p.id
                JOIN 
                    orders o ON fa.order_id = o.id
                WHERE 
                    {field_map[search_option]} LIKE %s
            """
            search_term = f"%{value}%" if search_option != "ID" else value
            cur.execute(sql, (search_term,))
            result = cur.fetchall()

            assy_treeview.delete(*assy_treeview.get_children())
            for record in result:
                assy_treeview.insert('', 'end', values=record)

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

def final_assy_frame(parent, user_info):
    global assy_treeview
    global notes_entry

    final_assy_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    final_assy_frame.place(x=201, y=100)

    heading_label = tk.Label(final_assy_frame, text='Final Assembly and Packaging Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(final_assy_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:final_assy_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(final_assy_frame, width=1075, height=240, bg='white')
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
    
    assy_treeview = ttk.Treeview(top_frame, columns=('id', 'order_id', 'product_name', 'customer_name', 'po_number',
                                                        'status', 'notes', 'created_at', 'assembly_date', 'assembler', 'packed_on'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=assy_treeview.xview)
    vertical_scrollbar.config(command=assy_treeview.yview)
    assy_treeview.pack(pady= (10, 0))
    
    assy_treeview.heading('id', text='ID')
    assy_treeview.heading('order_id', text='Order ID')
    assy_treeview.heading('product_name', text='Product name')
    assy_treeview.heading('customer_name', text='Customer name')
    assy_treeview.heading('po_number', text='P.O. #')
    assy_treeview.heading('status', text='Status')
    assy_treeview.heading('notes', text='Notes')
    assy_treeview.heading('created_at', text='Ready For Assy')
    assy_treeview.heading('assembly_date', text='Assembled Date')
    assy_treeview.heading('assembler', text='Assembler')
    assy_treeview.heading('packed_on', text='Packed Date')
    
    assy_treeview.column('id', width=80)
    assy_treeview.column('order_id', width=80)
    assy_treeview.column('product_name', width=200)
    assy_treeview.column('customer_name', width=200)
    assy_treeview.column('po_number', width=150)
    assy_treeview.column('status', width=175)
    assy_treeview.column('notes', width=300)
    assy_treeview.column('created_at', width=150)
    assy_treeview.column('assembly_date', width=150)
    assy_treeview.column('assembler', width=150)
    assy_treeview.column('packed_on', width=150)

    #call treeview function to display the items.
    treeview()
    
    #Lower Section of Page
    detail_frame = tk.Frame(final_assy_frame, width=675, height=300, bg='white')
    detail_frame.place(x=0, y=375)

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white')
    notes_label.grid(row=0, column=0, padx=10, pady=(20,0))
    notes_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', width=35)
    notes_entry.grid(row=0, column=1, padx=10, pady=(20,0))
    

    #Lower button Frame
    button_frame= tk.Frame(final_assy_frame, bg='white')
    button_frame.place(x=180, y=550, relwidth=1)

    update_button = tk.Button(button_frame, text='Update Note', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: row_select_check(user_info, update=True)
                                                                  )
    update_button.grid(row=0, column=0, padx=20)

    assembled_button = tk.Button(button_frame, text='Assembled', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(user_info, assembled=True)
                                                                  )
    assembled_button.grid(row=0, column=1, padx=20)

    packed_button = tk.Button(button_frame, text='Packed', 
                                            font=('times new roman', 12), 
                                            bg='red', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(user_info, complete=True)
                                                                )
    packed_button.grid(row=0, column=2, padx=20)
    
    
    # history_button = tk.Button(button_frame, text='History', 
    #                                        font=('times new roman', 12), 
    #                                        bg='#0f4d7d', 
    #                                        fg='white', 
    #                                        width= 10, 
    #                                        cursor='hand2', 
    #                                     #    command=lambda:  
    #                                     )
    # history_button.grid(row=0, column=3, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: row_select_check(user_info, delete=True)  
                                        )
    
    if user_info['role'] in ['manager', 'admin']:
        delete_button.grid(row=0, column=3, padx=20)

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))

    return final_assy_frame