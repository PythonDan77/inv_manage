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
            if name in ['Tubes', 'Knobs', 'Chassis']:
                start_index = customizations_text.index(tk.INSERT)
                customizations_text.insert(tk.END, f"{name}: ")
                end_index = customizations_text.index(tk.INSERT)
                customizations_text.tag_add("bold", start_index, end_index)
                customizations_text.insert(tk.END, f"{value}\n")
    else:
        customizations_text.insert(tk.END, "No customizations.")

    customizations_text.config(state='disabled')

def start_item(cur_id, user_info):
    result = messagebox.askyesno('Confirm', 'Do you want to start this build?')
    if result:
        try:
            set_date = datetime.today().strftime('%Y-%m-%d')
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""UPDATE amplifier_builds SET status=%s, builder_name=%s,
                                    build_start=%s WHERE id=%s""",
                                    ("In Progress", user_info['full_name'], set_date,
                                    cur_id)
                                    )
            conn.commit()
            treeview()

            status_combobox.set("In Progress")
            
            messagebox.showinfo('Success','Build Started Successfully.')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

def complete_item(cur_id):
    result = messagebox.askyesno('Confirm', 'Mark complete? This cannot be undone')
    if result:
        try:
            set_date = datetime.today().strftime('%Y-%m-%d')
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""UPDATE amplifier_builds SET status=%s, 
                                    completed_at=%s WHERE id=%s""",
                                    ("Completed", set_date,
                                    cur_id)
                                    )
            conn.commit()
            treeview()

            status_combobox.set("Completed")

            messagebox.showinfo('Success','Build Completed.')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

def update_item(cur_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""UPDATE amplifier_builds SET status=%s, serial_number=%s, notes=%s WHERE id=%s""",
                                (status_combobox.get(), serial_number_entry.get(), notes_entry.get(),
                                cur_id)
                                )
        conn.commit()
        treeview()
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
                cur.execute("DELETE FROM amplifier_builds WHERE id = %s", (cur_id,))
                
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
           
            status_combobox.set("Select..")
            serial_number_entry.delete(0,tk.END)
            notes_entry.delete(0, tk.END)
            customizations_text.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(user_info, start=False, update=False, complete=False, delete=False):
    
    selected = amp_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = amp_treeview.item(selected)
    id_num = data['values'][0]
    status = data['values'][6]

    if start:
        if status == "Pending":
            start_item(id_num, user_info)
        else:
            messagebox.showerror('Error','This build has already started or is completed.')
    elif update:
        if data['values'][7]:
            update_item(id_num)
        else:
            messagebox.showerror('Error','A build must be claimed by a builder to update fields.')
    elif complete:
        if serial_number_entry.get():
            if status == "In Progress":
                complete_item(id_num)
            else:
                messagebox.showerror('Error','This build hasn\'t started, needs repair, or is completed. Must be marked "In Progress" to complete.')
        else:
             messagebox.showerror('Error','A build cannot be marked "Completed" without a Serial Number.')
    elif delete:
        delete_item(id_num)

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
                cur.execute(f'SELECT * FROM amplifier_builds WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                amp_treeview.delete(*amp_treeview.get_children())
                for record in result:
                    amp_treeview.insert('', 'end', values=record)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Reloads all data and resets the search options.
def search_all(search_entry, search_combobox):
    treeview()
    search_entry.delete(0,'end')
    search_combobox.set('Select...')

# Clear the highlight from the combobox. Trigger in the main function at the bottom.
def on_select(event, combobox):
    combobox.selection_clear()

def amplifier_frame(parent, user_info):
    global amp_treeview
    global status_combobox
    global serial_number_entry
    global notes_entry
    global customizations_text 

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
                                                        'status', 'builder_name', 'serial_number', 'notes', 'created_at', 'build_start',
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
    amp_treeview.heading('serial_number', text='Serial Number')
    amp_treeview.heading('notes', text='Notes')
    amp_treeview.heading('created_at', text='Order date')
    amp_treeview.heading('build_start', text='Start date')
    amp_treeview.heading('completed_at', text='Completion date')
    
    amp_treeview.column('id', width=80)
    amp_treeview.column('order_id', width=80)
    amp_treeview.column('product_name', width=200)
    amp_treeview.column('customer_name', width=200)
    amp_treeview.column('po_number', width=150)
    amp_treeview.column('voltage', width=120)
    amp_treeview.column('status', width=150)
    amp_treeview.column('builder_name', width=175)
    amp_treeview.column('serial_number', width=190)
    amp_treeview.column('notes', width=300)
    amp_treeview.column('created_at', width=150)
    amp_treeview.column('build_start', width=150)
    amp_treeview.column('completed_at', width=150)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(amplifier_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    status_label = tk.Label(detail_frame, text='Status', font=('times new roman', 10, 'bold'), bg='white')
    status_label.grid(row=0, column=0, padx=20, pady=(20,0))
    status_combobox = ttk.Combobox(detail_frame, width=17, values=('In Progress','Needs Repair'),
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

    customizations_text = tk.Text(detail_frame, width=30, height=6, wrap='word')
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
                                         command=lambda: row_select_check(user_info, start=True)
                                                                  )
    claim_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(user_info, update=True)
                                                                  )
    update_button.grid(row=0, column=1, padx=20)

    completed_button = tk.Button(button_frame, text='Completed', 
                                            font=('times new roman', 12), 
                                            bg='red', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(user_info, complete=True)
                                                                )
    completed_button.grid(row=0, column=2, padx=20)
    
    
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
    

    def on_amplifier_select(event):
        selected = amp_treeview.selection()
        if selected:
            content_dict = amp_treeview.item(selected[0])
            row_data = content_dict['values']
            order_id = row_data[1]  # assuming first column is order_id
            update_customizations_display(order_id, customizations_text)

            status_combobox.set(row_data[6])
            serial_number_entry.delete(0,tk.END)
            notes_entry.delete(0,tk.END)
            serial_number_entry.insert(0,row_data[8])
            notes_entry.insert(0,row_data[9])



    amp_treeview.bind("<<TreeviewSelect>>", on_amplifier_select)

    #Disable certain buttons if user permissions are not adequate
    if user_info['role'] in ['manager', 'admin']:
        delete_button.grid(row=0, column=4, padx=20)

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))
    status_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, status_combobox))

    return amplifier_frame