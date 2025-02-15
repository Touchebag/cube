import tkinter as tk
import tkinter.ttk as ttk

import asyncio
import time

from message import CubeComm
from cubestate import CubeState

import global_state

class MainWindow(tk.Tk):
    cube_frame = None
    cube_faces = []

    ready_to_solve = False
    solve_start_time = None

    # Used to close loop and shutdown program
    close = False

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cube")
        self.root.geometry("300x200")
        self.root.protocol("WMI_DELETE_WINDOW", self.shutdown)

        self.connection_status = tk.StringVar(value="N/A")
        global_state.cube_comm = CubeComm(self.connection_status)

        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.grid(column=0, row=0)

        ttk.Label(main_frame, text="Status: ").grid(column=0, row=0)
        ttk.Label(main_frame, textvariable=self.connection_status).grid(column=1, row=0)

        ttk.Button(main_frame, text="Sync to solved", command=self.sync_to_solved).grid(column=0, row=1)
        ttk.Button(main_frame, text="Start solve", command=self.start_solve).grid(column=1, row=1)

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

        self.total_time = tk.StringVar(value="N/A")
        ttk.Label(main_frame, textvariable=self.total_time).grid(column=0, row=4)

    def sync_to_solved(self):
        if global_state.cube_comm is not None:
            asyncio.create_task(global_state.cube_comm.send_state_sync(CubeState()))

    def start_solve(self):
        print("Solve mode, make a move to start timer")
        self.ready_to_solve = True

    def new_cube_state(self, state: CubeState):
        if self.ready_to_solve:
            self.solve_start_time = time.time()
            self.ready_to_solve = False

        if self.solve_start_time is not None and state.is_solved():
            self.total_time.set(self.print_time(time.time() - self.solve_start_time))
            self.solve_start_time = None

        self.draw_cube_face(self.cube_faces[0], state.white)
        self.draw_cube_face(self.cube_faces[1], state.orange)
        self.draw_cube_face(self.cube_faces[2], state.green)
        self.draw_cube_face(self.cube_faces[3], state.red)
        self.draw_cube_face(self.cube_faces[4], state.blue)
        self.draw_cube_face(self.cube_faces[5], state.yellow)

    def print_time(self, time):
        return f"{int(time)}.{int((time % 1) * 100)}s"

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
        if (self.solve_start_time is not None):
            self.total_time.set(self.print_time(time.time() - self.solve_start_time))
        self.root.update()

