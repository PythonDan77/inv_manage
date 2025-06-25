import tkinter as tk

def inventory_frame(parent):
    
    inv_frame = tk.Frame(parent, width=1075, height=650)
    inv_frame.place(x=226, y=100)
    headingLabel = tk.Label(inv_frame, text='Inventory Detail', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    headingLabel.place(x=0, y=0, relwidth=1)

    return inv_frame
