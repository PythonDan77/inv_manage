import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

# Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM amplifier_builds')
        all_records = cur.fetchall()
        amp_treeview.delete(*amp_treeview.get_children())
        for record in all_records:
            amp_treeview.insert('', 'end', values=record)

def update_customizations_display(order_id, customizations_text):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT option_name, option_value
                FROM order_customizations
                WHERE order_id = %s
            """, (order_id,))
            rows = cur.fetchall()
    except Exception as e:
        rows = []
        print("DB Error:", e)

    # Clear and prepare to insert new content
    customizations_text.config(state='normal')
    customizations_text.delete("1.0", tk.END)

    if rows:
        for name, value in rows:
            start_index = customizations_text.index(tk.INSERT)
            customizations_text.insert(tk.END, f"{name}: ")
            end_index = customizations_text.index(tk.INSERT)
            customizations_text.tag_add("bold", start_index, end_index)
            customizations_text.insert(tk.END, f"{value}\n")
    else:
        customizations_text.insert(tk.END, "No customizations.")

    customizations_text.config(state='disabled')

def amplifier_frame(parent, user_info):
    global amp_treeview

    amplifier_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    amplifier_frame.place(x=201, y=100)

    heading_label = tk.Label(amplifier_frame, text='Amplifier Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(amplifier_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:amplifier_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(amplifier_frame, width=1075, height=240, bg='white')
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

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    amp_treeview = ttk.Treeview(top_frame, columns=('id','order_id', 'product_name', 'customer_name', 'po_number', 'voltage',
                                                        'status', 'builder_name', 'serial_number', 'notes', 'created_at',
                                                     'completed_at'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=amp_treeview.xview)
    vertical_scrollbar.config(command=amp_treeview.yview)
    amp_treeview.pack(pady= (10, 0))
    
    amp_treeview.heading('id', text='Build ID')
    amp_treeview.heading('order_id', text='Order ID')
    amp_treeview.heading('product_name', text='Product name')
    amp_treeview.heading('customer_name', text='Customer name')
    amp_treeview.heading('po_number', text='P.O. #')
    amp_treeview.heading('voltage', text='Voltage')
    amp_treeview.heading('status', text='Status')
    amp_treeview.heading('builder_name', text='Builder')
    amp_treeview.heading('notes', text='Notes')
    amp_treeview.heading('created_at', text='Date created')
    amp_treeview.heading('serial_number', text='Serial Number')
    amp_treeview.heading('completed_at', text='Completion date')
    
    amp_treeview.column('id', width=80)
    amp_treeview.column('order_id', width=80)
    amp_treeview.column('product_name', width=200)
    amp_treeview.column('customer_name', width=200)
    amp_treeview.column('po_number', width=150)
    amp_treeview.column('voltage', width=120)
    amp_treeview.column('status', width=150)
    amp_treeview.column('builder_name', width=175)
    amp_treeview.column('notes', width=300)
    amp_treeview.column('created_at', width=150)
    amp_treeview.column('serial_number', width=190)
    amp_treeview.column('completed_at', width=150)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(amplifier_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    status_label = tk.Label(detail_frame, text='Status', font=('times new roman', 10, 'bold'), bg='white')
    status_label.grid(row=0, column=0, padx=20, pady=(20,0))
    status_combobox = ttk.Combobox(detail_frame, width=17, values=('In Progress','Paused', 'Complete'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    status_combobox.set('Select..')
    status_combobox.grid(row=0, column=1, padx=10, pady=(20,0))

    serial_number_label = tk.Label(detail_frame, text='Serial Number', font=('times new roman', 10, 'bold'), bg='white')
    serial_number_label.grid(row=0, column=2,padx=10, pady=(20,0))
    serial_number_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    serial_number_entry.grid(row=0, column=3, padx=10, pady=(20,0))

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white')
    notes_label.grid(row=0, column=4, padx=10, pady=(20,0))
    notes_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', width=35)
    notes_entry.grid(row=0, column=5, padx=10, pady=(20,0))

    customizations_label = tk.Label(detail_frame, text="Custom", font=('times new roman', 10, 'bold'), bg='white')
    customizations_label.grid(row=1, column=0, padx=(10,0),pady=(20,0))

    customizations_text = tk.Text(detail_frame, width=30, height=4, wrap='word')
    customizations_text.tag_configure("bold", font=("Arial", 10, "bold"))
    customizations_text.config(state='disabled')
    customizations_text.grid(row=1, column=1, padx=(10,0),pady=(20,0))

    #Lower button Frame
    button_frame= tk.Frame(amplifier_frame, bg='white')
    button_frame.place(x=180, y=550, relwidth=1)

    claim_button = tk.Button(button_frame, text='Claim', 
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
                                        #                           restock_qty_entry.get(),
                                        #                           item_type_combobox.get(),
                                        #                           item_category_combobox.get())
                                                                  )
    claim_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(part_name_entry.get(), 
                                                                  part_num_entry.get(), 
                                                                  qty_entry.get(), 
                                                                  loc_entry.get(), 
                                                                  sup_entry.get(),
                                                                  low_entry.get(),
                                                                  restock_qty_entry.get(),
                                                                  item_type_combobox.get(),
                                                                  item_category_combobox.get(),
                                                                  update=True)
                                                                  )
    update_button.grid(row=0, column=1, padx=20)

    release_button = tk.Button(button_frame, text='Release', 
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
                                                                item_category_combobox,
                                                                delete=True)
                                                                )
    release_button.grid(row=0, column=2, padx=20)
    
    # Clicking the clear button triggers the clear_fields() function and removes all data from the entry fields.
    history_button = tk.Button(button_frame, text='History', 
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
                                                                  combobox1=item_type_combobox,
                                                                  combobox2=item_category_combobox,
                                                                  tab=True)
                                                                  )
    history_button.grid(row=0, column=3, padx=20)

    def on_amplifier_select(event):
        selected = amp_treeview.selection()
        if selected:
            content_dict = amp_treeview.item(selected[0])
            row_data = content_dict['values']
            order_id = row_data[1]  # assuming first column is order_id
            update_customizations_display(order_id, customizations_text)


    amp_treeview.bind("<<TreeviewSelect>>", on_amplifier_select)

    return amplifier_frame