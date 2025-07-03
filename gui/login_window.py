import tkinter as tk
import bcrypt
from db.connection import get_conn
from gui.asset_path import asset_path
from tkinter import messagebox
from db.config import ADMIN_PASS


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# -- Startup admin check --
def ensure_default_admin():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cur.fetchone()[0] == 0:
            default_password = ADMIN_PASS 
            hashed = hash_password(default_password)
            cur.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (%s, %s, 'admin', 'System Administrator')
            """, ('admin', hashed))
            conn.commit()
            print("Default admin user created (username: admin)")

def authenticate_user(username, password):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT username, role, password_hash, full_name FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[2].encode()):
            return {
                "username": row[0],
                "role": row[1],
                "full_name": row[3]
            }
    return None

def show_login_window():
    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("500x300+650+400")
    login_win.resizable(0 , 0)
    login_win.config(bg='white')

    username_var = tk.StringVar()
    password_var = tk.StringVar()
    user_info = {}

    titleLabel = tk.Label(login_win, text='       Inventory Management', 
                                font=('times new roman', 20, 'bold'), 
                                bg='#0f4d7d', 
                                fg='white', 
                                compound='left', 
                                anchor='w', 
                                padx=20)
    titleLabel.place(x=0, y=0, relwidth=1)

    login_frame = tk.Frame(login_win, width=500, height=400, bg='white')
    login_frame.place(x=80, y=60)

    username_label = tk.Label(login_frame, text="Username", font=('times new roman', 10, 'bold'), bg='white')
    username_label.grid(row=0, column=0,padx=(20,10), pady=20)
    
    username_entry = tk.Entry(login_frame, textvariable=username_var)
    username_entry.grid(row=0, column=1,padx=10, pady=20)

    password_label = tk.Label(login_frame, text="Password", font=('times new roman', 10, 'bold'), bg='white')
    password_label.grid(row=1, column=0,padx=(20,10), pady=20)
    password_entry = tk.Entry(login_frame, textvariable=password_var, show="*", bg='white')
    password_entry.grid(row=1, column=1,padx=10, pady=20)

    def try_login():
        username = username_var.get()
        password = password_var.get()
        user = authenticate_user(username, password)
        if user:
            user_info.update(user)  # user = dict with role, username, etc.
            login_win.destroy()
        else:
            messagebox.showerror("Login failed", "Incorrect username or password")

    button_frame= tk.Frame(login_win, bg='white')
    button_frame.place(x=10, y=225, relwidth=1)

    tk.Button(button_frame, text="Login", 
                                         font=('times new roman', 12), 
                                         bg='#0f4d7d', 
                                         fg='white', 
                                         width= 10, 
                                         cursor='hand2', 
                                         command=try_login).pack()

    login_win.grab_set()   # Make modal
    login_win.wait_window()

    return user_info if user_info else None