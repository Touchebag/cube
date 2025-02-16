import tkinter as tk
import tkinter.ttk as ttk

import asyncio
import time

from dataclasses import dataclass

from message import CubeComm
from cubestate import CubeState

import global_state

@dataclass
class SolveTime():
    # Total time
    start_timestamp = None
    finished_timestamp = None

    # Splits
    crs_timestamp = None
    f2l_timestamp = None
    oll_timestamp = None

class SolvedResult():
    total = None
    cross = None
    f2l = None
    oll = None

class MainWindow(tk.Tk):
    cube_frame = None
    cube_faces = []

    current_solve_time = None
    prev_solve_time = None

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

        ttk.Label(main_frame, textvariable=self.connection_status).grid(column=0, row=0)

        self.battery_level = tk.StringVar(value="Battery: N/A")
        ttk.Label(main_frame, textvariable=self.battery_level).grid(column=1, row=0)

        ttk.Button(main_frame, text="Sync to solved", command=self.sync_to_solved, takefocus=0).grid(column=0, row=1)
        ttk.Button(main_frame, text="Start solve", command=self.start_solve, takefocus=0).grid(column=1, row=1)

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

        self.current_time = tk.StringVar(value="N/A")
        ttk.Label(main_frame, text="Current time: ").grid(column=0, row=4)
        ttk.Label(main_frame, textvariable=self.current_time).grid(column=1, row=4, sticky=tk.W)

        self.prev_total_time = tk.StringVar(value="")
        self.prev_crs_time = tk.StringVar(value="")
        self.prev_f2l_time = tk.StringVar(value="")
        self.prev_oll_time = tk.StringVar(value="")
        self.prev_pll_time = tk.StringVar(value="")
        ttk.Label(main_frame, text="Previous time: ").grid(column=0, row=5)
        ttk.Label(main_frame, textvariable=self.prev_total_time).grid(column=1, row=5, sticky=tk.W)
        ttk.Label(main_frame, text="Cross: ").grid(column=0, row=6)
        ttk.Label(main_frame, textvariable=self.prev_crs_time).grid(column=1, row=6, sticky=tk.W)
        ttk.Label(main_frame, text="F2L: ").grid(column=0, row=7)
        ttk.Label(main_frame, textvariable=self.prev_f2l_time).grid(column=1, row=7, sticky=tk.W)
        ttk.Label(main_frame, text="OLL: ").grid(column=0, row=8)
        ttk.Label(main_frame, textvariable=self.prev_oll_time).grid(column=1, row=8, sticky=tk.W)
        ttk.Label(main_frame, text="PLL: ").grid(column=0, row=9)
        ttk.Label(main_frame, textvariable=self.prev_pll_time).grid(column=1, row=9, sticky=tk.W)

        self.root.bind("<space>", self.start_solve)

    def sync_to_solved(self):
        if global_state.cube_comm is not None:
            asyncio.create_task(global_state.cube_comm.send_state_sync(CubeState()))

    def start_solve(self, _ = None):
        print("Solve mode, make a move to start timer")
        self.current_solve_time = SolveTime()

    def new_cube_state(self, state: CubeState):
        # If ready to solve
        if self.current_solve_time is not None:
            # Start solve
            if self.current_solve_time.start_timestamp is None:
                self.current_solve_time.start_timestamp = time.time()

            # Check cross
            if self.current_solve_time.crs_timestamp is None and state.is_cross_solved():
                print("Cross solved")
                self.current_solve_time.crs_timestamp = time.time()

            # Check f2l
            if self.current_solve_time.f2l_timestamp is None and state.is_f2l_solved():
                print("F2l solved")
                self.current_solve_time.f2l_timestamp = time.time()

            # Check OLL
            if self.current_solve_time.oll_timestamp is None and state.is_oll_solved():
                print("OLL solved")
                self.current_solve_time.oll_timestamp = time.time()

            # Check solved
            if state.is_solved():
                self.current_solve_time.finished_timestamp = time.time()

                self.prev_solve_time = SolvedResult()
                self.prev_solve_time.total = max(0, self.current_solve_time.finished_timestamp - self.current_solve_time.start_timestamp)
                self.prev_solve_time.cross = max(0, self.current_solve_time.crs_timestamp - self.current_solve_time.start_timestamp)
                self.prev_solve_time.f2l   = max(0, self.current_solve_time.f2l_timestamp - self.current_solve_time.crs_timestamp)
                self.prev_solve_time.oll   = max(0, self.current_solve_time.oll_timestamp - self.current_solve_time.f2l_timestamp)
                self.prev_solve_time.pll   = max(0, self.current_solve_time.finished_timestamp - self.current_solve_time.oll_timestamp)

                self.current_solve_time = None

                self.prev_total_time.set(self.print_time(self.prev_solve_time.total))
                self.prev_crs_time.set(self.print_time(self.prev_solve_time.cross) + " (" + str(round(100 * self.prev_solve_time.cross / self.prev_solve_time.total, 2)) + "%)")
                self.prev_f2l_time.set(self.print_time(self.prev_solve_time.f2l) + " (" + str(round(100 * self.prev_solve_time.f2l / self.prev_solve_time.total, 2)) + "%)")
                self.prev_oll_time.set(self.print_time(self.prev_solve_time.oll) + " (" + str(round(100 * self.prev_solve_time.oll / self.prev_solve_time.total, 2)) + "%)")
                self.prev_pll_time.set(self.print_time(self.prev_solve_time.pll) + " (" + str(round(100 * self.prev_solve_time.pll / self.prev_solve_time.total, 2)) + "%)")

        self.draw_cube_face(self.cube_faces[0], state.white)
        self.draw_cube_face(self.cube_faces[1], state.orange)
        self.draw_cube_face(self.cube_faces[2], state.green)
        self.draw_cube_face(self.cube_faces[3], state.red)
        self.draw_cube_face(self.cube_faces[4], state.blue)
        self.draw_cube_face(self.cube_faces[5], state.yellow)

    def print_time(self, time):
        return str(round(time, 1)) + "s"

    def set_battery_level(self, level: int):
        self.battery_level.set(f"Battery: {level}%")

    def draw_cube_face(self, canvas: tk.Canvas, face):
        i = 0

        for y in [1, 11, 21]:
            for x in [1, 11, 21]:
                color = CubeState.int_color_dict[face[i]]
                if self.connection_status.get() != "Connected":
                    color = "grey"

                canvas.create_rectangle(x, y, x + 9, y + 9, fill=color)
                i += 1

    def shutdown(self):
        self.close = True
        self.root.destroy()

    def render(self):
        if (self.current_solve_time is not None and
            self.current_solve_time.start_timestamp is not None):
                self.current_time.set(self.print_time(time.time() - self.current_solve_time.start_timestamp))
        self.root.update()

