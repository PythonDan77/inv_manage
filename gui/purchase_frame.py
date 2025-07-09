import tkinter as tk
from tkinter import ttk
from gui.asset_path import asset_path
from db.connection import get_conn
from tkinter import messagebox, filedialog
from datetime import datetime
import csv
import os

# Used to populate the treeview form with orders. It is called after purchase_treeview is created in purchase_frame(). Also add_update_item()
def treeview():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT
                pr.id,
                pr.part_id,
                i.part_name,
                i.part_number,
                i.restock_qty,
                pr.requested_by,
                pr.status,
                pr.request_date,
                pr.notes,
                pr.purchased_by,
                pr.purchase_qty,
                pr.purchase_date,
                pr.outstanding_qty
            FROM purchase_requests pr
            JOIN inventory_items i ON pr.part_id = i.id
            ORDER BY pr.id;"""
        )
        all_records = cur.fetchall()
        purchase_treeview.delete(*purchase_treeview.get_children())
        for record in all_records:
            clean_record = ["" if field is None else field for field in record]
            purchase_treeview.insert('', 'end', values=clean_record)

def create_request(part_id_entry, notes_entry, user):

    part_id = part_id_entry.get()
    notes = notes_entry.get()

    if not part_id:
        messagebox.showerror('Empty Field', 'Part ID cannot be empty.')
        return
    
    try:
        part_id = int(part_id)
    except ValueError:
        messagebox.showerror("Validation Error", "Part ID must be a number.")
        return

    if not notes:
        notes = "User-generated request"

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM inventory_items WHERE id = %s""", (part_id,)
            )

            result = cur.fetchone()
            if not result:
                messagebox.showerror("Not Found", "Part ID not found.")
                return

            cur.execute(
                """SELECT * FROM purchase_requests WHERE part_id = %s""", (part_id,)
            )
            duplicate = cur.fetchone()
            if duplicate:
                dup_confirm = messagebox.askyesno('Duplicate Request', 'This request already exists. Do you want to proceed?')
                if not dup_confirm:
                    return

            set_date = datetime.today().strftime('%Y-%m-%d')
            cur.execute( """INSERT INTO purchase_requests (part_id, requested_by, request_date, status, notes) 
                            VALUES (%s, %s, %s, %s, %s)""",
                            (result[0],
                             user,
                             set_date,
                             'requested',
                             notes)
                        )
        conn.commit()
        treeview()

        part_id_entry.delete(0,tk.END)
        notes_entry.delete(0,tk.END)
    except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Check to make sure a row is selected to either update or delete.
def row_select_check(user, receive=False, purchase=False, delete=False):
    
    selected = purchase_treeview.selection()
    if not selected:
        messagebox.showerror('Error','You must select a row.')
        return

    # Get the currently selected ID of the row.
    data = purchase_treeview.item(selected)
    id_num = data['values'][0]

    if delete:
        delete_item(id_num)
    elif purchase:
        open_purchase_popup(user, id_num)
    elif receive:
        open_received_popup(user, id_num)

# Pop up window to handle the purchase of items when they are marked requested in the table.
def open_purchase_popup(user, id_num):
    popup = tk.Toplevel(bg='white')
    popup.title("Enter Purchase Quantity")
    popup.geometry("500x300+700+400")
    popup.transient()  # Keeps it on top
    popup.grab_set()   # Modal behavior
    
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                    """SELECT 
                            ii.part_name,
                            ii.restock_qty,
                            pr.status
                        FROM purchase_requests pr
                        JOIN inventory_items ii ON pr.part_id = ii.id
                        WHERE pr.id = %s;""", (id_num,)
                        )
            result = cur.fetchone()
    except Exception as e:
            messagebox.showerror("Database Error", str(e))

    if result[2] == 'ordered':
        confirm = messagebox.askyesno('Already Ordered', 'This item has already been ordered. Do you want to adjust the order?')
        if not confirm:
            popup.destroy()
            return

    tk.Label(popup, text=f"Part: {result[0]}", font=('times new roman', 10, 'bold'), bg='white').pack(pady=5)
    tk.Label(popup, text=f"Requested: {result[1]}", font=('times new roman', 10, 'bold'), bg='white').pack(pady=5)
    tk.Label(popup, text="Qty Purchased:", font=('times new roman', 10, 'bold'), bg='white').pack(pady=5)

    qty_entry = tk.Entry(popup, font=('times new roman', 12), bg='lightyellow')
    qty_entry.pack(pady=5)

    def submit_purchase():
        qty = qty_entry.get()

        if not qty:
            messagebox.showerror("Error", "Quantity cannot be empty.")
            return

        if not qty.isdigit():
            messagebox.showerror("Error", "Enter a valid quantity")
            return

        try:
            conn = get_conn()
            set_date = datetime.today().strftime('%Y-%m-%d')
            with conn.cursor() as cur:
                cur.execute(
                        """UPDATE purchase_requests SET status=%s, 
                                        purchased_by=%s, 
                                        purchase_qty=%s, 
                                        purchase_date=%s,
                                        outstanding_qty=%s
                                        WHERE id=%s""",
                                        ('ordered', user, qty, set_date, qty, id_num)
                            )
                result = cur.fetchone()
            conn.commit()
            treeview()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        popup.destroy()

    def cancel():
        popup.destroy()

    submit_button = tk.Button(popup, text="Submit", 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=submit_purchase)
    submit_button.pack(side="left", padx=10, pady=10)
    cancel_button = tk.Button(popup, text="Cancel", font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=cancel)
    cancel_button.pack(side="right", padx=10, pady=10)

