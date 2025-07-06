import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from tkinter import messagebox
import bcrypt

# Used to populate the treeview form with inventory items. It is called after inv_treeview is created in inventory_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT id, username, role, full_name FROM users')
        all_records = cur.fetchall()
        user_treeview.delete(*user_treeview.get_children())
        for record in all_records:
            user_treeview.insert('', 'end', values=record)

# Function used to verify all data in fields is present and of the right type.
def validate_form_inputs(username, password, role, full_name):
    
    if role == "Select..":
        messagebox.showerror('Empty Field', 'Select a user role.')
        return None

    if not username:
        messagebox.showerror('Empty Field', 'Username cannot be empty.')
        return None

    if not full_name:
            messagebox.showerror('Empty Field', 'Full name cannot be empty.')
            return None
    
    if password:
        return (username.strip(),
            password.strip(),
            role.strip(),
            full_name.strip()  
        )
        
    return (username.strip(),
            role.strip(),
            full_name.strip()
        )

# Check to make sure a row is selected to either update or delete.
def row_select_check(username, role, full_name, password=None, re_pass=None, add_button=None, update=False, delete=False):
    
    selected = user_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = user_treeview.item(selected)
    id_num = data['values'][0]
    
    if update:
        add_update_item(username, role, full_name, update=True, cur_id=id_num)
    elif delete:
        delete_item(username, role, full_name, id_num, password, re_pass, add_button)


def password_check(username, role, full_name, password, re_password):
    if not password:
        messagebox.showerror('Empty Field', 'Password cannot be empty.')
        return None

    if not re_password:
        messagebox.showerror('Empty Field', 'Must re-enter password.')
        return None

    if password != re_password:
        messagebox.showerror('Password Error', 'Passwords do not match.')
        return None

    add_update_item(username, role, full_name, password=password)


# When all fields are filled and the add button is pressed, this function adds the items to the database.
def add_update_item(username, role, full_name, password=None, update=False, cur_id=None):

    validated_data = validate_form_inputs(username, password, role, full_name)
    
    if not validated_data:
        return
    else:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                if update:
                    cur.execute('SELECT id, username, role, full_name FROM users WHERE id = %s', (cur_id,))
                    current_db_data = cur.fetchone()
                    if not current_db_data:
                        messagebox.showerror("Error", 'The user does not exist.')
                        return
                    current_db_data = current_db_data[1:]
                    if current_db_data == validated_data:
                        messagebox.showinfo('No Changes','No Changes Detected.')
                        return
                    else:
                        cur.execute("""UPDATE users SET username=%s, 
                                    role=%s,
                                    full_name=%s WHERE id=%s""",
                                    (*validated_data,
                                    cur_id)
                                    )

                        messagebox.showinfo('Success','Update successful.')
                else:

                    cur.execute(
                        """SELECT username, full_name FROM users
                        WHERE username = %s AND full_name = %s
                        """, (validated_data[0], validated_data[3]))
                    
                    if cur.fetchone():
                        messagebox.showerror("Duplicate Error", 'The user already exists.')
                        return

                    else:
                        hashed_pw = bcrypt.hashpw(validated_data[1].encode(), bcrypt.gensalt()).decode()
                        cur.execute(
                            """INSERT INTO users (username, password_hash, role, full_name) VALUES (%s, %s, %s, %s)""",
                            (
                            validated_data[0],
                            hashed_pw,
                            validated_data[2],
                            validated_data[3]
                            )
                        )
                        messagebox.showinfo('Success','Saved Successfully.')
            conn.commit()
            treeview()
        
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Delete the selected row/item.
def delete_item(username, role, full_name, id_num, password, re_pass, add_button):

    result = messagebox.askyesno('Confirm', 'Do you want to delete this record?')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute('DELETE FROM users WHERE id=%s',(id_num,))
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
            clear_fields((username, full_name, password, re_pass), combobox=role, add_button=add_button)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


# Clears data from all fields. Highlighted row is also cleared when the CLEAR button is pressed, but not when called from select_data().
def clear_fields(all_fields, combobox, add_button=None, pass_update_button= None, tab=False):

    for field in all_fields:
        field.delete(0,tk.END)

    combobox.set("Select..")

    if len(all_fields) == 4:
        all_fields[2].config(state="normal")
        all_fields[3].config(state="normal")
    if add_button:
        add_button.config(state="normal")
    if pass_update_button:
        pass_update_button.config(state='disabled')

    if tab:
        user_treeview.selection_remove(user_treeview.selection())

