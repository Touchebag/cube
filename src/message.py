from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

from Cryptodome.Cipher import AES

from tkinter import StringVar

import global_state
from cubestate import CubeState

AES_KEY = bytearray([87, 177, 249, 171, 205, 90, 232, 167, 156, 185, 140, 231, 87, 140, 81, 8])
CHARACTERISTIC = "fff6"

class CubeComm:
    device = None
    client: BleakClient = None
    address = None
    connection_status = None
    handshake_done = False

    def __init__(self, connection_status):
        self.connection_status = connection_status
        self.connection_status.set("Not connected")

    def __exit__(self, exc_type, exc_value, traceback):
        if client is not None:
            print("Closing connection")
            asyncio.run(client.disconnect())

    async def scan_and_connect(self):
        self.connection_status.set("Scanning")
        devices = await self.scan_for_devices()

        for d in devices.values():
            name = d[0].name
            if name is not None and "QY-QYSC" in name:
                await self.connect(d[0].address)
                return

        print("No devices found")
        self.connection_status.set("Not connected")

    async def connect(self, address):
        print(f"Connecting to device {address}")

        self.connection_status.set("Connecting")
        self.address = address
        self.device = await BleakScanner.find_device_by_address(address)
        self.client = BleakClient(self.device)
        await self.client.connect()

        self.handshake_done = False
        await self.setup_notifications()
        await self.send_hello()

        self.connection_status.set("Connected")
        print("Connected")

    async def scan_for_devices(self):
        print("Scanning...")

        devices = await BleakScanner.discover(return_adv=True)

        return devices

    def encrypt(self, data):
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        return cipher.encrypt(data)

    def decrypt(self, data):
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        return cipher.decrypt(data)

    def calculate_crc(self, data):
        crc = 0xFFFF
        for i in range(len(data)):
            crc ^= data[i]
            for j in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1

        return crc.to_bytes(2, byteorder="little")

    def pad(self, data):
        data += [0x00] * (16 - (len(data) % 16))

        return data

    async def notification_callback(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        decrypted_data = self.decrypt(data)
        print("Recieved message")
        print(decrypted_data.hex(" "))

        if decrypted_data[2] != 0x04:
            print("Acking")
            await self.send_ack(decrypted_data)

        if len(decrypted_data) > 35:
            global_state.main_window.set_battery_level(decrypted_data[35])

        if not self.handshake_done:
            print("Sending sync")
            self.handshake_done = True
            # Only send on first try
            await self.send_state_sync(CubeState())
        else:
            if decrypted_data[2] == 0x03 or decrypted_data[2] == 0x04:
                state = CubeState()

                if len(decrypted_data) > 91 and decrypted_data[91] != 1:
                    # If needs ack then we should ignore response state and assume solved
                    state.decode(decrypted_data[7:34])

                global_state.main_window.new_cube_state(state)


    async def setup_notifications(self):
        await self.client.start_notify(CHARACTERISTIC, self.notification_callback)

    async def write_data(self, data):
        print("Sending message")
        print(data.hex(" "))
        encrypted_data = self.encrypt(data)

        await self.client.write_gatt_char(CHARACTERISTIC, encrypted_data)

    async def send_state_sync(self, state: CubeState):
        data = [0xfe, 0x26]
        data += [0x04, 0x17, 0x88, 0x8b, 0x31]
        data += state.encode()
        data += [0x00, 0x00]
        data += self.calculate_crc(data)

        data = self.pad(data)

        await self.write_data(bytearray(data))

    async def send_ack(self, message):
        data = [0xfe, 0x09]
        data += message[2:7]
        data += self.calculate_crc(data)

        data = self.pad(data)

        await self.write_data(bytearray(data))

    async def send_hello(self):
        data = [0xfe, 0x15]
        data += [00,00,00,00,00,00,00,00,00,00,00]
        for i in reversed(self.address.split(sep=":")):
            data += [int(f"0x{i}", 16)]
        data += self.calculate_crc(data)

        data = self.pad(data)

        await self.write_data(bytearray(data))
