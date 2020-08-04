import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import configparser
import asyncio

from timer import Timer
from timer import TimerStatus

DEBUG = True                                    # For debug messages
SETTING_OPTIONS = ['work_time', 'short_break_time', 'long_break_time', 'sessions', 'use_long_breaks']
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')              # Grabs Discord bot token from .env file
bot = commands.Bot(command_prefix='*')
timer = Timer()
workTimeLeft = 0
breakTimeLeft = 0


# ------------ Overall Work List ---------
# TODO: Complete remaining commands
# TODO: Complete all error handling
# TODO: Store user-set times
# TODO: Override *help command to be fancier (see Octave bot)
# TODO: Add docstrings
# TODO: Create empty .env file before finalizing
# TODO: Remove all DEBUG statements and check imports before finalizing


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord.')


@bot.command(name='start', help='Starts a Pomodoro timer for 25 minutes for work, 5 minutes for break')
async def start_timer(ctx):
    # TODO: Adjust help message to be more general
    # TODO: Add break functionality
    # TODO: Let *start also resume the timer if paused
    # TODO: Add proper msgs for error handling + correct
    if DEBUG:
        em = discord.Embed(title='Starting Timer', description='Starting timer', color=0x00FF00)
        msg = await ctx.send('Starting timer')
        await msg.edit(embed=em)
        print('Command: *start')

    if timer.get_status() == TimerStatus.STOPPED:
        work_time = int(config['CURRENT_SETTINGS']['work_time']) * 60
        timer.start(work_time)

        while timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)
            timer.tick()
    else:
        em = discord.Embed(title='Warning', description='Timer is already running.', color=0x00FF00)
        msg = await ctx.send('Timer is already running')
        await msg.edit(embed=em)
        if DEBUG:
            print('Timer already exists.')


@bot.command(name='set', help='Customizes the work/break amounts for the timer')
async def set_timer_amt(ctx, work_time: int, break_time: int):
    # TODO: Store user-specified times
    # TODO: Change to accept default values
    # TODO: Change input params to work with short and long break inputs
    if DEBUG:
        await ctx.send(f'Work: {work_time} Break: {break_time}')
        print(f'Command: *set: Work Time: {work_time} Break Time: {break_time}')


@bot.command(name='pause', help='Pauses the timer')
async def pause_timer(ctx):
    # TODO: Handle if timer is already paused or stopped already
    if DEBUG:
        await ctx.send('Paused timer')
        print('Command: *pause')
    if not timer.pause():
        # Handle error here
        pass


@bot.command(name='stop', help='Stops the timer')
async def stop_timer(ctx):
    # TODO: Handle if timer is already stopped or hasn't started yet
    if DEBUG:
        await ctx.send('Stopped timer')
        print(f'Command: *stop')
    if not timer.stop():
        # Handle error here
        pass


@bot.command(name='reset', help='Reset timer settings to default values.')
async def reset_settings(ctx):
    for option in SETTING_OPTIONS:
        config.set('CURRENT_SETTINGS', option, config['DEFAULT'][option])
    with open('settings.ini', 'w') as configFile:
        config.write(configFile)
    await ctx.send('Finished resetting timer settings to default values.')


# TODO: Remove command later
@bot.command(name='t', help='Temporary for testing commands')
async def t(ctx):
    em = discord.Embed(title='Error', description='Desc', color=0x00FF00)
    msg = await ctx.send()
    await msg.edit(embed=em)


# ----------------------- ERROR HANDLING -----------------------------
# TODO: Fill in remaining method errors
@set_timer_amt.error
async def set_timer_amt_error(ctx, error):
    if DEBUG:
        print(f'*timer error: {ctx.message.content} \n{ctx.message}\n')
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Specify both a valid work and break time. \nFormat: `*settimer # #`')
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send('Specify whole numbers for both work and break times. \nFormat: `*settimer # #`')
    else:
        with open('error.log', 'a') as errorLog:
            errorLog.write(f'Unhandled *settimer message: {ctx.message.content} \n{ctx.message}\n')


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')                 # Read in settings from settings.ini
    bot.run(TOKEN)
