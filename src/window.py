import tkinter as tk
import tkinter.ttk as ttk

import asyncio

class MainWindow(tk.Tk):
    current_address = None
    cube_comm = None

    # Used to close loop and shutdown program
    close = False

    def connect(self):
        if self.cube_comm is not None:
            asyncio.create_task(self.cube_comm.connect(self.current_address.get()))

    def __init__(self, cube_comm):
        self.cube_comm = cube_comm

        self.root = tk.Tk()
        self.root.title("Cube")
        self.root.protocol("WMI_DELETE_WINDOW", self.shutdown)

        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.grid(column=0, row=0)

        self.current_address = tk.StringVar()
        self.current_address.set("N/A")
        ttk.Label(main_frame, textvariable=self.current_address).grid(column=0, row=0)

        ttk.Button(main_frame, text="Connect", command=self.connect).grid(column=1, row=0)

    def shutdown(self):
        self.close = True
        self.root.destroy()

    def set_mac_address(self, address):
        self.current_address.set(address)

    def render(self):
        self.root.update()