# When a field in treeview is selected, this function collects the data and applies it to all entry fields (all_fields).
def select_data(event, all_fields, combobox, add_button, pass_update_button):

    index = user_treeview.selection()
    if index:
        content_dict = user_treeview.item(index)
        row_data = content_dict['values']

        clear_fields(all_fields, combobox=combobox, add_button=add_button)

        all_fields[2].config(state="disabled")
        all_fields[3].config(state="disabled")
        add_button.config(state="disabled")
        pass_update_button.config(state='normal')

        all_fields[0].insert(0,row_data[1])
        all_fields[1].insert(0,row_data[3])
        combobox.set(row_data[2])

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
                cur.execute(f'SELECT id, username, role, full_name FROM users WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                user_treeview.delete(*user_treeview.get_children())
                for record in result:
                    user_treeview.insert('', 'end', values=record)

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

def password_update(frame, username_entry, full_name_entry, password_entry, 
                    re_password_entry, update_button, delete_button, 
                    clear_button, pass_update_button, role_combobox
                    ):
    
    save_button = cancel_button = None

    def cancel_save():
        password_entry.delete(0,tk.END)
        re_password_entry.delete(0,tk.END)

        username_entry.config(state='normal')
        full_name_entry.config(state='normal')
        role_combobox.config(state='normal')
        update_button.config(state='normal')
        delete_button.config(state='normal')
        clear_button.config(state='normal')
        pass_update_button.config(state='normal')
        password_entry.config(state='disabled')
        re_password_entry.config(state='disabled')
        save_button.destroy()
        cancel_button.destroy()
        
        return


    def save_password():
        selected = user_treeview.selection()
        data = user_treeview.item(selected)
        id_num = data['values'][0]

        new_pw = password_entry.get()
        re_new_pw = re_password_entry.get()

        if not new_pw:
            messagebox.showerror("Error", "Password required.")
            return

        if new_pw != re_new_pw:
            messagebox.showerror('Password Error', 'Passwords do not match.')
            cancel_save()
            return

        try:
            hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, id_num))
                conn.commit()
            messagebox.showinfo("Success", "Password updated.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            cancel_save()   
        
    username_entry.config(state='disabled')
    full_name_entry.config(state='disabled')
    role_combobox.config(state='disabled')
    update_button.config(state='disabled')
    delete_button.config(state='disabled')
    clear_button.config(state='disabled')
    pass_update_button.config(state='disabled')
    password_entry.config(state='normal')
    password_entry.focus()
    re_password_entry.config(state='normal')
    
    save_button = tk.Button(frame, text='Save', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=save_password
                                                                )
    save_button.grid(row=2, column=4, padx=(20,0))

    cancel_button = tk.Button(frame, text='Cancel', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=cancel_save
                                                                )
    cancel_button.grid(row=2, column=5)


def user_frame(parent, user_info):
    global user_treeview

    user_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    user_frame.place(x=201, y=100)

    heading_label = tk.Label(user_frame, text='User Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    
    back_img_user = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(user_frame, image=back_img_user, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:user_frame.place_forget())
    back_button.image = back_img_user
    back_button.place(x=5, y=33)
    
    #Top Section of Page
    top_frame = tk.Frame(user_frame, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Username', 'Role', 'Full name'), 
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

    # horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    user_treeview = ttk.Treeview(top_frame, columns=('id', 'username', 'role', 'full_name'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set)
                                        #    xscrollcommand=horizontal_scrollbar.set)
    # horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    # horizontal_scrollbar.config(command=user_treeview.xview)
    vertical_scrollbar.config(command=user_treeview.yview)
    user_treeview.pack(pady= (10, 0))
    
    user_treeview.heading('id', text='ID')
    user_treeview.heading('username', text='User Name')
    user_treeview.heading('full_name', text='Full Name')
    user_treeview.heading('role', text='Role')
    
    user_treeview.column('id', width=70)
    user_treeview.column('username', width=200)
    user_treeview.column('full_name', width=175)
    user_treeview.column('role', width=150)

    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(user_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)

    username_label = tk.Label(detail_frame, text='Username', font=('times new roman', 10, 'bold'), bg='white')
    username_label.grid(row=0, column=0,padx=10, pady=20)
    username_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    username_entry.grid(row=0, column=1, padx=10, pady=20 )

    full_name_label = tk.Label(detail_frame, text='Full Name', font=('times new roman', 10, 'bold'), bg='white')
    full_name_label.grid(row=0, column=2, padx=10, pady=20)
    full_name_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    full_name_entry.grid(row=0, column=3, padx=10, pady=20)

    password_label = tk.Label(detail_frame, text='Password', font=('times new roman', 10, 'bold'), bg='white')
    password_label.grid(row=0, column=4, padx=10, pady=20)
    password_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', show="*")
    password_entry.grid(row=0, column=5, padx=10, pady=20)

    role_label = tk.Label(detail_frame, text='Role', font=('times new roman', 10, 'bold'), bg='white')
    role_label.grid(row=1, column=0, padx=10, pady=20)
    role_combobox = ttk.Combobox(detail_frame, width=17, values=('employee', 'manager', 'admin'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    role_combobox.set('Select..')
    role_combobox.grid(row=1, column=1, padx=10, pady=20)

    re_password_label = tk.Label(detail_frame, text='Re-Enter Password', font=('times new roman', 10, 'bold'), bg='white')
    re_password_label.grid(row=1, column=4, padx=10, pady=20)
    re_password_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow', show="*")
    re_password_entry.grid(row=1, column=5, padx=10, pady=20)

    #Lower button Frame
    button_frame= tk.Frame(user_frame, bg='white')
    button_frame.place(x=125, y=550, relwidth=1)

    add_button = tk.Button(button_frame, text='Add', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: password_check(username_entry.get(),
                                                                  role_combobox.get(),
                                                                  full_name_entry.get(), 
                                                                  password_entry.get(),
                                                                  re_password_entry.get()
                                                                  )
                                                                  )
    add_button.grid(row=0, column=0, padx=20)

    update_button = tk.Button(button_frame, text='Update', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2', 
                                            command=lambda: row_select_check(username_entry.get(), 
                                                                  role_combobox.get(),
                                                                  full_name_entry.get(),
                                                                  update=True)
                                                                  )
    update_button.grid(row=0, column=1, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=lambda: row_select_check(
                                                                username_entry, 
                                                                role_combobox,
                                                                full_name_entry,
                                                                password=password_entry,
                                                                re_pass=re_password_entry,
                                                                add_button=add_button,
                                                                delete=True)
                                                                )
    delete_button.grid(row=0, column=2, padx=20)
    
    # Clicking the clear button triggers the clear_fields() function and removes all data from the entry fields.
    clear_button = tk.Button(button_frame, text='Clear', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           command=lambda: clear_fields((
                                                                  username_entry, 
                                                                  full_name_entry, 
                                                                  password_entry,
                                                                  re_password_entry
                                                                  ), 
                                                                  add_button=add_button,
                                                                  pass_update_button=pass_update_button,
                                                                  combobox=role_combobox,
                                                                  tab=True)
                                                                  )
    clear_button.grid(row=0, column=3, padx=20)

    pass_update_button = tk.Button(button_frame, text='New Password', 
                                           font=('times new roman', 12), 
                                           bg='#0f4d7d', 
                                           fg='white', 
                                           width= 10, 
                                           cursor='hand2', 
                                           state='disabled',
                                           command=lambda: password_update(
                                                                  detail_frame,
                                                                  username_entry, 
                                                                  full_name_entry, 
                                                                  password_entry,
                                                                  re_password_entry, 
                                                                  update_button,
                                                                  delete_button,
                                                                  clear_button,
                                                                  pass_update_button,
                                                                  role_combobox
                                                                  )
                                                                  )
    pass_update_button.grid(row=0, column=4, padx=20)
    


    # When a field in treeview is clicked, the select_data() function fills the entry fields.
    user_treeview.bind('<ButtonRelease-1>', lambda event: select_data(
                                                            event,
                                                            (username_entry, 
                                                            full_name_entry,
                                                            password_entry,
                                                            re_password_entry),
                                                            role_combobox,
                                                            add_button,
                                                            pass_update_button)
                                                            )

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))
    role_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, role_combobox))

    return user_frame