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
SETTING_OPTIONS = ['work_time', 'short_break_time', 'long_break_time', 'sessions', 'use_long_breaks', 'keep_pings']
COMMAND_PREFIX = '*'
TIMER_COMMANDS = ['start', 'pause', 'stop', 'time', 'notify', 'set', 'setextra', 'togglebreak']
GENERAL_COMMANDS = ['reset', 'help']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')              # Grabs Discord bot token from .env file
bot = commands.Bot(command_prefix=COMMAND_PREFIX, help_command=None)
timer = Timer()


# ------------ Overall Work List ---------
# TODO: Complete all error handling
# TODO: Store user-set times
# TODO: Add break functionality + settings to adjust long breaks, sessions
# TODO: Add docstrings
# TODO: Create empty .env file before finalizing
# TODO: Add settings.ini file before finalizing
# TODO: Add empty pings.txt file before finalizing
# TODO: Remove all DEBUG statements and check imports before finalizing

# TODO: Update Enum with more colors
class MsgColors(Enum):
    AQUA = 0x33c6bb
    YELLOW = 0xFFD966
    RED = 0xEA3546
    PURPLE = 0x6040b1


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord.')


@bot.command(name='start', help='Starts/resumes a Pomodoro timer', aliases=['resume'])
async def start_timer(ctx):
    if timer.get_status() == TimerStatus.STOPPED:
        work_mins = config['CURRENT_SETTINGS']['work_time']                 # Grabs work duration from user settings
        work_secs = '00'
        desc = f'Time Remaining: `{work_mins}:{work_secs}`'                 # Formats message to be sent

        em = discord.Embed(title=':timer: Starting Timer',
                           description=desc,
                           color=MsgColors.AQUA.value)
        await ctx.send(embed=em)
        if DEBUG:
            print('Command: *start (from stopped timer)')

        work_time = int(work_mins) * 60                                     # Multiplied by 60 to get seconds
        timer.start(work_time)
        while timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)                                          # Sleep for 1 sec before timer counts down
            timer.tick()
        if timer.get_status() == TimerStatus.STOPPED:                       # Ping users when timer stops
            with open('pings.txt', 'r') as pingFile:
                pingList = [user for user in pingFile]

                for user in pingList:
                    await ctx.send(f'Pinging {user}')
            if not config['CURRENT_SETTINGS']['keep_pings']:                # Erase ping list if not keeping users
                open('pings.txt', 'w').close()

    elif timer.get_status() == TimerStatus.PAUSED:                          # Resuming timer from paused state
        em = discord.Embed(title=':timer: Resuming Timer',
                           description=getFrmtTime(timer),
                           color=MsgColors.AQUA.value)
        await ctx.send(embed=em)
        if DEBUG:
            print('Command: *start (from paused timer)')

        timer.resume()
        while timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)
            timer.tick()
        if timer.get_status() == TimerStatus.STOPPED:                       # Ping users when timer stops
            with open('pings.txt', 'r') as pingFile:
                for user in pingFile:
                    await ctx.send(f'Pinging {user}')
            if not config['CURRENT_SETTINGS']['keep_pings']:                # Erase ping list if not keeping users
                open('pings.txt', 'w').close()
    else:
        em = discord.Embed(title=':warning: Warning',
                           description='Timer is already running.',
                           color=MsgColors.YELLOW.value)
        await ctx.send(embed=em)


@bot.command(name='pause', help='Pauses the timer')
async def pause_timer(ctx):
    if not timer.pause():
        em = discord.Embed(title=':warning: Warning',
                           description='Timer has already been paused or stopped.',
                           color=MsgColors.YELLOW.value)
    else:
        em = discord.Embed(title=':pause_button: Paused Timer',
                           description='Timer has been paused.\n'+getFrmtTime(timer),
                           color=MsgColors.AQUA.value)
    await ctx.send(embed=em)


@bot.command(name='stop', help='Stops the timer')
async def stop_timer(ctx):
    if not timer.stop():
        em = discord.Embed(title=':warning: Warning',
                           description='Timer has already been stopped or paused.',
                           color=MsgColors.YELLOW.value)
    else:
        em = discord.Embed(title=':stop_button: Stopped Timer',
                           description='Timer has been stopped.',
                           color=MsgColors.RED.value)
    await ctx.send(embed=em)


@bot.command(name='time', help='Displays the current timer status', aliases=['timer', 'status'])
async def current_time(ctx):
    status = timer.get_status()
    if status == TimerStatus.STOPPED:
        em = discord.Embed(title=':stop_button: Timer Stopped',
                           description='Time Remaining: 0:00',
                           color=MsgColors.RED.value)
    elif status == TimerStatus.RUNNING:
        em = discord.Embed(title=':timer: Timer Running',
                           description=getFrmtTime(timer),
                           color=MsgColors.AQUA.value)
    else:
        em = discord.Embed(title=':pause_button: Timer Paused',
                           description=getFrmtTime(timer),
                           color=MsgColors.YELLOW.value)
    await ctx.send(embed=em)


@bot.command(name='notify', help='Signs up the user to be pinged when the timer ends')
async def notify_user(ctx):
    em = discord.Embed(title=':ballot_box_with_check: Notification Confirmed',
                       description='Timer will ping ' + ctx.message.author.name + ' when the timer stops.',
                       color=MsgColors.AQUA.value)
    newUser = ctx.message.author.mention
    with open('pings.txt', 'r+') as pingFile:
        pingList = [user for user in pingFile]                              # Populates list of users to be pinged
        print(pingList)
        if newUser not in pingList:                                            # Adds user if not already added
            pingFile.write(ctx.message.author.mention + '\n')
    await ctx.send(embed=em)


