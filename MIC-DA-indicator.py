import asyncio
import json
import socketio
import pyfirmata
import time
import discord

intents = discord.Intents.all()
intents.voice_states = True
from discord.ext import commands
from discord.ext.commands import Bot

client = Bot(command_prefix="!")
global counter
counter = 0

board = pyfirmata.Arduino('COM13')
TOKEN = 'YOUR Donation Alerts Token'
TOKEN_bot = 'YOUR Discord Bot Token'
bot = commands.Bot(command_prefix='!')
sio = socketio.Client()


@bot.event
async def on_ready():
	print('Logged in...')


@bot.event
async def on_voice_state_update(self, before, after):
	global counter
	channel = 'your channel id in discord where microphone state monitored'
	if self.id == 'your user id in discord' and after.self_mute == True:
		counter = 0
		board.digital[2].write(0)
		time.sleep(1)
		mystring = f'MIC t={counter}'
		print(mystring)
		board.digital[2].write(1)
		print("MIC MUTE")

	if self.id == 'your user id in discord' and after.self_mute == False:
		board.digital[2].write(0)
		counter = 0
		mystring = f'MIC t={counter}'
		print(mystring)
		print("MIC UNMUTE")
	return (counter)

@sio.on('connect')
def on_connect():
	sio.emit('add-user', {"token": TOKEN, "type": "alert_widget"})


@sio.on('donation')
def on_message(data):
	global counter
	y = json.loads(data)
	# text = "New donate from: " + (y['username']), (y['amount']), (y['currency'])
	text = "New alert about " + (y['username'])
	channel = 'your channel id in discord where alerts are published'
	asyncio.run_coroutine_threadsafe(send_msg(channel, text), bot.loop)
	counter = 1
	mystring = f'Alert t={counter}'
	# while True:
	# 	print(mystring)
	# 	time.sleep(5)
	while counter == 1:
		board.digital[2].write(1)
		mystring = f'led on'
		print(mystring)
		time.sleep(1)
		board.digital[2].write(0)
		mystring = f'led off'
		print(mystring)
		mystring = f'Alert t={counter}'
		print(mystring)
		time.sleep(1)



async def send_msg(channel, text):
	channel = bot.get_channel(channel)
	await channel.send(text)



print("Что, кожанный мешок, Бота запустил, Бабок ждешь.... ну ну.... ну давай подождем.... ")
sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
bot.run(TOKEN_bot)
