import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from datetime import datetime
from tkinter import messagebox

def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM cabinet_builds')
        all_records = cur.fetchall()
        cab_treeview.delete(*cab_treeview.get_children())
        for record in all_records:
            cab_treeview.insert('', 'end', values=record)

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
        messagebox.showerror("Database Error", str(e))

    # Clear and prepare to insert new content
    customizations_text.config(state='normal')
    customizations_text.delete("1.0", tk.END)

    if rows:
        for name, value in rows:
            if name in ['Tolex', 'Corners', 'Handle', 'Faceplate', 'Piping', 'Speakers', 'Grill_Cloth']:
                start_index = customizations_text.index(tk.INSERT)
                customizations_text.insert(tk.END, f"{name}: ")
                end_index = customizations_text.index(tk.INSERT)
                customizations_text.tag_add("bold", start_index, end_index)
                customizations_text.insert(tk.END, f"{value}\n")
    else:
        customizations_text.insert(tk.END, "No customizations.")

    customizations_text.config(state='disabled')

def start_item(cur_id):
    result = messagebox.askyesno('Confirm', 'Do you want to start this build?')
    if result:
        try:
            set_date = datetime.today().strftime('%Y-%m-%d')
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""UPDATE cabinet_builds SET status=%s, 
                                    build_start=%s WHERE id=%s""",
                                    ("In Progress", set_date,
                                    cur_id)
                                    )
            conn.commit()
            treeview()

            status_entry.config(state="normal")
            status_entry.delete(0,tk.END)
            status_entry.insert(0,"In Progress")
            status_entry.config(state="readonly")

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
                cur.execute("""UPDATE cabinet_builds SET status=%s, 
                                    completed_at=%s WHERE id=%s""",
                                    ("Completed", set_date,
                                    cur_id)
                                    )
            conn.commit()
            treeview()

            status_entry.config(state="normal")
            status_entry.delete(0,tk.END)
            status_entry.insert(0,"Completed")
            status_entry.config(state="readonly")

            messagebox.showinfo('Success','Build Completed.')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

def update_item(cur_id):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""UPDATE cabinet_builds SET notes=%s WHERE id=%s""",
                                (notes_entry.get(),
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
                cur.execute("DELETE FROM cabinet_builds WHERE id = %s", (cur_id,))
                
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
           
            status_entry.config(state="normal")
            status_entry.delete(0,tk.END)
            status_entry.config(state="readonly")
            notes_entry.delete(0, tk.END)
            customizations_text.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(start=False, update=False, complete=False, delete=False):
    
    selected = cab_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = cab_treeview.item(selected)
    id_num = data['values'][0]
    status = data['values'][5]

    if start:
        if status == "Pending":
            start_item(id_num)
        else:
            messagebox.showerror('Error','This build has already started or is completed.')
    elif update:
        update_item(id_num)
    elif complete:
        if status == "In Progress":
            complete_item(id_num)
        else:
            messagebox.showerror('Error','This build has not yet started or is completed.')
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
                cur.execute(f'SELECT * FROM cabinet_builds WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                cab_treeview.delete(*cab_treeview.get_children())
                for record in result:
                    cab_treeview.insert('', 'end', values=record)

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

def cabinet_frame(parent, user_info):
    global cab_treeview
    global status_entry
    global notes_entry
    global customizations_text

    cabinet_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    cabinet_frame.place(x=201, y=100)

    heading_label = tk.Label(cabinet_frame, text='Cabinet Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_inv = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(cabinet_frame, image=back_img_inv, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:cabinet_frame.place_forget())
    back_button.image = back_img_inv
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(cabinet_frame, width=1075, height=240, bg='white')
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
    
    cab_treeview = ttk.Treeview(top_frame, columns=('id','order_id', 'product_name', 'customer_name', 'po_number',
                                                        'status', 'notes', 'created_at', 'build_start', 'completed_at'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=cab_treeview.xview)
    vertical_scrollbar.config(command=cab_treeview.yview)
    cab_treeview.pack(pady= (10, 0))
    
    cab_treeview.heading('id', text='Build ID')
    cab_treeview.heading('order_id', text='Order ID')
    cab_treeview.heading('product_name', text='Product name')
    cab_treeview.heading('customer_name', text='Customer name')
    cab_treeview.heading('po_number', text='P.O. #')
    cab_treeview.heading('status', text='Status')
    cab_treeview.heading('notes', text='Notes')
    cab_treeview.heading('created_at', text='Order date')
    cab_treeview.heading('build_start', text='Start date')
    cab_treeview.heading('completed_at', text='Completion date')
    
    cab_treeview.column('id', width=80)
    cab_treeview.column('order_id', width=80)
    cab_treeview.column('product_name', width=200)
    cab_treeview.column('customer_name', width=200)
    cab_treeview.column('po_number', width=150)
    cab_treeview.column('status', width=150)
    cab_treeview.column('notes', width=300)
    cab_treeview.column('created_at', width=150)
    cab_treeview.column('build_start', width=150)
    cab_treeview.column('completed_at', width=150)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(cabinet_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    customizations_label = tk.Label(detail_frame, text="Custom", font=('times new roman', 10, 'bold'), bg='white')
    customizations_label.grid(row=0, column=0, padx=(30,0),pady=(30,0))

    customizations_text = tk.Text(detail_frame, width=30, height=10, wrap='word')
    customizations_text.tag_configure("bold", font=("Arial", 10, "bold"))
    customizations_text.config(state='disabled')
    customizations_text.grid(row=0, column=1, padx=(20,0),pady=(5,0))

    status_label = tk.Label(detail_frame, text='Status', font=('times new roman', 10, 'bold'), bg='white')
    status_label.grid(row=0, column=2, padx=20, pady=(20,0))
    
    status_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', state="readonly")
    status_entry.grid(row=0, column=3, padx=10, pady=(20,0))

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white')
    notes_label.grid(row=0, column=4, padx=10, pady=(20,0))
    notes_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', width=35)
    notes_entry.grid(row=0, column=5, padx=10, pady=(20,0))

    

    #Lower button Frame
    button_frame= tk.Frame(cabinet_frame, bg='white')
    button_frame.place(x=180, y=550, relwidth=1)

    start_button = tk.Button(button_frame, text='Start Build', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: row_select_check(start=True)
                                        )
    start_button.grid(row=0, column=0, padx=20)

    completed_button = tk.Button(button_frame, text='Completed', 
                                            font=('times new roman', 12), 
                                            bg='red', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(complete=True)
                                                                )
    completed_button.grid(row=0, column=1, padx=20)
    
    update_button = tk.Button(button_frame, text='Update Notes', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: row_select_check(update=True)
                                                                  )
    update_button.grid(row=0, column=2, padx=20)

    history_button = tk.Button(button_frame, text='History', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                        #    command=lambda: row_select_check(complete=True)
                                                                  )
    history_button.grid(row=0, column=3, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: row_select_check(delete=True)
                                                                  )
    

    def on_cabinet_select(event):
        selected = cab_treeview.selection()
        if selected:
            content_dict = cab_treeview.item(selected[0])
            row_data = content_dict['values']
            order_id = row_data[1]  # assuming first column is order_id
            update_customizations_display(order_id, customizations_text)

            status_entry.config(state="normal")
            status_entry.delete(0,tk.END)
            status_entry.insert(0,row_data[5])
            status_entry.config(state="readonly")

            notes_entry.delete(0,tk.END)
            notes_entry.insert(0,row_data[6])


    cab_treeview.bind("<<TreeviewSelect>>", on_cabinet_select)
    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))

    #Disable certain buttons if user permissions are not adequate
    if user_info['role'] in ['manager', 'admin']:
        delete_button.grid(row=0, column=4, padx=20)

    return cabinet_frame