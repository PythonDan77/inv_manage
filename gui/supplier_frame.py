import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from tkinter import messagebox

# When first run, verify the table exists in the MYSQL db
def ensure_table_exists():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS supplier_list (
                   id INT PRIMARY KEY AUTO_INCREMENT, 
                   name VARCHAR(40), 
                   contact VARCHAR(20),
                   phone_number VARCHAR(20), 
                   email VARCHAR(30),
                   country VARCHAR(20),
                   address VARCHAR(50)   
                   )"""
        )

ensure_table_exists()

def supplier_frame(parent):
    # Main Frame Code
    supplier_frame = tk.Frame(parent, width=1075, height=650, bg='white')
    supplier_frame.place(x=226, y=100)

    heading_label = tk.Label(supplier_frame, text='Supplier Detail', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_img_supplier = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(supplier_frame, image=back_img_supplier, 
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:supplier_frame.place_forget())
    back_button.image = back_img_supplier
    back_button.place(x=5, y=33)

    #Left Frame Code
    left_frame = tk.Frame(supplier_frame, width=537, height=600, bg='white')
    left_frame.place(x=0, y=75)
    left_frame.grid_propagate(False)

    name_label = tk.Label(left_frame, text="Company Name",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    name_label.grid(row=0, column=0, padx=(20,0), pady=(60,0))
    name_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    name_entry.grid(row=0, column=1, padx=(15,0), pady=(60,0))

    contact_label = tk.Label(left_frame, text="Contact Name",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    contact_label.grid(row=1, column=0, padx=(20,0), pady=(20,0))
    contact_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    contact_entry.grid(row=1, column=1, padx=(15,0), pady=(20,0))

    phone_label = tk.Label(left_frame, text="Phone",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    phone_label.grid(row=2, column=0, padx=(20,0), pady=(20,0))
    phone_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    phone_entry.grid(row=2, column=1, padx=(15,0), pady=(20,0))

    email_label = tk.Label(left_frame, text="Email",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    email_label.grid(row=3, column=0, padx=(20,0), pady=(20,0))
    email_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    email_entry.grid(row=3, column=1, padx=(15,0), pady=(20,0))

    country_label = tk.Label(left_frame, text="Country",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    country_label.grid(row=4, column=0, padx=(20,0), pady=(20,0))
    country_entry = tk.Entry(left_frame, font=('times new roman', 12), bg='lightyellow', width=25)
    country_entry.grid(row=4, column=1, padx=(15,0), pady=(20,0))
    
    address_label = tk.Label(left_frame, text="Address",font=('times new roman', 12, 'bold'), bg='white', width=15, anchor='w')
    address_label.grid(row=5, column=0, padx=(20,0), pady=(20,0), sticky='nw')
    address_text = tk.Text(left_frame, width=31, height=6, bg='lightyellow', bd=2)
    address_text.grid(row=5, column=1, padx=(15,0), pady=(20,0))

    button_frame = tk.Frame(left_frame, width=537, height= 200, bg='white')
    button_frame.place(x=0, y=450, relwidth=1)

    add_button = tk.Button(button_frame, text='Add', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2'
                                        )
    add_button.grid(row=0, column=0, padx=(20,0), pady=20)

    update_button = tk.Button(button_frame, text='Update', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2'
                                        )
    update_button.grid(row=0, column=1, padx=(20,0), pady=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2'
                                        )
    delete_button.grid(row=0, column=2, padx=(20,0), pady=20)

    clear_button = tk.Button(button_frame, text='Clear', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 8, 
                                         cursor='hand2'
                                        )
    clear_button.grid(row=0, column=3, padx=(20,0), pady=20)


    #Right frame code
    right_frame = tk.Frame(supplier_frame, width=537, height= 600, bg='red')
    right_frame.place(x=537, y=75)

    #Search Frame
    search_frame = tk.Frame(right_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, width=8, values=('ID', 'Company', 'Contact', 'Country'), 
                                                 font=('times new roman', 12), 
                                                 state='readonly'
                                                 )
    search_combobox.set('Select..')
    search_combobox.grid(row=0, column=0, padx=(5,10))

    #Entry Field
    search_entry = tk.Entry(search_frame, font=('times new roman', 12), bg='lightyellow', width=18)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text='Search', 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width=7, 
                                            cursor='hand2',
                                            )
    search_button.grid(row=0, column=2, padx=(12,12))

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width=7, 
                                          cursor='hand2'
                                            )
                                          
    show_button.grid(row=0, column=3)