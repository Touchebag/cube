#!/usr/bin/env python3

import asyncio

from window import MainWindow

async def main_loop():
    with open('address.txt') as f:
        mac_address = f.read().replace("\n", "")

        window = MainWindow()

        while not window.close:
            window.render()

            if window.cube_comm.connection_status.get() == "Not connected":
                asyncio.create_task(window.cube_comm.scan_and_connect())

            await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main_loop())
