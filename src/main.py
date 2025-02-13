#!/usr/bin/env python3

from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

import asyncio

import time

from Cryptodome.Cipher import AES

AES_KEY = bytearray([87, 177, 249, 171, 205, 90, 232, 167, 156, 185, 140, 231, 87, 140, 81, 8])
CHARACTERISTIC = "fff6"

MAC_ADDRESS = None

def encrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.encrypt(data)

def decrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.decrypt(data)

async def write_data(client, data):
    encrypted_data = encrypt(data)

    await client.write_gatt_char(CHARACTERISTIC, encrypted_data)

def notification_callback(characteristic: BleakGATTCharacteristic, data: bytearray):
    decrypted_data = decrypt(data)
    print(decrypted_data)

async def main_loop(client):
    await client.start_notify(CHARACTERISTIC, notification_callback)

    data = [0xfe, 0x15]
    data += [00,00,00,00,00,00,00,00,00,00,00]
    for i in reversed(MAC_ADDRESS.split(sep=":")):
        data += [int(f"0x{i}", 16)]
    data += [0x50, 0xb4]
    data += [0,0,0,0,0,0,0,0,0,0,0]

    print("Sending hello")
    await write_data(client, bytearray(data))

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
