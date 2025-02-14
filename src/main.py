#!/usr/bin/env python3

from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

import asyncio

import time

from message import CubeComm

from window import MainWindow

async def main_loop(mac_address):
    cube_comm = CubeComm()

    window = MainWindow(cube_comm)
    window.set_mac_address(mac_address)

    while not window.close:
        window.render()

        await asyncio.sleep(0.1)


async def scan_for_devices():
    print("Scanning...")

    devices = await BleakScanner.discover(return_adv=True)

    for d in devices.values():
        print(d)
        print("\n")

if __name__ == "__main__":
    with open('address.txt') as f:
        mac_address = f.read().replace("\n", "")
        asyncio.run(main_loop(mac_address))
