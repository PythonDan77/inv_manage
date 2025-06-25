import os
import tkinter as tk
from gui.inventory_frame import inventory_frame

def asset_path(filename:str) -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "assets" , filename)

def create_main_window():

    root = tk.Tk()
    root.title('Inventory Management')
    root.geometry('1300x750+275+120')
    root.resizable(0, 0)
    root.config(bg='white')

    icon_png = tk.PhotoImage(file=asset_path("icon.png"))
    checklist_png = tk.PhotoImage(file=asset_path("checklist.png"))
    boxes_png = tk.PhotoImage(file=asset_path("boxes.png"))
    ic_png = tk.PhotoImage(file=asset_path("ic.png"))
    cart_png = tk.PhotoImage(file=asset_path("cart.png"))
    truck_png = tk.PhotoImage(file=asset_path("shipping.png"))

    #Small png and title bar
    titleLabel = tk.Label(root, text='         Inventory Management', 
                                font=('times new roman', 40, 'bold'), 
                                bg='#010c48', 
                                fg='white', 
                                image=icon_png, 
                                compound='left', 
                                anchor='w', 
                                padx=20)
    titleLabel.image = icon_png
    titleLabel.place(x=0, y=0, relwidth=1)
    
    logoutButton = tk.Button(root, text='Logout', font=('times new roman', 20, 'bold'), fg='#010c48')
    logoutButton.place(x=1120, y=10)

    #Sub title bar with date and time
    subtitleLabel = tk.Label(root, text='Date: 06-24-2025\t\t\tTime: 12:34:17 PM',font=('times new roman', 15), bg='#4d636d', fg='white')
    subtitleLabel.place(x=0, y=70, relwidth=1)

    #Left frame
    leftFrame = tk.Frame(root)
    leftFrame.place(x=0, y=100, width=225, height=650)
    
    #Image of checklist and person in leftFrame
    checklistLabel = tk.Label(leftFrame, image=checklist_png)
    checklistLabel.image = checklist_png
    checklistLabel.pack()
    
    #Menu text in left frame
    menuLabel = tk.Label(leftFrame, text='Menu', font=('times new roman', 25), bg='#010c48', fg='white')
    menuLabel.pack(fill='x')
    
    #Inventory button with boxes png(25 px)
    
    inventory_button = tk.Button(leftFrame, text='Inventory', 
                                            font=('times new roman', 20, 'bold'), 
                                            image=boxes_png, 
                                            compound='left', 
                                            anchor='w',
                                            command=lambda: inventory_frame(root))
    inventory_button.image = boxes_png
    inventory_button.pack(fill='x')

    #Purchasing button with IC png(25 px)
    
    purchasing_button = tk.Button(leftFrame, text='Purchasing', font=('times new roman', 20, 'bold'), image=ic_png, compound='left', anchor='w')
    purchasing_button.image = ic_png
    purchasing_button.pack(fill='x')

    #Sales button with cart png(25 px)
    sales_button = tk.Button(leftFrame, text='Sales', font=('times new roman', 20, 'bold'), image=cart_png, compound='left', anchor='w')
    sales_button.image = cart_png
    sales_button.pack(fill='x')

    #Shipping button with truck png(25 px)
    shipping_button = tk.Button(leftFrame, text='Shipping', font=('times new roman', 20, 'bold'), image=truck_png, compound='left', anchor='w')
    shipping_button.image = truck_png
    shipping_button.pack(fill='x')

    return root