from discord.ext import commands
import discord
from database import init_db, insert_sentiment
from sentiment_analysis import analyze_sentiment, generate_sentiment_report
from role_commands import setup as setup_role_commands
import json
import sqlite3
from plotting import generate_sentiment_plot
import os


# Load configuration and set up the bot
with open('config.json') as config_file:
    config = json.load(config_file)
discord_token = config["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    init_db()

#@bot.event
#async def on_application_command_error(ctx, error):
#    await ctx.respond("You likely do not have the necessary permissions to use this command.", ephemeral=True)


def is_allowed():
    async def predicate(ctx):
        with sqlite3.connect('sentiments.db') as conn:
            c = conn.cursor()
            c.execute('SELECT role_id FROM allowed_roles WHERE guild_id = ?', (str(ctx.guild.id),))
            allowed_roles = [row[0] for row in c.fetchall()]

        user_roles = [str(role.id) for role in ctx.author.roles]
        return any(role in allowed_roles for role in user_roles)
    return commands.check(predicate)

# Bot setup and other command definitions follow here

@bot.slash_command(name='visual_sentiment_report_xdays', description="Visual report for 7 days")
async def sentiment_report(ctx, days: int):
    plot_filename = f'sentiment_{ctx.guild.id}_{days}days.png'
    success = generate_sentiment_plot(plot_filename, days, str(ctx.guild.id))
    if success:
        try:
            file = discord.File(plot_filename, filename=plot_filename)
            await ctx.respond(f"Here's the sentiment analysis for the last {days} days:", file=file)
        finally:
            os.remove(plot_filename)  # Delete the file after sending it
    else:
        await ctx.respond("No data available for the specified range.")



@bot.event
async def on_message(message):
    if message.author == bot.user or message.content.startswith(bot.command_prefix):
        return
    if not message.guild:  # Ignore private messages or messages outside of guilds
        return

    sentiment_result = analyze_sentiment(message.content)
    sentiment = 'positive' if sentiment_result['compound'] > 0.05 else 'negative' if sentiment_result['compound'] < -0.05 else 'neutral'
    insert_sentiment(str(message.guild.id), message.channel.name, sentiment)

    await bot.process_commands(message)

@bot.slash_command(name="server_report_7d", description="Generate a server-wide sentiment report for the past 7 days.")
@is_allowed()
async def server_report_7d(ctx):
    query = '''
        SELECT sentiment, COUNT(*) as cnt FROM sentiment_data
        WHERE guild_id = ? AND timestamp >= datetime('now', '-7 days')
        GROUP BY sentiment
    '''
    params = (str(ctx.guild.id),)
    report = generate_sentiment_report(ctx, query, params)
    await ctx.respond(report)

@bot.slash_command(name="channel_report", description="Generate a sentiment report for a specific channel.")
@is_allowed()
async def channel_report(ctx, channel: discord.TextChannel):
    query = '''
        SELECT sentiment, COUNT(*) as cnt FROM sentiment_data
        WHERE guild_id = ? AND channel_name = ? AND timestamp >= datetime('now', '-7 days')
        GROUP BY sentiment
    '''
    params = (str(ctx.guild.id), channel.name)
    ctx.channel = channel  # To include channel in the report
    report = generate_sentiment_report(ctx, query, params)
    await ctx.respond(report)

@bot.slash_command(name="server_custom_time_report", description="Generate a sentiment report for the specified number of past days.")
@is_allowed()
async def server_custom_time_report(ctx, days: int):
    query = '''
        SELECT sentiment, COUNT(*) as cnt FROM sentiment_data
        WHERE guild_id = ? AND timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY sentiment
    '''
    params = (str(ctx.guild.id), days)
    ctx.days = days  # To include time frame in the report
    report = generate_sentiment_report(ctx, query, params)
    await ctx.respond(report)

@bot.slash_command(name="channel_custom_time_report", description="Generate a sentiment report for a specified channel over a specified number of days.")
@is_allowed()
async def channel_custom_time_report(ctx, channel: discord.TextChannel, days: int):
    query = '''
        SELECT sentiment, COUNT(*) as cnt FROM sentiment_data
        WHERE guild_id = ? AND channel_name = ? AND timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY sentiment
    '''
    params = (str(ctx.guild.id), channel.name, days)
    ctx.channel = channel  # To include channel in the report
    ctx.days = days  # To include time frame in the report
    report = generate_sentiment_report(ctx, query, params)
    await ctx.respond(report)

setup_role_commands(bot)
bot.run(discord_token)
