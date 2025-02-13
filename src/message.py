from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from Cryptodome.Cipher import AES

AES_KEY = bytearray([87, 177, 249, 171, 205, 90, 232, 167, 156, 185, 140, 231, 87, 140, 81, 8])
CHARACTERISTIC = "fff6"

def encrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.encrypt(data)

def decrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.decrypt(data)

def calculate_crc(data):
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

def notification_callback(characteristic: BleakGATTCharacteristic, data: bytearray):
    decrypted_data = decrypt(data)
    print(decrypted_data)

async def setup_notifications(client):
    await client.start_notify(CHARACTERISTIC, notification_callback)

async def write_data(client, data):
    encrypted_data = encrypt(data)

    await client.write_gatt_char(CHARACTERISTIC, encrypted_data)

async def send_hello(client, address):
    data = [0xfe, 0x15]
    data += [00,00,00,00,00,00,00,00,00,00,00]
    for i in reversed(address.split(sep=":")):
        data += [int(f"0x{i}", 16)]
    data += calculate_crc(data)
    data += [0,0,0,0,0,0,0,0,0,0,0]

    await write_data(client, bytearray(data))
