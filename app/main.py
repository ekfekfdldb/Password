import tkinter as tk
from pathlib import Path

from app.store import Vault
from app.ui import LoginFrame, MainFrame
from app.utils import get_db_path, try_icon
from app.utils import resource_path
from app.version import __app_name__, __version__


def run():
    db_path: Path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    vault = Vault(db_path)
    vault.connect()
    vault.init_db_if_needed()

    root = tk.Tk()
    root.title(f"{__app_name__}")
    root.geometry("780x560")
    try_icon(root)

    def show_main():
        for w in root.winfo_children(): w.destroy()
        MainFrame(root, vault, switch_to_login=show_login).grid(row=0, column=0, sticky="nsew")

    def show_login():
        for w in root.winfo_children(): w.destroy()
        LoginFrame(root, vault, on_unlocked=show_main).grid(row=0, column=0, sticky="nsew")

    show_login()
    root.mainloop()

if __name__ == "__main__":
    run()
