from gui.root_window import create_main_window
from db.create_tables import ensure_tables_exist
from db.sync_tables import sync_inventory_status


def main():
    ensure_tables_exist()
    sync_inventory_status()
    root = create_main_window()

    root.mainloop()

if __name__ == "__main__":
    main()