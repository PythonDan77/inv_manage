import os
import tkinter as tk
from tkinter import ttk

def asset_path(filename:str) -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "assets" , filename)

def inventory_frame(parent):

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
    
    inv_treeview = ttk.Treeview(top_frame, columns=('Part Name', 'Part Number', 'Quantity', 'Location','Supplier', 'Supplier Contact', 'Low Limit', 'Last Receive Date', 'Last Receive Qty'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=inv_treeview.xview)
    vertical_scrollbar.config(command=inv_treeview.yview)
    inv_treeview.pack(pady= (10, 0))

    inv_treeview.heading('Part Name', text='Part Name')
    inv_treeview.heading('Part Number', text='Part Number')
    inv_treeview.heading('Quantity', text='Quantity')
    inv_treeview.heading('Location', text='Location')
    inv_treeview.heading('Supplier', text='Supplier')
    inv_treeview.heading('Supplier Contact', text='Supplier Contact')
    inv_treeview.heading('Low Limit', text='Low Limit')
    inv_treeview.heading('Last Receive Date', text='LRD')
    inv_treeview.heading('Last Receive Qty', text='LRQ')

    inv_treeview.column('Part Name', width=120)
    inv_treeview.column('Part Number', width=120)
    inv_treeview.column('Quantity', width=100)
    inv_treeview.column('Location', width=100)
    inv_treeview.column('Supplier', width=120)
    inv_treeview.column('Supplier Contact', width=150)
    inv_treeview.column('Low Limit', width=100)
    inv_treeview.column('Last Receive Date', width=120)
    inv_treeview.column('Last Receive Qty', width=100)
    
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

    add_button = tk.Button(button_frame, text='Add', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    add_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    update_button.grid(row=0, column=1, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    delete_button.grid(row=0, column=2, padx=20)

    clear_button = tk.Button(button_frame, text='Clear', font=('times new roman', 12), bg='#0f4d7d', fg='white', width= 10, cursor='hand2')
    clear_button.grid(row=0, column=3, padx=20)


    return inv_frame