# Pop up to handle receiving shipments. Full and partial.
def open_received_popup(user, id_num):
    popup = tk.Toplevel(bg='white')
    popup.title("Enter Received Quantity")
    popup.geometry("500x300+700+400")
    popup.transient()  # Keeps it on top
    popup.grab_set()

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                    """SELECT 
                            ii.id,
                            ii.part_name,
                            pr.requested_by,
                            pr.purchased_by,
                            pr.purchase_qty,
                            pr.request_date,
                            pr.purchase_date,
                            pr.status,
                            pr.outstanding_qty,
                            pr.id
                        FROM purchase_requests pr
                        JOIN inventory_items ii ON pr.part_id = ii.id
                        WHERE pr.id = %s;""", (id_num,)
                        )
            result = cur.fetchone()
    except Exception as e:
            messagebox.showerror("Database Error", str(e))
   
    if result[7] == 'requested':
        messagebox.showerror("Receiving Error", 'Item has not been marked "ordered" and cannot be received.')
        popup.destroy()
        return
    
    tk.Label(popup, text=f"Part: {result[1]}", font=('times new roman', 10, 'bold'), bg='white').pack(pady=5)
    tk.Label(popup, text=f"Purchased: {result[4]}", font=('times new roman', 10, 'bold'), bg='white').pack(pady=5)
    tk.Label(popup, text="Qty Received:", font=('times new roman', 10, 'bold'), bg='white').pack(pady=5)

    qty_entry = tk.Entry(popup, font=('times new roman', 12), bg='lightyellow')
    qty_entry.pack(pady=5)

    def submit_received():
        qty = qty_entry.get()
        set_date = datetime.today().strftime('%Y-%m-%d')

        if not qty:
            messagebox.showerror("Error", "Quantity cannot be empty.")
            return

        try:
            qty = int(qty)
        except ValueError:
            messagebox.showerror("Validation Error", "Qty must be a number.")
            return

        try:
            conn = get_conn()
            with conn.cursor() as cur:
                received_now = qty
                total_outstanding = result[8]
                remaining = total_outstanding - received_now
                note = f"Received {received_now}/{result[4]} on {set_date}. {remaining} remaining."

                # Insert into purchase_history always (log every receive event)
                cur.execute(
                    """INSERT INTO purchase_history (
                        purchase_id, part_id, part_name, requested_by, purchased_by,
                        received_by, purchase_qty, received_qty,
                        request_date, purchase_date, receive_date, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        result[9], result[0], result[1], result[2], result[3],
                        user, result[4], received_now,
                        result[5], result[6], set_date,
                        note
                    )
                )

                cur.execute(
                    """UPDATE inventory_items
                    SET quantity = quantity + %s,
                        last_receive_qty = %s,
                        last_receive_date = %s
                    WHERE id = %s""",
                    (received_now, received_now, set_date, result[0])
                )

                if remaining > 0:
                    # Partial receipt: update outstanding and status
                    cur.execute(
                        """UPDATE purchase_requests
                        SET status = %s,
                            notes = %s,
                            outstanding_qty = %s
                        WHERE id = %s""",
                        ('received partial', note, remaining, id_num)
                    )

                else:
                    # All items received: delete from purchase_requests
                    cur.execute("DELETE FROM purchase_requests WHERE id = %s", (id_num,))

            conn.commit()
            treeview()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        popup.destroy()

    def cancel():
        popup.destroy()

    submit_button = tk.Button(popup, text="Submit", 
                                            font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=submit_received)
    submit_button.pack(side="left", padx=10, pady=10)
    cancel_button = tk.Button(popup, text="Cancel", font=('times new roman', 12), 
                                            bg='#0f4d7d', 
                                            fg='white', 
                                            width= 10, 
                                            cursor='hand2',
                                            command=cancel)
    cancel_button.pack(side="right", padx=10, pady=10)


# Delete the selected row/item.
def delete_item(id_num):

    result = messagebox.askyesno('Confirm', 'Do you want to delete this record?')
    if result:
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute('DELETE FROM purchase_requests WHERE id=%s',(id_num,))
            conn.commit()
            treeview()
            messagebox.showinfo('Success','Deleted Successfully.')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# History tab that provides access to the table purchase_history which shows all completed and received purchases.
def history_popup():

    popup = tk.Toplevel(bg='white')
    popup.title("Purchase History")
    popup.geometry("1150x650+400+250")
    popup.transient()  # Keeps it on top
    popup.grab_set()   # Modal behavior

    history_treeview = None

    heading_label = tk.Label(popup, text='Purchase History', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    top_frame = tk.Frame(popup, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()

    # Function verifies data has been used to search the database and then retrieves the data.
    def hist_search_item(search_option, value):
        if search_option == 'Select..':
            messagebox.showerror('Error','Select an option.')
        elif not value:
            messagebox.showerror('Error','Enter a value to search.')
        else:
            try:
                search_option = search_option.replace(' ', '_')
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute(f'SELECT * FROM purchase_history WHERE {search_option} LIKE %s', f'%{value}%')
                    result = cur.fetchall()
                    history_treeview.delete(*history_treeview.get_children())
                    for record in result:
                        history_treeview.insert('', 'end', values=record)

            except Exception as e:
                messagebox.showerror("Database Error", str(e))

    # Reloads all data and resets the search options.
    def hist_search_all(search_entry, search_combobox):
        hist_treeview()
        search_entry.delete(0,'end')
        search_combobox.set('Select...')

    # Clear the highlight from the combobox. Trigger in the main function at the bottom.
    def hist_on_select(event, combobox):
        combobox.selection_clear()

    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Part ID', 'Part name'), 
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
                                            command= lambda: hist_search_item(search_combobox.get(),search_entry.get())
                                            )
    search_button.grid(row=0, column=2, padx=20)

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 10, 
                                          cursor='hand2',
                                          command= lambda: hist_search_all(search_entry, search_combobox)
                                          )
    show_button.grid(row=0, column=3)

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    history_treeview = ttk.Treeview(top_frame, columns=('id', 'purchase_id', 'part_id', 'part_name', 'requested_by', 'purchased_by', 
                                                        'receieved_by', 'purchase_qty', 'received_qty', 'request_date', 
                                                        'purchase_date', 'receive_date', 'notes'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=history_treeview.xview)
    vertical_scrollbar.config(command=history_treeview.yview)
    history_treeview.pack(pady= (10, 0))
    
    history_treeview.heading('id', text='History ID')
    history_treeview.heading('purchase_id', text='Purchase ID')
    history_treeview.heading('part_id', text='Part ID')
    history_treeview.heading('part_name', text='Part name')
    history_treeview.heading('requested_by', text='Requested by')
    history_treeview.heading('purchased_by', text='Purchased by')
    history_treeview.heading('receieved_by', text='Received by')
    history_treeview.heading('purchase_qty', text='Purchase qty')
    history_treeview.heading('received_qty', text='Received qty')
    history_treeview.heading('request_date', text='Request date')
    history_treeview.heading('purchase_date', text='Purchased date')
    history_treeview.heading('receive_date', text='Received date')
    history_treeview.heading('notes', text='Notes')
    
    history_treeview.column('id', width=100)
    history_treeview.column('purchase_id', width=100)
    history_treeview.column('part_id', width=100)
    history_treeview.column('part_name', width=200)
    history_treeview.column('requested_by', width=175)
    history_treeview.column('purchased_by', width=170)
    history_treeview.column('receieved_by', width=170)
    history_treeview.column('purchase_qty', width=125)
    history_treeview.column('received_qty', width=125)
    history_treeview.column('request_date', width=150)
    history_treeview.column('purchase_date', width=150)
    history_treeview.column('receive_date', width=150)
    history_treeview.column('notes', width=300)
    
    def hist_treeview():
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM purchase_history"""
                )
                all_records = cur.fetchall()
                history_treeview.delete(*history_treeview.get_children())
                for record in all_records:
                    clean_record = ["" if field is None else field for field in record]
                    history_treeview.insert('', 'end', values=clean_record)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    #call treeview function to display the items.
    hist_treeview()

    button_frame= tk.Frame(popup, bg='white')
    button_frame.place(x=400, y=500, relwidth=1)

    def cancel():
        popup.destroy()

    close_button = tk.Button(button_frame, text='Close', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=cancel)
                                                                  
    close_button.grid(row=0, column=0, padx=20)

    def export_purchase_history_to_csv():
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM purchase_history")
                rows = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]

            if not rows:
                messagebox.showinfo("Export", "No data in purchase history.")
                return

            # Default filename
            default_filename = f"purchase_history_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

            # Path to user's Desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            # Ask where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                initialdir=desktop_path,
                title="Save Purchase History As"
            )

            if not file_path:
                return  # User cancelled

            # Write the CSV file
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(column_names)  # headers
                writer.writerows(rows)         # data

            messagebox.showinfo("Export Successful", f"CSV file saved:\n{file_path}")

            # Optionally open the file (Windows only)
            try:
                os.startfile(file_path)
            except:
                pass

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    excel_button = tk.Button(button_frame, text='Excel Sheet', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=export_purchase_history_to_csv
                                        )
                                                                  
    excel_button.grid(row=0, column=1, padx=20)

    search_combobox.bind("<<ComboboxSelected>>", lambda event: hist_on_select(event, search_combobox))

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
                cur.execute(f'SELECT * FROM purchase_requests WHERE {search_option} LIKE %s', f'%{value}%')
                result = cur.fetchall()
                purchase_treeview.delete(*purchase_treeview.get_children())
                for record in result:
                    purchase_treeview.insert('', 'end', values=record)

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

