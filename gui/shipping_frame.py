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
                shipping.id,
                orders.id AS order_id,
                products.product_name,
                orders.customer_name,
                orders.po_number,
                orders.status,
                shipping.notes,
                shipping.shipper,
                shipping.tracking
            FROM shipping
            JOIN orders ON shipping.order_id = orders.id
            JOIN products ON orders.product_id = products.id
            WHERE orders.status = 'Packed'
        """)
        all_records = cur.fetchall()
        shipping_treeview.delete(*shipping_treeview.get_children())
        for record in all_records:
            shipping_treeview.insert('', 'end', values=record)

# History tab that provides access to the table build_history.
def shipping_popup():

    popup = tk.Toplevel(bg='white')
    popup.title("Shipping History")
    popup.geometry("1150x650+400+250")
    popup.transient()  # Keeps it on top
    popup.grab_set()   # Modal behavior

    history_treeview = None

    heading_label = tk.Label(popup, text='Shipping History', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
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
                    cur.execute(f'SELECT * FROM shipping_history WHERE {search_option} LIKE %s', f'%{value}%')
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
    
    history_treeview = ttk.Treeview(top_frame, columns=('id', 'order_id', 'product_name', 'customer_name', 'po_number', 
                                                        'status', 'notes', 'shipper', 'tracking', 
                                                        'shipped_date', 'shipped_by'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=history_treeview.xview)
    vertical_scrollbar.config(command=history_treeview.yview)
    history_treeview.pack(pady= (10, 0))
    
    history_treeview.heading('id', text='History ID')
    history_treeview.heading('order_id', text='Order ID')
    history_treeview.heading('product_name', text='Product_name')
    history_treeview.heading('customer_name', text='Customer name')
    history_treeview.heading('po_number', text='PO #')
    history_treeview.heading('status', text='Status')
    history_treeview.heading('notes', text='Notes')
    history_treeview.heading('shipper', text='Shipper')
    history_treeview.heading('tracking', text='Tracking')
    history_treeview.heading('shipped_date', text='Shipped Date')
    history_treeview.heading('shipped_by', text='Shipped By')
    
    history_treeview.column('id', width=100)
    history_treeview.column('order_id', width=100)
    history_treeview.column('product_name', width=175)
    history_treeview.column('customer_name', width=175)
    history_treeview.column('po_number', width=170)
    history_treeview.column('status', width=150)
    history_treeview.column('notes', width=175)
    history_treeview.column('shipper', width=175)
    history_treeview.column('tracking', width=175)
    history_treeview.column('shipped_date', width=175)
    history_treeview.column('shipped_by', width=175)
    
    def hist_treeview():
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM shipping_history"""
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
                cur.execute("SELECT * FROM shipping_history")
                rows = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]

            if not rows:
                messagebox.showinfo("Export", "No data in shipping history.")
                return

            # Default filename
            default_filename = f"shipping_history_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

            # Path to user's Desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            # Ask where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                initialdir=desktop_path,
                title="Save Shipping History As"
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

# Delete the selected row/item.
def delete_item(cur_id):
    result = messagebox.askyesno('Confirm', 'Do you want to delete this build?'
                                 ' The order will need to be re-entered to have it appear here again.')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM shipping WHERE id = %s", (cur_id,))
                
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

def update_item(cur_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""UPDATE shipping SET notes=%s WHERE id=%s""",
                                (notes_entry.get(),
                                cur_id)
                                )
        conn.commit()
        treeview()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(user_info, assembled=False, update=False, complete=False, delete=False):
    
    selected = shipping_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = shipping_treeview.item(selected)
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

def shipping_frame(parent, user_info):
    global shipping_treeview
    global notes_entry

    shipping_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    shipping_frame.place(x=201, y=100)

    heading_label = tk.Label(shipping_frame, text='Shipping Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(shipping_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:shipping_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(shipping_frame, width=1075, height=240, bg='white')
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
    
    shipping_treeview = ttk.Treeview(top_frame, columns=('id','order_id', 'product_name', 'customer_name', 'po_number',
                                                        'status', 'notes', 'shipper', 'tracking'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set,
                                           selectmode="extended")
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=shipping_treeview.xview)
    vertical_scrollbar.config(command=shipping_treeview.yview)
    shipping_treeview.pack(pady= (10, 0))
    
    shipping_treeview.heading('id', text='Ship ID')
    shipping_treeview.heading('order_id', text='Order ID')
    shipping_treeview.heading('product_name', text='Product name')
    shipping_treeview.heading('customer_name', text='Customer name')
    shipping_treeview.heading('po_number', text='P.O. #')
    shipping_treeview.heading('status', text='Status')
    shipping_treeview.heading('notes', text='Notes')
    shipping_treeview.heading('shipper', text='Courier')
    shipping_treeview.heading('tracking', text='Tracking')
    
    shipping_treeview.column('id', width=80)
    shipping_treeview.column('order_id', width=80)
    shipping_treeview.column('product_name', width=200)
    shipping_treeview.column('customer_name', width=200)
    shipping_treeview.column('po_number', width=150)
    shipping_treeview.column('status', width=150)
    shipping_treeview.column('notes', width=300)
    shipping_treeview.column('shipper', width=175)
    shipping_treeview.column('tracking', width=175)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(shipping_frame, width=675, height=300, bg='white')
    detail_frame.place(x=0, y=375)

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white')
    notes_label.grid(row=0, column=0, padx=10, pady=(20,0))
    notes_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', width=35)
    notes_entry.grid(row=0, column=1, padx=10, pady=(20,0))

    courier_label = tk.Label(detail_frame, text='Courier', font=('times new roman', 10, 'bold'), bg='white')
    courier_label.grid(row=0, column=2, padx=10, pady=(20,0))
    courier_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    courier_entry.grid(row=0, column=3, padx=10, pady=(20,0))

    tracking_label = tk.Label(detail_frame, text='Tracking', font=('times new roman', 10, 'bold'), bg='white')
    tracking_label.grid(row=0, column=4, padx=10, pady=(20,0))
    tracking_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    tracking_entry.grid(row=0, column=5, padx=10, pady=(20,0))

    button_frame= tk.Frame(shipping_frame, bg='white')
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

    fulfill_button = tk.Button(button_frame, text='Pedal Fulfill', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(user_info, complete=True)
                                                                )
    fulfill_button.grid(row=0, column=1, padx=20)

    shipped_button = tk.Button(button_frame, text='Mark Shipped', 
                                            font=('times new roman', 12), 
                                            bg='red', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(user_info, complete=True)
                                                                )
    shipped_button.grid(row=0, column=2, padx=20)
    
    
    history_button = tk.Button(button_frame, text='History', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda:shipping_popup()
                                        )
    history_button.grid(row=0, column=3, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: row_select_check(user_info, delete=True)  
                                        )


    if user_info['role'] in ['manager', 'admin']:
        delete_button.grid(row=0, column=4, padx=20)

    def on_shipping_select(event):
        selected = shipping_treeview.selection()
        if selected:
            content_dict = shipping_treeview.item(selected[0])
            row_data = content_dict['values']
            
            notes_entry.delete(0,tk.END)   
            notes_entry.insert(0,row_data[6])
            courier_entry.delete(0,tk.END)   
            courier_entry.insert(0,row_data[7])
            tracking_entry.delete(0,tk.END)   
            tracking_entry.insert(0,row_data[8])

    shipping_treeview.bind("<<TreeviewSelect>>", on_shipping_select)

    return shipping_frame