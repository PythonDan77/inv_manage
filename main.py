import tkinter as tk
from gui.root_window import create_main_window
from gui.login_window import show_login_window, ensure_default_admin
from db.create_tables import ensure_tables_exist
from db.sync_tables import sync_inventory_status, sync_final_assembly


# def main():
#     ensure_tables_exist()
#     sync_inventory_status()
#     root = create_main_window()

#     root.mainloop()

def main():
    ensure_tables_exist()
    ensure_default_admin()

    # Show login window
    user_info = show_login_window()
    
    if user_info:  # If login was successful
        sync_inventory_status()
        sync_final_assembly()
        root = create_main_window(user_info)  # Pass user info if needed
        root.mainloop()
    else:
        print("Login failed or cancelled.")

if __name__ == "__main__":
    main()