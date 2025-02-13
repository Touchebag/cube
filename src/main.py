#!/usr/bin/env python3

from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

import asyncio

import time

from message import CubeComm

async def main_loop(client, mac_address):
    cube_comm = CubeComm()
    cube_comm.set_client(client)

    await cube_comm.setup_notifications()

    print("Sending hello")
    await cube_comm.send_hello(mac_address)

    while True:
        await asyncio.sleep(0.1)

async def connect(address):
    print(f"Connecting to device {address}")
    device = await BleakScanner.find_device_by_address(address)

    async with BleakClient(device) as client:
        print("Connected")
        await main_loop(client, address)

async def scan_for_devices():
    print("Scanning...")

    devices = await BleakScanner.discover(return_adv=True)

    for d in devices.values():
        print(d)
        print("\n")

if __name__ == "__main__":
    with open('address.txt') as f:
        asyncio.run(connect(f.read().replace("\n", "")))