@bot.command(name='set', help='Sets duration for work and short breaks')
async def set_options_simple(ctx, work_time: int, short_break_time: int):
    config.set('CURRENT_SETTINGS', 'work_time', str(work_time))
    config.set('CURRENT_SETTINGS', 'short_break_time', str(short_break_time))
    with open('settings.ini', 'w') as configFile:
        config.write(configFile)

    em = discord.Embed(title=':gear: Adjusting Timer Settings',
                       description=f'Setting work time to {work_time} minutes and break time to {short_break_time} minutes',
                       color=MsgColors.AQUA.value)
    await ctx.send(embed=em)

    if DEBUG:
        print(f'Command: *set: Work Time: {work_time} Break Time: {short_break_time}')


@bot.command(name='setextra', help='Sets duration for long breaks and number of work sessions')
async def set_options_extra(ctx, long_break_time: int, sessions: int):
    config.set('CURRENT_SETTINGS', 'long_break_time', str(long_break_time))
    config.set('CURRENT_SETTINGS', 'sessions', str(sessions))
    with open('settings.ini', 'w') as configFile:
        config.write(configFile)

    em = discord.Embed(title=':gear: Adjusting Timer Settings',
                       description=f'Setting long break time to {long_break_time} minutes and number of work sessions to {sessions}.',
                       color=MsgColors.AQUA.value)
    await ctx.send(embed=em)


@bot.command(name='togglebreak', help='Toggles the option to enable/disable long breaks')
async def toggle_long_break(ctx):
    break_option = config['CURRENT_SETTINGS']['use_long_breaks'] == 'True'
    config.set('CURRENT_SETTINGS', 'use_long_breaks', str(not break_option))
    with open('settings.ini', 'w') as configFile:
        config.write(configFile)

    if break_option:
        desc = 'Disabled long breaks.'
    else:
        desc = 'Enabled long breaks.'
    em = discord.Embed(title=':gear: Adjusting Timer Settings',
                       description=desc,
                       color=MsgColors.AQUA.value)
    await ctx.send(embed=em)


@bot.command(name='reset', help='Reset timer settings to default values.')
async def reset_settings(ctx):
    for option in SETTING_OPTIONS:
        config.set('CURRENT_SETTINGS', option, config['DEFAULT'][option])
    with open('settings.ini', 'w') as configFile:
        config.write(configFile)
    em = discord.Embed(title=':leftwards_arrow_with_hook: Reset Timer Settings',
                       description='Timer settings have been reset to default values.',
                       color=MsgColors.AQUA.value)
    await ctx.send(embed=em)


@bot.command(name='help', help='Describes all bot commands.')
async def help(ctx):
    help_commands = dict()                                              # Dict of help commands + their description
    for command in bot.commands:
        help_commands[command.name] = command.help

    desc = 'The prefix for this bot is `' + COMMAND_PREFIX + '`\n'      # Prints ordered list of timer commands
    desc += f'\n**Timer Commands | {len(TIMER_COMMANDS)}**\n'
    for command in TIMER_COMMANDS:
        desc += '`{:12s}` {}\n'.format(command, help_commands[command])

    desc += f'\n**General Commands | {len(GENERAL_COMMANDS)}**\n'       # Prints ordered list of general commands
    for command in GENERAL_COMMANDS:
        desc += '`{:12s}` {}\n'.format(command, help_commands[command])

    em = discord.Embed(title='Bot Commands',
                       description=desc,
                       color=MsgColors.PURPLE.value)
    await ctx.send(embed=em)


# TODO: Remove command later
@bot.command(name='t', help='Temporary for testing commands')
async def t(ctx):
    with open('pings.txt', 'r') as pingFile:
        for line in pingFile:
            await ctx.send(line)

# ----------------------- ERROR HANDLING -----------------------------
# TODO: Fill in remaining method errors
@set_options_simple.error
async def set_options_simple_error(ctx, error):
    if DEBUG:
        print(f'*set error: {ctx.message.content} \n{ctx.message}\n')
    if isinstance(error, commands.errors.MissingRequiredArgument):
        em = discord.Embed(title=':warning: Invalid *set Command Usage',
                           description='Specify both a valid work and break time.\nFormat: `*set # #`',
                           color=MsgColors.YELLOW.value)
    elif isinstance(error, commands.errors.BadArgument):
        em = discord.Embed(title=':warning: Invalid *set Command Usage',
                           description='Specify whole numbers for both work and break times. \nFormat: `*set # #`',
                           color=MsgColors.YELLOW.value)
    else:
        em = discord.Embed(title=':x: Invalid *set Command Usage Error',
                           description=f'Unhandled *set error has been logged.',
                           color=MsgColors.RED.value)
        with open('error.log', 'a') as errorLog:
            errorLog.write(f'Unhandled *set message: {ctx.message.content} \n{ctx.message}\n')
    await ctx.send(embed=em)


# ----------------------- UTILITY FUNCTIONS -----------------------------
def getFrmtTime(clock: Timer):
    work_secs = clock.get_time() % 60
    work_mins = int((clock.get_time() - work_secs) / 60)
    if work_secs < 10:  # Formats seconds if <10 seconds left
        work_secs = '0' + str(work_secs)

    return f'Time Remaining: `{work_mins}:{work_secs}`'


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')                 # Read in settings from settings.ini
    bot.run(TOKEN)
