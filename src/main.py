#!/usr/bin/env python3

from bleak import BleakScanner, BleakClient
import asyncio

async def connect(address):
    print(f"Trying to connect to device {address}")
    device = await BleakScanner.find_device_by_address(address)

    async with BleakClient(device) as client:
        print("Connected")

async def scan_for_devices():
    print("Scanning...")

    devices = await BleakScanner.discover(return_adv=True)

    for d in devices.values():
        print(d)
        print("\n")

if __name__ == "__main__":
    with open('address.txt') as f:
        asyncio.run(connect(f.read().replace("\n", "")))
