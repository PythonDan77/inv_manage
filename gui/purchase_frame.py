import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from tkinter import messagebox
from datetime import datetime

# def ensure_table_exists():
#     conn = get_conn()
#     with conn.cursor() as cur:
#         cur.execute(
#             """CREATE TABLE IF NOT EXISTS purchase_requests (
#                     id INT PRIMARY KEY AUTO_INCREMENT,
#                     part_id INT,
#                     order_quantity INT,
#                     requested_by VARCHAR(50), 
#                     status ENUM('requested', 'approved', 'ordered', 'received') DEFAULT 'requested',
#                     request_date VARCHAR(20),
#                     notes VARCHAR(150),
#                     FOREIGN KEY (part_id) REFERENCES inventory_items(id)
#                    )"""
#         )

# ensure_table_exists()

# Used to populate the treeview form with orders. It is called after purchase_treeview is created in purchase_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT
                pr.id,
                pr.part_id,
                i.part_name,
                i.part_number,
                pr.order_quantity,
                pr.requested_by,
                pr.status,
                pr.request_date,
                pr.notes
            FROM purchase_requests pr
            JOIN inventory_items i ON pr.part_id = i.id
            ORDER BY pr.request_date DESC;"""
        )
        all_records = cur.fetchall()
        purchase_treeview.delete(*purchase_treeview.get_children())
        for record in all_records:
            purchase_treeview.insert('', 'end', values=record)

def purchase_frame(parent):
    global purchase_treeview

    purchase_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    purchase_frame.place(x=201, y=100)
    
    heading_label = tk.Label(purchase_frame, text='Purchasing Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_img_purchase = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(purchase_frame, image=back_img_purchase,
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:purchase_frame.place_forget())
    back_button.image = back_img_purchase
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(purchase_frame, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Part ID', 'Part name', 'Part number', 'Supplier'), 
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
                                            # command= lambda: search_item(search_combobox.get(),search_entry.get())
                                            )
    search_button.grid(row=0, column=2, padx=20)

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 10, 
                                          cursor='hand2',
                                        #   command= lambda: search_all(search_entry, search_combobox)
                                          )
    show_button.grid(row=0, column=3)

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    purchase_treeview = ttk.Treeview(top_frame, columns=('id', 'part_id', 'part_name', 'part_number', 'order_quantity', 'requested_by', 'status','request_date', 'notes'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=purchase_treeview.xview)
    vertical_scrollbar.config(command=purchase_treeview.yview)
    purchase_treeview.pack(pady= (10, 0))
    
    purchase_treeview.heading('id', text='Order ID')
    purchase_treeview.heading('part_id', text='Part ID')
    purchase_treeview.heading('part_name', text='Part name')
    purchase_treeview.heading('part_number', text='Part number')
    purchase_treeview.heading('order_quantity', text='Order QTY')
    purchase_treeview.heading('requested_by', text='Requested by')
    purchase_treeview.heading('status', text='Status')
    purchase_treeview.heading('request_date', text='Date Requested')
    purchase_treeview.heading('notes', text='Notes')
  
    
    purchase_treeview.column('id', width=100)
    purchase_treeview.column('part_id', width=100)
    purchase_treeview.column('part_name', width=200)
    purchase_treeview.column('part_number', width=175)
    purchase_treeview.column('order_quantity', width=100)
    purchase_treeview.column('requested_by', width=150)
    purchase_treeview.column('status', width=175)
    purchase_treeview.column('request_date', width=150)
    purchase_treeview.column('notes', width=300)
    
    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(purchase_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)
    
    part_id_label = tk.Label(detail_frame,text='Part ID', font=('times new roman', 10, 'bold'), bg='white', anchor='w')
    part_id_label.grid(row=0, column=0,padx=(20,10), pady=(20,0))
    part_id_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    part_id_entry.grid(row=0, column=1, padx=15, pady=(20,0))

    order_qty_label = tk.Label(detail_frame,text='Qty Request', font=('times new roman', 10, 'bold'), bg='white', anchor='w')
    order_qty_label.grid(row=0, column=2,padx=(10,10), pady=(20,0))
    order_qty_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    order_qty_entry.grid(row=0, column=3, padx=15, pady=(20,0))

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white', anchor='w')
    notes_label.grid(row=0, column=4,padx=(10,10), pady=(20,0))
    notes_entry = tk.Entry(detail_frame, width=30, font=('times new roman', 11), bg='lightyellow')
    notes_entry.grid(row=0, column=5, padx=15, pady=(20,0))
    
    #Lower button Frame
    button_frame= tk.Frame(purchase_frame, bg='white')
    button_frame.place(x=110, y=550, relwidth=1)

    create_button = tk.Button(button_frame, text='Create', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                        #  command=lambda: add_update_item(part_name_entry.get(), 
                                        #                           part_num_entry.get(), 
                                        #                           qty_entry.get(), 
                                        #                           loc_entry.get(), 
                                        #                           sup_entry.get(), 
                                        #                           low_entry.get(),
                                        #                           item_type_combobox.get())
                                                                  )
    create_button.grid(row=0, column=0, padx=20)

    purchased_button = tk.Button(button_frame, text='Purchased', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                        #  command=lambda: add_update_item(part_name_entry.get(), 
                                        #                           part_num_entry.get(), 
                                        #                           qty_entry.get(), 
                                        #                           loc_entry.get(), 
                                        #                           sup_entry.get(), 
                                        #                           low_entry.get(),
                                        #                           item_type_combobox.get())
                                                                  )
    purchased_button.grid(row=0, column=1, padx=20)

    received_button = tk.Button(button_frame, text='Received', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                        #  command=lambda: add_update_item(part_name_entry.get(), 
                                        #                           part_num_entry.get(), 
                                        #                           qty_entry.get(), 
                                        #                           loc_entry.get(), 
                                        #                           sup_entry.get(), 
                                        #                           low_entry.get(),
                                        #                           item_type_combobox.get())
                                                                  )
    received_button.grid(row=0, column=2, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                        #  command=lambda: add_update_item(part_name_entry.get(), 
                                        #                           part_num_entry.get(), 
                                        #                           qty_entry.get(), 
                                        #                           loc_entry.get(), 
                                        #                           sup_entry.get(), 
                                        #                           low_entry.get(),
                                        #                           item_type_combobox.get())
                                                                  )
    delete_button.grid(row=0, column=3, padx=20)

    history_button = tk.Button(button_frame, text='History', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                        #  command=lambda: add_update_item(part_name_entry.get(), 
                                        #                           part_num_entry.get(), 
                                        #                           qty_entry.get(), 
                                        #                           loc_entry.get(), 
                                        #                           sup_entry.get(), 
                                        #                           low_entry.get(),
                                        #                           item_type_combobox.get())
                                                                  )
    history_button.grid(row=0, column=4, padx=20)


    return purchase_frame