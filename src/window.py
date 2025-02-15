import tkinter as tk
import tkinter.ttk as ttk

import asyncio

from message import CubeComm
from cubestate import CubeState

import global_state

class MainWindow(tk.Tk):
    connection_status = None
    cube_frame = None
    cube_faces = []

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

        # Cube faces
        self.cube_frame = tk.Frame(main_frame)
        self.cube_frame.configure(bg="lightgrey")
        self.cube_frame.grid(column=0, row=3)

        self.cube_faces.append(tk.Canvas(self.cube_frame, width=30, height=30))
        self.cube_faces[0].grid(column=1, row=0)

        self.cube_faces.append(tk.Canvas(self.cube_frame, width=30, height=30))
        self.cube_faces[1].grid(column=0, row=1)

        self.cube_faces.append(tk.Canvas(self.cube_frame, width=30, height=30))
        self.cube_faces[2].grid(column=1, row=1)

        self.cube_faces.append(tk.Canvas(self.cube_frame, width=30, height=30))
        self.cube_faces[3].grid(column=2, row=1)

        self.cube_faces.append(tk.Canvas(self.cube_frame, width=30, height=30))
        self.cube_faces[4].grid(column=3, row=1)

        self.cube_faces.append(tk.Canvas(self.cube_frame, width=30, height=30))
        self.cube_faces[5].grid(column=1, row=2)

        self.new_cube_state(CubeState())

    def sync_to_solved(self):
        if global_state.cube_comm is not None:
            asyncio.create_task(global_state.cube_comm.send_state_sync(CubeState()))

    def new_cube_state(self, state: CubeState):
        self.draw_cube_face(self.cube_faces[0], state.white)
        self.draw_cube_face(self.cube_faces[1], state.orange)
        self.draw_cube_face(self.cube_faces[2], state.green)
        self.draw_cube_face(self.cube_faces[3], state.red)
        self.draw_cube_face(self.cube_faces[4], state.blue)
        self.draw_cube_face(self.cube_faces[5], state.yellow)

    def draw_cube_face(self, canvas: tk.Canvas, face):
        i = 0

        for y in [1, 11, 21]:
            for x in [1, 11, 21]:
                color = CubeState.int_color_dict[face[i]]
                if self.connection_status.get() != "Connected":
                    color = "grey"

                canvas.create_rectangle(x, y, x + 9, y + 9, fill=color)
                i += 1

        canvas.create_line(0,0, 0,30, 30,30, 30,0, 0,0)

    def shutdown(self):
        self.close = True
        self.root.destroy()

    def render(self):
        self.root.update()

