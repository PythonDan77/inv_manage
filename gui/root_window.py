import tkinter as tk
from gui.inventory_frame import inventory_frame
from gui.supplier_frame import supplier_frame
from gui.purchase_frame import purchase_frame
from gui.user_frame import user_frame
from gui.asset_path import asset_path
import time

current_frame = None

# Update time and date on sub title bar. Function called from bottom of create_main_window().
def time_update(user_info):
    date_time = time.strftime('\t\t%I:%M:%S %p\t\t %A, %B %d, %Y')
    subtitleLabel.config(text=f'Welcome {user_info['full_name']}{date_time}')
    subtitleLabel.after(1000, lambda: time_update(user_info)) # Update every 1000ms (1 sec).

# Close frame before opening another.
def forget_last(func, root, user_info):
    global current_frame
    if current_frame:
        current_frame.place_forget()
    current_frame = func(root, user_info)

def create_main_window(user_info):
    global subtitleLabel

    root = tk.Tk()
    root.title('Inventory Management')
    root.geometry('1300x750+300+150')
    root.resizable(0, 0)
    root.config(bg='white')

    icon_png = tk.PhotoImage(file=asset_path("icon.png"))
    checklist_png = tk.PhotoImage(file=asset_path("inventory2.png"))
    boxes_png = tk.PhotoImage(file=asset_path("boxes.png"))
    ic_png = tk.PhotoImage(file=asset_path("ic.png"))
    cart_png = tk.PhotoImage(file=asset_path("cart.png"))
    truck_png = tk.PhotoImage(file=asset_path("shipping.png"))
    supplier_png = tk.PhotoImage(file=asset_path("supplier.png"))
    user_png = tk.PhotoImage(file=asset_path("user.png"))
    assembly_png = tk.PhotoImage(file=asset_path("assembly.png"))
    
    #Small png and title bar (bg='#010c48')
    titleLabel = tk.Label(root, text='         Inventory Management', 
                                font=('times new roman', 40, 'bold'), 
                                bg='#0f4d7d', 
                                fg='white', 
                                image=icon_png, 
                                compound='left', 
                                anchor='w', 
                                padx=20)
    titleLabel.image = icon_png
    titleLabel.place(x=0, y=0, relwidth=1)
    
    logoutButton = tk.Button(root, text='Exit', font=('times new roman', 20, 'bold'), fg='#010c48')
    logoutButton.place(x=1120, y=10)

    #Sub title bar with date and time
    subtitleLabel = tk.Label(root, text='Date: 06-24-2025\t\t\tTime: 12:34:17 PM',font=('times new roman', 15), bg='#8A9966', fg='white')
    subtitleLabel.place(x=0, y=70, relwidth=1)

    #Left frame
    leftFrame = tk.Frame(root)
    leftFrame.place(x=0, y=100, width=200, height=650)
    
    #Image of checklist and person in leftFrame
    checklistLabel = tk.Label(leftFrame, image=checklist_png)
    checklistLabel.image = checklist_png
    checklistLabel.pack()
    
    #Menu text in left frame
    menuLabel = tk.Label(leftFrame, text='Menu', font=('times new roman', 20), bg='#0f4d7d', fg='white')
    menuLabel.pack(fill='x')
    
    #Inventory button with boxes png(25 px)
    
    inventory_button = tk.Button(leftFrame, text='Inventory', 
                                            font=('times new roman', 16, 'bold'), 
                                            image=boxes_png, 
                                            compound='left', 
                                            anchor='w',
                                            # command=lambda: inventory_frame(root)
                                            command= lambda: forget_last(inventory_frame, root, user_info))
    inventory_button.image = boxes_png
    inventory_button.pack(fill='x')

    #Purchasing button with IC png(25 px)
    purchasing_button = tk.Button(leftFrame, text='Purchasing', 
                                             font=('times new roman', 16, 'bold'), 
                                             image=ic_png, 
                                             compound='left', 
                                             anchor='w',
                                             command= lambda: forget_last(purchase_frame, root, user_info))
    purchasing_button.image = ic_png
    purchasing_button.pack(fill='x')

    supplier_button = tk.Button(leftFrame, text='Suppliers', 
                                           font=('times new roman', 16, 'bold'), 
                                           image=supplier_png, 
                                           compound='left', 
                                           anchor='w',
                                        #    command=lambda: supplier_frame(root)
                                           command= lambda: forget_last(supplier_frame, root, user_info)
                                           )
    supplier_button.image = supplier_png
    supplier_button.pack(fill='x')

    #Sales button with cart png(25 px)
    orders_button = tk.Button(leftFrame, text='Orders', font=('times new roman', 16, 'bold'), image=cart_png, compound='left', anchor='w')
    orders_button.image = cart_png
    orders_button.pack(fill='x')

    sub_assembly_button = tk.Button(leftFrame, text='Assembly', font=('times new roman', 16, 'bold'), image=assembly_png, compound='left', anchor='w')
    sub_assembly_button.image = assembly_png
    sub_assembly_button.pack(fill='x')

    #Assembly button with assy png(25 px)
    assembly_button = tk.Button(leftFrame, text='Assembly', font=('times new roman', 16, 'bold'), image=assembly_png, compound='left', anchor='w')
    assembly_button.image = assembly_png
    assembly_button.pack(fill='x')

    products_button = tk.Button(leftFrame, text='Products', font=('times new roman', 16, 'bold'), image=assembly_png, compound='left', anchor='w')
    products_button.image = assembly_png
    products_button.pack(fill='x')

    if user_info['role'] in ['manager', 'admin']:
        user_button = tk.Button(leftFrame, text='Users', 
                                        font=('times new roman', 16, 'bold'), 
                                        image=user_png, 
                                        compound='left', 
                                        anchor='w',
                                        command= lambda: forget_last(user_frame, root, user_info)
                                        )
        user_button.image = user_png
        user_button.pack(fill='x')

    time_update(user_info)

    return root






