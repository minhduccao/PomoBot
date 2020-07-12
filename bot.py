import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

DEBUG = True                                    # For debug messages
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')              # Grabs Discord bot token from .env file
bot = commands.Bot(command_prefix='*')

# ------------ Overall Work List ---------
# TODO: Complete remaining commands
# TODO: Complete all error handling
# TODO: Store user-set times
# TODO: Override *help command to be fancier (see Octave bot)
# TODO: Add docstrings
# TODO: Create logo for repo and bot icon
# TODO: Create empty .env file before finalizing
# TODO: Remove all DEBUG statements and check imports before finalizing


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord.')


@bot.command(name='start', help='Starts a Pomodoro timer for 25 minutes for work, 5 minutes for break')
async def start_timer(ctx):
    # TODO: Add default to timer and call from user-set timing
    # TODO: Adjust help message to be more general
    # TODO: Start a bot timer with some trigger at the end of the timer
    # TODO: Add a 'long break' functionality later
    if DEBUG:
        await ctx.send('Starting timer')
        print('Command: *start')


@bot.command(name='settimer', help='Customizes the work/break amounts for the timer')
async def set_timer_amt(ctx, work_time: int, break_time: int):
    # TODO: Store user-specified times
    # TODO: Change to accept default values
    # TODO: Change input params to work with short and long break inputs
    if DEBUG:
        await ctx.send(f'Work: {work_time} Break: {break_time}')
        print(f'Command: *settimer: Work Time: {work_time} Break Time: {break_time}')


@bot.command(name='stop', help='Stops the timer')
async def stop_timer(ctx):
    # TODO: Stop the current timer
    # TODO: Handle if timer is already stopped or hasn't started yet
    if DEBUG:
        await ctx.send('Stopped timer')
        print(f'Command: *stop')


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

bot.run(TOKEN)
