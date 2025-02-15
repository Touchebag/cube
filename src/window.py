import tkinter as tk
import tkinter.ttk as ttk

import asyncio

from message import CubeComm
from cubestate import CubeState

import global_state

class MainWindow(tk.Tk):
    connection_status = None

    # Used to close loop and shutdown program
    close = False

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cube")
        self.root.protocol("WMI_DELETE_WINDOW", self.shutdown)

        self.connection_status = tk.StringVar(value="N/A")
        global_state.cube_comm = CubeComm(self.connection_status)

        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.grid(column=0, row=0)

        ttk.Label(main_frame, text="Status: ").grid(column=0, row=0)
        ttk.Label(main_frame, textvariable=self.connection_status).grid(column=1, row=0)

        ttk.Button(main_frame, text="Sync to solved", command=self.sync_to_solved).grid(column=0, row=1)

    def sync_to_solved(self):
        if global_state.cube_comm is not None:
            asyncio.create_task(global_state.cube_comm.send_state_sync(CubeState()))

    def shutdown(self):
        self.close = True
        self.root.destroy()

    def render(self):
        self.root.update()

