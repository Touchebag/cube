#!/usr/bin/env python3

from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

import asyncio

import time

from message import send_hello, setup_notifications

CHARACTERISTIC = "fff6"

MAC_ADDRESS = None

async def main_loop(client):
    await setup_notifications(client)

    print("Sending hello")
    await send_hello(client, MAC_ADDRESS)

    while True:
        await asyncio.sleep(0.1)

async def connect(address):
    print(f"Connecting to device {address}")
    device = await BleakScanner.find_device_by_address(address)

    async with BleakClient(device) as client:
        print("Connected")
        global MAC_ADDRESS
        MAC_ADDRESS = address
        await main_loop(client)

async def scan_for_devices():
    print("Scanning...")

    devices = await BleakScanner.discover(return_adv=True)

    for d in devices.values():
        print(d)
        print("\n")

if __name__ == "__main__":
    with open('address.txt') as f:
        asyncio.run(connect(f.read().replace("\n", "")))
