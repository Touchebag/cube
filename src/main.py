#!/usr/bin/env python3

import asyncio

from window import MainWindow

import global_state

async def main_loop():
    with open('address.txt') as f:
        mac_address = f.read().replace("\n", "")

        global_state.main_window = MainWindow()

        while not global_state.main_window.close:
            global_state.main_window.render()

            if global_state.cube_comm.connection_status.get() == "Not connected":
                asyncio.create_task(global_state.cube_comm.scan_and_connect())

            await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main_loop())
