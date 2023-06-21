import socket
import json
import time
import struct
import discord
from discord.ext import commands, tasks
import time
import asyncio

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# EDIT THIS INFO
SERVER_IP = "127.0.0.1"
SERVER_PORT = 25566
TOKEN = "TOKEN"
# -------------

def write_varint(data):
    ordinal = b''
    while True:
        byte = data & 0x7F
        data >>= 7
        ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))
        if data == 0:
            break
    return ordinal

def read_varint(sock):
    data = 0
    for i in range(5):
        ordinal = sock.recv(1)
        if len(ordinal) == 0:
            break
        byte = ord(ordinal)
        data |= (byte & 0x7F) << 7 * i
        if not byte & 0x80:
            break
    return data

@bot.event
async def on_ready():
    print('Bot is ready')
    update_status.start()

@tasks.loop(seconds=10)
async def update_status():
    handshake = b'\x00\x00\t127.0.0.1\xddc\x01'
    nullb = b'\x00'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(7)
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.send(write_varint(len(handshake)) + handshake)
        sock.send(write_varint(len(nullb)) + nullb)
        packet_length = read_varint(sock)
        packet_id = read_varint(sock)
        byte = b''
        if packet_id > packet_length:
            read_varint(sock)
        extra_length = read_varint(sock)
        while len(byte) < extra_length:
            byte += sock.recv(extra_length)
        response = json.loads(byte.decode('utf8'))
        online = response["players"]["online"]
        max = response["players"]["max"]
        status = f'{online}/{max} Players'
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Game(name="Play.YourServer.iR"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Server Online"))
        await asyncio.sleep(10)
    except:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Server Offline"))

bot.run(TOKEN)
