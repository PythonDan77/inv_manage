import tkinter as tk
from gui.inventory_frame import inventory_frame
from gui.supplier_frame import supplier_frame
from gui.purchase_frame import purchase_frame
from gui.user_frame import user_frame
from gui.products_frame import products_frame
from gui.orders_frame import orders_frame
from gui.amplifier_frame import amplifier_frame
from gui.cabinet_frame import cabinet_frame
from gui.pedal_frame import pedal_frame
from gui.final_assembly import final_assy_frame
from gui.shipping_frame import shipping_frame
from gui.asset_path import asset_path
from db.sync_tables import sync_inventory_status, sync_final_assembly
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
    # Refresh the auto fill functions in sync tables (db section)
    sync_inventory_status()
    sync_final_assembly()

def create_main_window(user_info):
    global subtitleLabel

    root = tk.Tk()
    root.title('Inventory Management')
    root.geometry('1300x750+300+150')
    root.resizable(0, 0)
    root.config(bg='white')

    icon_png = tk.PhotoImage(file=asset_path("icon.png"))
    checklist_png = tk.PhotoImage(file=asset_path("g3344.png"))
    boxes_png = tk.PhotoImage(file=asset_path("boxes.png"))
    ic_png = tk.PhotoImage(file=asset_path("ic.png"))
    cart_png = tk.PhotoImage(file=asset_path("cart.png"))
    truck_png = tk.PhotoImage(file=asset_path("shipping.png"))
    supplier_png = tk.PhotoImage(file=asset_path("supplier.png"))
    user_png = tk.PhotoImage(file=asset_path("user.png"))
    assembly_png = tk.PhotoImage(file=asset_path("assembly.png"))
    products_png = tk.PhotoImage(file=asset_path("guitar-amplifier.png"))
    
    #Small png and title bar (bg='#010c48')
    titleLabel = tk.Label(root, text='           Inventory Management', 
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
    orders_button = tk.Button(leftFrame, text='Orders', 
                                         font=('times new roman', 16, 'bold'), 
                                         image=cart_png, 
                                         compound='left', 
                                         anchor='w',
                                         command= lambda: forget_last(orders_frame, root, user_info))
    orders_button.image = cart_png
    orders_button.pack(fill='x')

    amplifiers_button = tk.Button(leftFrame, text='Amplifiers', 
                                             font=('times new roman', 16, 'bold'), 
                                             image=assembly_png, 
                                             compound='left', 
                                             anchor='w',
                                             command=lambda: forget_last(amplifier_frame, root, user_info))
    amplifiers_button.image = assembly_png
    amplifiers_button.pack(fill='x')

    #Assembly button with assy png(25 px)
    pedals_button = tk.Button(leftFrame, text='Pedals', 
                                         font=('times new roman', 16, 'bold'), 
                                         image=assembly_png, 
                                         compound='left', 
                                         anchor='w',
                                         command=lambda: forget_last(pedal_frame, root, user_info)
                                         )
    pedals_button.image = assembly_png
    pedals_button.pack(fill='x')

    #Assembly button with assy png(25 px)
    cabinets_button = tk.Button(leftFrame, text='Cabinets', 
                                           font=('times new roman', 16, 'bold'), 
                                           image=assembly_png, 
                                           compound='left', 
                                           anchor='w',
                                           command=lambda: forget_last(cabinet_frame, root, user_info))
    cabinets_button.image = assembly_png
    cabinets_button.pack(fill='x')

    final_button = tk.Button(leftFrame, text='Final Assy', 
                                           font=('times new roman', 16, 'bold'), 
                                           image=assembly_png, 
                                           compound='left', 
                                           anchor='w',
                                           command=lambda: forget_last(final_assy_frame, root, user_info)
                                        )
    final_button.image = assembly_png
    final_button.pack(fill='x')

    shipping_button = tk.Button(leftFrame, text='Shipping', 
                                           font=('times new roman', 16, 'bold'), 
                                           image=truck_png, 
                                           compound='left', 
                                           anchor='w',
                                           command=lambda: forget_last(shipping_frame, root, user_info)
                                        )
    shipping_button.image = truck_png
    shipping_button.pack(fill='x')
    
    if user_info['role'] in ['manager', 'admin']:
        products_button = tk.Button(leftFrame, text='Assemblies', 
                                            font=('times new roman', 16, 'bold'), 
                                            image=products_png, 
                                            compound='left', 
                                            anchor='w',
                                            command= lambda: forget_last(products_frame, root, user_info))
        products_button.image = products_png
        products_button.pack(fill='x')

    if user_info['role'] in ['admin']:
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