def purchase_frame(parent, user_info):
    global purchase_treeview

    purchase_frame = tk.Frame(parent, width=1100, height=650, bg='white')
    purchase_frame.place(x=201, y=100)
    
    heading_label = tk.Label(purchase_frame, text='Purchasing Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_img_purchase = tk.PhotoImage(file=asset_path('back_button.png'))
    back_button = tk.Button(purchase_frame, image=back_img_purchase,
                                       bd=0, highlightthickness=0, 
                                       bg='white', cursor='hand2', 
                                       command=lambda:purchase_frame.place_forget())
    back_button.image = back_img_purchase
    back_button.place(x=5, y=33)

    #Top Section of Page
    top_frame = tk.Frame(purchase_frame, width=1075, height=240, bg='white')
    top_frame.place(x=0, y=75, relwidth=1)
    
    #Search Frame
    search_frame = tk.Frame(top_frame, bg='white')
    search_frame.pack()
    #Drop Down Menu
    search_combobox = ttk.Combobox(search_frame, values=('ID', 'Part ID', 'Part name', 'Part number', 'Status'), 
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
                                            command= lambda: search_item(search_combobox.get(),search_entry.get())
                                            )
    search_button.grid(row=0, column=2, padx=20)

    show_button = tk.Button(search_frame, text='Show All', 
                                          font=('times new roman', 12), 
                                          bg='#0f4d7d', 
                                          fg='white', 
                                          width= 10, 
                                          cursor='hand2',
                                          command= lambda: search_all(search_entry, search_combobox)
                                          )
    show_button.grid(row=0, column=3)

    horizontal_scrollbar = tk.Scrollbar(top_frame, orient='horizontal')
    vertical_scrollbar = tk.Scrollbar(top_frame, orient='vertical')
    
    purchase_treeview = ttk.Treeview(top_frame, columns=('id', 'part_id', 'part_name', 'part_number', 'order_quantity', 'requested_by', 'status','request_date', 'notes', 'purchased_by', 'purchase_qty', 'purchase_date', 'outstanding_qty'), 
                                           show='headings',
                                           yscrollcommand=vertical_scrollbar.set,
                                           xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side='bottom', fill='x')
    vertical_scrollbar.pack(side='right', fill='y', pady=(10, 0))
    horizontal_scrollbar.config(command=purchase_treeview.xview)
    vertical_scrollbar.config(command=purchase_treeview.yview)
    purchase_treeview.pack(pady= (10, 0))
    
    purchase_treeview.heading('id', text='Order ID')
    purchase_treeview.heading('part_id', text='Part ID')
    purchase_treeview.heading('part_name', text='Part name')
    purchase_treeview.heading('part_number', text='Part number')
    purchase_treeview.heading('order_quantity', text='Reorder Qty')
    purchase_treeview.heading('requested_by', text='Requested by')
    purchase_treeview.heading('status', text='Status')
    purchase_treeview.heading('request_date', text='Date Requested')
    purchase_treeview.heading('notes', text='Notes')
    purchase_treeview.heading('purchased_by', text='Purchased by')
    purchase_treeview.heading('purchase_qty', text='Purchase qty')
    purchase_treeview.heading('purchase_date', text='Purchase date')
    purchase_treeview.heading('outstanding_qty', text='Outstanding Qty')
  
    
    purchase_treeview.column('id', width=100)
    purchase_treeview.column('part_id', width=100)
    purchase_treeview.column('part_name', width=200)
    purchase_treeview.column('part_number', width=175)
    purchase_treeview.column('order_quantity', width=100)
    purchase_treeview.column('requested_by', width=170)
    purchase_treeview.column('status', width=175)
    purchase_treeview.column('request_date', width=150)
    purchase_treeview.column('notes', width=300)
    purchase_treeview.column('purchased_by', width=175)
    purchase_treeview.column('purchase_qty', width=120)
    purchase_treeview.column('purchase_date', width=150)
    purchase_treeview.column('outstanding_qty', width=150)
    
    #call treeview function to display the items.
    treeview()

    #Lower Section of Page
    detail_frame = tk.Frame(purchase_frame, width=1075, height=300, bg='white')
    detail_frame.place(x=0, y=352, relwidth=1)
    
    part_id_label = tk.Label(detail_frame,text='Part ID', font=('times new roman', 10, 'bold'), bg='white', anchor='w')
    part_id_label.grid(row=0, column=0,padx=(20,10), pady=(20,0))
    part_id_entry = tk.Entry(detail_frame, font=('times new roman', 11), bg='lightyellow')
    part_id_entry.grid(row=0, column=1, padx=15, pady=(20,0))

    notes_label = tk.Label(detail_frame, text='Notes', font=('times new roman', 10, 'bold'), bg='white', anchor='w')
    notes_label.grid(row=0, column=2,padx=(10,10), pady=(20,0))
    notes_entry = tk.Entry(detail_frame, width=30, font=('times new roman', 11), bg='lightyellow')
    notes_entry.grid(row=0, column=3, padx=15, pady=(20,0))
    
    #Lower button Frame
    button_frame= tk.Frame(purchase_frame, bg='white')
    button_frame.place(x=110, y=550, relwidth=1)

    create_button = tk.Button(button_frame, text='Create', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: create_request(part_id_entry, notes_entry, user_info['full_name'])
                                                                  )
    create_button.grid(row=0, column=0, padx=20)

    purchased_button = tk.Button(button_frame, text='Purchase', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: row_select_check(user_info['full_name'], purchase=True)
                                                                  )
    purchased_button.grid(row=0, column=1, padx=20)

    received_button = tk.Button(button_frame, text='Receive', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: row_select_check(user_info['full_name'], receive=True)
                                                                  )
    received_button.grid(row=0, column=2, padx=20)

    delete_button = tk.Button(button_frame, text='Delete', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=lambda: row_select_check(user_info['full_name'],delete=True)
                                                                  )
    delete_button.grid(row=0, column=3, padx=20)

    history_button = tk.Button(button_frame, text='History', 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=history_popup
                                                                  )
    history_button.grid(row=0, column=4, padx=20)

    search_combobox.bind("<<ComboboxSelected>>", lambda event: on_select(event, search_combobox))

    #Disable all entry fields and certain buttons if user permissions are not adequate
    if user_info['role'] not in ['manager', 'admin']:
        purchased_button.config(state="disabled")
        received_button.config(state="disabled")
        delete_button.config(state="disabled")

    return purchase_frame