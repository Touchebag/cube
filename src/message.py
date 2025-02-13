from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from Cryptodome.Cipher import AES

AES_KEY = bytearray([87, 177, 249, 171, 205, 90, 232, 167, 156, 185, 140, 231, 87, 140, 81, 8])
CHARACTERISTIC = "fff6"

class CubeComm:
    client : BleakClient

    def set_client(self, client):
        self.client = client

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

        await self.send_ack(decrypted_data)

    async def setup_notifications(self):
        await self.client.start_notify(CHARACTERISTIC, self.notification_callback)

    async def write_data(self, data):
        print("Sending message")
        print(data.hex(" "))
        encrypted_data = self.encrypt(data)

        await self.client.write_gatt_char(CHARACTERISTIC, encrypted_data)

    async def send_ack(self, message):
        data = [0xfe, 0x09]
        data += message[2:7]
        data += self.calculate_crc(data)

        data = self.pad(data)

        await self.write_data(bytearray(data))

    async def send_hello(self, address):
        data = [0xfe, 0x15]
        data += [00,00,00,00,00,00,00,00,00,00,00]
        for i in reversed(address.split(sep=":")):
            data += [int(f"0x{i}", 16)]
        data += self.calculate_crc(data)

        data = self.pad(data)

        await self.write_data(bytearray(data))
