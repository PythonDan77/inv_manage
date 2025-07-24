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
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=shipping_treeview.xview)
    vertical_scrollbar.config(command=shipping_treeview.yview)
    shipping_treeview.pack(pady= (10, 0))
    
    shipping_treeview.heading('id', text='Build ID')
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

    fulfill_button = tk.Button(button_frame, text='Fulfill', 
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
                                        #    command=lambda:  
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

    return shipping_frame