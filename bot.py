import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import configparser
import asyncio
from enum import Enum

from timer import Timer
from timer import TimerStatus

DEBUG = True                                    # For debug messages
SETTING_OPTIONS = ['work_time', 'short_break_time', 'long_break_time', 'sessions', 'use_long_breaks']
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')              # Grabs Discord bot token from .env file
bot = commands.Bot(command_prefix='*')
timer = Timer()
pingList = []


# ------------ Overall Work List ---------
# TODO: Complete remaining commands
# TODO: Complete all error handling
# TODO: Store user-set times
# TODO: Override *help command to be fancier (see Octave bot)
# TODO: Add docstrings
# TODO: Create empty .env file before finalizing
# TODO: Remove all DEBUG statements and check imports before finalizing
# TODO: Allow bot to ping users once timer ends

# TODO: Update Enum with more colors
class MsgColors(Enum):
    AQUA = 0x33c6bb
    YELLOW = 0xFFD966
    RED = 0xEA3546


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord.')


@bot.command(name='start', help='Starts a Pomodoro timer for 25 minutes for work, 5 minutes for break')
async def start_timer(ctx):
    # TODO: Adjust help message to be more general
    # TODO: Add break functionality
    # TODO: Let *start also resume the timer if paused
    # TODO: Add proper msgs for error handling + correct
    if timer.get_status() == TimerStatus.STOPPED:
        work_mins = config['CURRENT_SETTINGS']['work_time']                 # Grabs work duration from user settings
        work_secs = '00'
        desc = f'Time Remaining: {work_mins}:{work_secs}'                   # Formats message to be sent

        em = discord.Embed(title='Starting Timer', description=desc, color=MsgColors.AQUA.value)
        await ctx.send(embed=em)
        if DEBUG:
            print('Command: *start (from stopped timer)')

        work_time = int(work_mins) * 60                                     # Multiplied by 60 to get seconds
        timer.start(work_time)
        while timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)                                          # Sleep for 1 sec before timer counts down
            timer.tick()
        if timer.get_status() == TimerStatus.STOPPED:                       # Ping users when timer stops
            for user in pingList:
                await ctx.send(f'Pinging {user}')
            pingList.clear()

    elif timer.get_status() == TimerStatus.PAUSED:
        work_secs = timer.get_time() % 60
        work_mins = int((timer.get_time() - work_secs) / 60)
        if work_secs < 10:                                                  # Formats seconds if <10 seconds left
            work_secs = '0' + str(work_secs)

        desc = f'Time Remaining: {work_mins}:{work_secs}'
        em = discord.Embed(title='Resuming Timer', description=desc, color=MsgColors.AQUA.value)
        await ctx.send(embed=em)
        if DEBUG:
            print('Command: *start (from paused timer)')

        timer.resume()
        while timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)
            timer.tick()
        if timer.get_status() == TimerStatus.STOPPED:                       # Ping users when timer stops
            for user in pingList:
                await ctx.send(f'Pinging {user}')
            pingList.clear()
    else:
        em = discord.Embed(title='Warning', description='Timer is already running.', color=MsgColors.YELLOW.value)
        await ctx.send(embed=em)
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
    if DEBUG:
        print('Command: *pause')
    if not timer.pause():
        em = discord.Embed(title='Warning', description='Timer has already been paused or stopped.', color=MsgColors.YELLOW.value)
    else:
        em = discord.Embed(title='Paused Timer', description='Timer has been paused.', color=MsgColors.AQUA.value)
    await ctx.send(embed=em)


@bot.command(name='stop', help='Stops the timer')
async def stop_timer(ctx):
    if DEBUG:
        print('Command: *stop')
    if not timer.stop():
        em = discord.Embed(title='Warning', description='Timer has already been stopped or paused.', color=MsgColors.YELLOW.value)
    else:
        em = discord.Embed(title='Stopped Timer', description='Timer has been stopped.', color=MsgColors.AQUA.value)
    await ctx.send(embed=em)


@bot.command(name='time', help='Displays the current timer status')
async def current_time(ctx):
    # TODO: Add in formatting for remaining time
    if DEBUG:
        print('Command: *time')

    # seconds = timer.get_time()
    # if seconds <= 0:
    #     seconds = '0'
    #     minutes = '00'
    # else:
    #     minutes = seconds
    #     seconds %= 60
    #     minutes

    status = timer.get_status()
    if status == TimerStatus.STOPPED:
        em = discord.Embed(title='Timer Stopped', description='Time Remaining: 0:00', color=MsgColors.RED.value)
    elif status == TimerStatus.RUNNING:
        em = discord.Embed(title='Timer Running', description=f'Time Remaining: ', color=MsgColors.AQUA.value)
    else:
        em = discord.Embed(title='Time Paused', description='Time Remaining: ', color=MsgColors.YELLOW.value)
    await ctx.send(embed=em)


@bot.command(name='notify', help='Signs up the user to be pinged when the timer ends')
async def notify_user(ctx):
    if DEBUG:
        print('Command: *notify')
    pingList.append(ctx.message.author.mention)


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
    x = ctx.message.author.mention
    await ctx.send(x)


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
